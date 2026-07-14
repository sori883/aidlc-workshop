#!/usr/bin/env bash
# A領域: AI採点（別モデル。既に完了した開発の成果物・ログに対する事後検査）
# 使い方: ./04_grade_A.sh [green-field|brown-field]   （既定: brown-field）
# 出力: results/<対象>/A_採点_*.md（既存はスキップ）
#
# 採点項目:
#   要件_<キー>     … 要件カバレッジ: requirements.md の各機能要件が生成コードの diff で
#                     実装/テストされているか（REQ <ID>: 0|1|2）
#   承認記録_<キー> … 承認記録カバレッジ: 会話録から重要判断を抽出し、audit.md への記録有無を判定
#   D4_<キー>       … 曖昧要件検出: 元指示/Visionの曖昧点リスト（シールド）のうち、
#                     質問駆動で確認された割合（P*: 2=確認 / 1=独断で文書化 / 0=未検討）
#   D2判定_<キー>   … セッション内に仕様変更事象があったかのAI判定（介入一覧から）
#   D2_<キー>       … 事象があった場合のみ: 影響範囲特定の正誤（HIT/MISS/EXTRA）と退行の判定。
#                     注入型（【仕様変更】マーカー+shield/future/の正解）にも自然発生にも対応
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"

MANIFEST="$RESULTS/A_sessions.tsv"
[ -s "$MANIFEST" ] || { echo "ERROR: 先に ./01_setup_A.sh $TARGET_FIELD を実行してください" >&2; exit 1; }
IFS=$'\t' read -r key _jsonl base head prefix < <(tail -n +2 "$MANIFEST" | head -1)

# 要件文書は head コミット時点のものを使う（現ディレクトリは後から改変されている可能性があるため）
show_head() { git -C "$REPO_ROOT" show "$head:${prefix}$1" 2>/dev/null; }
REQ_CONTENT="$(show_head "aidlc-docs/inception/requirements/requirements.md" || true)"
RVQ_CONTENT="$(show_head "aidlc-docs/inception/requirements/requirement-verification-questions.md" || true)"
TRANSCRIPT="$RESULTS/A_会話録_${key}.md"
D4_SHIELD="$SHIELD_TARGET/A_D4_曖昧点.md"

run_grade() { # $1=出力  stdinに採点入力
  if [ -s "$1" ]; then echo "skip: $1（既存）"; cat > /dev/null; return; fi
  echo "=== 採点: $(basename "$1") ==="
  (
    cd "$EVAL_ROOT"
    # shellcheck disable=SC2046
    claude -p $(model_args "$GRADE_MODEL") --allowedTools ""
  ) > "$1" || { echo "ERROR: 採点失敗（$1 を削除して再実行してください）" >&2; exit 1; }
  echo "-> $1"
}

# 1) 要件カバレッジ
if [ -n "$REQ_CONTENT" ]; then
  {
    cat "$PROMPTS/grade_A_req_header.md"
    echo; echo "--- 要件定義書（requirements.md） ---"; printf '%s\n' "$REQ_CONTENT"
    echo; echo "--- 生成コードの差分（${base}..${head}。ドキュメント類は除外済み） ---"
    echo '```diff'
    git -C "$REPO_ROOT" diff "$base" "$head" -- "${prefix:-.}" "${A_DIFF_EXCLUDES[@]}"
    echo '```'
  } | run_grade "$RESULTS/A_採点_要件_${key}.md"
else
  echo "skip: 要件_${key}（headコミットに requirements.md がありません）"
fi

# 2) 承認記録カバレッジ
if [ -s "$TRANSCRIPT" ]; then
  {
    cat "$PROMPTS/grade_A_audit_header.md"
    echo; echo "--- セッション会話録 ---"; cat "$TRANSCRIPT"
    echo; echo "--- このセッションで audit.md に追記された内容（diff） ---"
    echo '```diff'
    git -C "$REPO_ROOT" diff "$base" "$head" -- "${prefix}aidlc-docs/audit.md"
    echo '```'
  } | run_grade "$RESULTS/A_採点_承認記録_${key}.md"
else
  echo "skip: 承認記録_${key}（会話録なし。先に ./02_measure_A.py を実行）"
fi

# 3) D4 曖昧要件検出（事後検査版）
if [ -s "$D4_SHIELD" ] && [ -s "$TRANSCRIPT" ]; then
  {
    cat "$PROMPTS/grade_A_D4_header.md"
    echo; echo "--- 曖昧点リスト（正解・採点基準） ---"; cat "$D4_SHIELD"
    echo; echo "--- 要件検証質問（requirement-verification-questions.md） ---"
    if [ -n "$RVQ_CONTENT" ]; then printf '%s\n' "$RVQ_CONTENT"; else echo "（ファイルなし）"; fi
    echo; echo "--- 要件定義書（requirements.md） ---"
    if [ -n "$REQ_CONTENT" ]; then printf '%s\n' "$REQ_CONTENT"; else echo "（ファイルなし）"; fi
    echo; echo "--- セッション会話録 ---"; cat "$TRANSCRIPT"
  } | run_grade "$RESULTS/A_採点_D4_${key}.md"
else
  echo "skip: D4_${key}（曖昧点リスト $D4_SHIELD または会話録がありません）"
fi

# 4) D2 仕様変更（判定 → 事象があれば評価、なければ「なし」の記録のみ）
INTERV="$RESULTS/A_介入一覧_${key}.md"
D2_DETECT="$RESULTS/A_採点_D2判定_${key}.md"
if [ -s "$INTERV" ] && [ -s "$TRANSCRIPT" ]; then
  {
    cat "$PROMPTS/grade_A_D2detect_header.md"
    echo; echo "--- 人間介入一覧 ---"; cat "$INTERV"
  } | run_grade "$D2_DETECT"
  # 行頭アンカー＋大文字小文字・全角コロン許容（05_report_A.py のパーサと同基準）
  if grep -qiE '^D2_PRESENT[:：][[:space:]]*yes' "$D2_DETECT"; then
    D2_ANSWER="$RESULTS/A_D2影響範囲回答_${key}.md"
    {
      cat "$PROMPTS/grade_A_D2_header.md"
      # 注入型（マーカーあり）で用意済みの正解があればそれを基準にする
      if grep -q "【仕様変更】" "$INTERV" && [ -s "$SHIELD/future/A_D2_影響範囲正解.md" ]; then
        echo; echo "--- 正解（影響範囲の定義・採点基準） ---"; cat "$SHIELD/future/A_D2_影響範囲正解.md"
      fi
      if [ -s "$D2_ANSWER" ]; then
        echo; echo "--- 変更依頼直後のAIの影響範囲列挙 ---"; cat "$D2_ANSWER"
      fi
      echo; echo "--- セッション会話録 ---"; cat "$TRANSCRIPT"
    } | run_grade "$RESULTS/A_採点_D2_${key}.md"
  else
    echo "D2: 仕様変更事象なし（評価はスキップ。判定は ${D2_DETECT}）"
  fi
else
  echo "skip: D2判定_${key}（介入一覧または会話録なし。先に ./02_measure_A.py を実行）"
fi

echo "採点完了。次: ./05_report_A.py $TARGET_FIELD"
