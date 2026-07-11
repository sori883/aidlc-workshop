#!/usr/bin/env bash
# A領域: 品質の機械検査（AI採点なし。すべてツールによる決定的測定）
# 使い方: ./03_quality_A.sh [green-field|brown-field]   （既定: brown-field）
# 入力  : results/<対象>/A_sessions.tsv（01が生成。コミット境界を含む）
# 出力  : results/<対象>/A_品質_<キー>.json（既存はスキップ）
#
# 検査内容（既に完了した開発の成果物に対する事後検査）:
#   tests            … 現在の成果物でのテスト結果（passed/failed。既存テスト含む全件）
#   coverage_changed … 生成コード（base..headで変更・追加された app/ 配下）の行カバレッジ
#   static           … ruff / bandit の所見数（headとbaseの差分＝生成コードが持ち込んだ所見）
#   pip_audit        … 依存脆弱性件数（SKIP_PIP_AUDIT=1 で省略。ネットワーク必要）
#   churn            … base..head の総変更行数（生成コードの規模。ドキュメント類は除外）
#   extensions       … aidlc-state.md のextension opt-in状態とPBTの痕跡（D5の記述的検査）
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"

command -v "$UVX" >/dev/null || { echo "ERROR: uvx がありません（brew install uv）" >&2; exit 1; }
MANIFEST="$RESULTS/A_sessions.tsv"
[ -s "$MANIFEST" ] || { echo "ERROR: 先に ./01_setup_A.sh $TARGET_FIELD を実行してください" >&2; exit 1; }

ensure_venv() { # $1=requirements.txtのあるdir
  if [ ! -x "$QUALITY_VENV/bin/python" ]; then
    echo "venv作成: $QUALITY_VENV"
    if command -v uv >/dev/null; then uv venv -q "$QUALITY_VENV"; else python3 -m venv "$QUALITY_VENV"; fi
  fi
  if command -v uv >/dev/null; then
    VIRTUAL_ENV="$QUALITY_VENV" uv pip install -q -r "$1/requirements.txt" pytest-cov
  else
    "$QUALITY_VENV/bin/pip" install -q -r "$1/requirements.txt" pytest-cov
  fi
}

# 注: ruffは存在しないパスを指定するとE902を「所見1件」として返すため、app/の存在を先に確認する
count_ruff()   { [ -d "$1/app" ] || { echo 0; return; }
  (cd "$1" && "$UVX" -q ruff check app --output-format json --exit-zero 2>/dev/null || echo "[]") | python3 -c "import json,sys
try: print(len(json.load(sys.stdin)))
except Exception: print(0)"; }
count_bandit() { [ -d "$1/app" ] || { echo 0; return; }
  (cd "$1" && "$UVX" -q bandit -r app -f json -q 2>/dev/null || true) | python3 -c "import json,sys
try: print(len(json.load(sys.stdin).get('results', [])))
except Exception: print(0)"; }

# manifestは1対象=1行
IFS=$'\t' read -r key _jsonl base head prefix < <(tail -n +2 "$MANIFEST" | head -1)
out="$RESULTS/A_品質_${key}.json"
if [ -s "$out" ]; then
  echo "skip: ${out}（既存）"
else
  echo "=== 品質検査: ${key}（$base..${head}） ==="

  # 検査は head コミットの worktree に対して行う。
  # 現ディレクトリは開発完了後に改変されている可能性があるため、成果物そのもの（headの状態）を検査する
  tmph="$(mktemp -d "${TMPDIR:-/tmp}/aidlc-h-XXXXXX")"
  git -C "$REPO_ROOT" worktree add -q "$tmph/w" "$head"
  HEAD_DIR="$tmph/w/${prefix%/}"; [ -d "$HEAD_DIR" ] || HEAD_DIR="$tmph/w"
  ensure_venv "$HEAD_DIR"

  # 1) 成果物（head時点）のテスト + カバレッジ
  test_out="$(cd "$HEAD_DIR" && "$QUALITY_VENV/bin/python" -m pytest -q --cov=app --cov-report=json:coverage.json 2>&1 | tail -5)" || true
  read -r passed failed <<<"$(python3 - "$test_out" <<'EOF'
import re, sys
out = sys.argv[1]
p = re.search(r"(\d+) passed", out); f = re.search(r"(\d+) failed", out); e = re.search(r"(\d+) error", out)
if p or f or e:
    print((int(p.group(1)) if p else 0), (int(f.group(1)) if f else 0) + (int(e.group(1)) if e else 0))
else:
    print(-1, -1)
EOF
)"

  # 生成コード = base..head で変更・追加された app/ 配下（コミット内パスから接頭辞を剥がす）
  changed_files="$(git -C "$REPO_ROOT" diff --name-only "$base" "$head" -- "${prefix}app" | grep '\.py$' | sed "s|^${prefix}||" || true)"
  cov_changed="$(python3 - "$HEAD_DIR/coverage.json" <<EOF
import json, sys
try:
    cov = json.load(open(sys.argv[1]))
except Exception:
    print(-1); raise SystemExit
files = """$changed_files""".split()
tot = hit = 0
for f, d in cov.get("files", {}).items():
    if f in files:
        s = d["summary"]
        tot += s["num_statements"]; hit += s["covered_lines"]
print(round(100 * hit / tot, 1) if tot else -1)
EOF
)"
  # 2) 静的解析: head時点 と base時点 の所見数
  ruff_head="$(count_ruff "$HEAD_DIR")"; bandit_head="$(count_bandit "$HEAD_DIR")"
  tmpb="$(mktemp -d "${TMPDIR:-/tmp}/aidlc-b-XXXXXX")"
  git -C "$REPO_ROOT" worktree add -q "$tmpb/w" "$base"
  base_dir="$tmpb/w/${prefix%/}"; [ -d "$base_dir" ] || base_dir="$tmpb/w"
  ruff_base="$(count_ruff "$base_dir")"; bandit_base="$(count_bandit "$base_dir")"
  git -C "$REPO_ROOT" worktree remove --force "$tmpb/w"; command rm -rf "$tmpb"

  # 3) 依存脆弱性
  audit_count=-1
  if [ "${SKIP_PIP_AUDIT:-0}" != "1" ]; then
    audit_count="$( (cd "$HEAD_DIR" && "$UVX" -q pip-audit -r requirements.txt -f json 2>/dev/null || echo '{}') | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(sum(len(dep.get('vulns', [])) for dep in d.get('dependencies', [])))
