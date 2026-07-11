#!/usr/bin/env bash
# A領域（開発効率・品質）: 検査対象の解決と検証
# 使い方: ./01_setup_A.sh [green-field|brown-field]   （既定: brown-field）
#
# 新規セッションは走らせない。既に完了したAI-DLC開発について、
#   - 開発セッションのJSONLログが存在するか
#   - 生成コードのコミット境界(base..head)がリポジトリに存在するか
# を検証し、results/<対象>/A_sessions.tsv に検査レコードを登録する。
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"

if [ -z "$FIELD_DIR" ] || [ ! -d "$FIELD_DIR" ]; then
  echo "ERROR: 検査対象 '$TARGET_FIELD' が見つかりません（FIELD_DIR=/path/to で明示指定可）" >&2
  exit 1
fi
if [ -z "$A_SESSION_JSONL" ]; then
  echo "ERROR: 対象 '$TARGET_FIELD' のセッションJSONLが未定義です（A_SESSION_JSONL=で指定）" >&2
  exit 1
fi
if [ ! -s "$A_SESSION_JSONL" ]; then
  echo "ERROR: セッションJSONLがありません: $A_SESSION_JSONL" >&2
  echo "  開発を実施したマシンの ~/.claude/projects/ から該当ファイルを探して A_SESSION_JSONL= で指定してください。" >&2
  exit 1
fi
for c in "$A_BASE_COMMIT" "$A_HEAD_COMMIT"; do
  git -C "$REPO_ROOT" rev-parse -q --verify "$c^{commit}" >/dev/null || {
    echo "ERROR: コミット $c が $REPO_ROOT に存在しません" >&2; exit 1; }
done

# セッションログが本当にこの対象の開発か軽く検証（cwdの一致）
# 注: pipefail下では head|grep -q がSIGPIPEで偽の失敗になるため、ファイルを直接grepする
if ! grep -q '"cwd":"[^"]*aidlc-workshop' "$A_SESSION_JSONL"; then
  echo "WARN: セッションJSONLのcwdがaidlc-workshop配下ではないようです。対象違いの可能性があります。" >&2
fi

mkdir -p "$RESULTS"
MANIFEST="$RESULTS/A_sessions.tsv"
printf 'key\tsession_jsonl\tbase_commit\thead_commit\tdiff_prefix\n' > "$MANIFEST"
printf '%s\t%s\t%s\t%s\t%s\n' "$TARGET_FIELD" "$A_SESSION_JSONL" "$A_BASE_COMMIT" "$A_HEAD_COMMIT" "$A_DIFF_PREFIX" >> "$MANIFEST"

echo "検査対象   : $FIELD_DIR"
echo "セッション : $A_SESSION_JSONL ($(du -h "$A_SESSION_JSONL" | cut -f1))"
echo "コミット境界: $A_BASE_COMMIT..${A_HEAD_COMMIT}（接頭辞: '${A_DIFF_PREFIX:-なし}'）"
echo "-> $MANIFEST"
echo "次: ./02_measure_A.py ${TARGET_FIELD}（または ./00_run_A.sh $TARGET_FIELD で全工程を自動実行）"