except Exception:
    print(-1)")" || audit_count=-1
  fi

  # 4) churn（生成コードの規模。ドキュメント・足場を除外）
  churn_total="$(git -C "$REPO_ROOT" diff --shortstat "$base" "$head" -- "${prefix:-.}" "${A_DIFF_EXCLUDES[@]}" | python3 -c "import re,sys; s=sys.stdin.read(); m=re.findall(r'(\d+) (?:insertion|deletion)', s); print(sum(map(int, m)) if m else 0)")"

  # 5) extensions（D5の記述的検査）: aidlc-state.md のopt-in表とPBTの痕跡（head時点）
  ext_json="$(python3 - "$HEAD_DIR" <<'EOF'
import json, re, sys
from pathlib import Path
root = Path(sys.argv[1])
exts = {}
state = root / "aidlc-docs" / "aidlc-state.md"
if state.exists():
    in_table = False
    for line in state.read_text(encoding="utf-8").splitlines():
        if "Extension" in line and "Enabled" in line:
            in_table = True
            continue
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line) if in_table else None
        if m and not set(m.group(1)) <= {"-", " "}:
            exts[m.group(1)] = m.group(2)
        elif in_table and not line.strip().startswith("|"):
            in_table = False
pbt_files = [str(p.relative_to(root)) for p in root.glob("tests/*pbt*.py")]
pbt_files += [str(p.relative_to(root)) for p in root.glob("tests/*.py")
              if "hypothesis" in p.read_text(encoding="utf-8", errors="ignore") and str(p.relative_to(root)) not in pbt_files]
print(json.dumps({"opt_in": exts, "pbt_test_files": sorted(set(pbt_files))}, ensure_ascii=False))
EOF
)"

  python3 - <<EOF
import json
data = {
    "key": "$key",
    "commit_range": "$base..$head",
    "tests": {"passed": $passed, "failed": $failed},
    "coverage_changed_files_pct": $cov_changed,
    "changed_app_files": """$changed_files""".split(),
    "static": {"ruff_head": $ruff_head, "ruff_baseline": $ruff_base, "ruff_delta": $ruff_head - $ruff_base,
                "bandit_head": $bandit_head, "bandit_baseline": $bandit_base, "bandit_delta": $bandit_head - $bandit_base},
    "pip_audit_vulns": $audit_count,
    "churn_total_lines": $churn_total,
    "extensions": $ext_json,
}
open("$out", "w").write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(data, ensure_ascii=False, indent=2))
EOF
  git -C "$REPO_ROOT" worktree remove --force "$tmph/w"; command rm -rf "$tmph"
  echo "-> $out"
fi
echo "品質検査完了。次: ./04_grade_A.sh $TARGET_FIELD"
