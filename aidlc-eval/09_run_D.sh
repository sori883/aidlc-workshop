#!/usr/bin/env bash
# D. 説明責任テスト: 記録あり(records) / 記録なし(code) の2セッションを実行する
# 使い方: ./09_run_D.sh [評価対象フォルダ名]   （既定: brown-field）
# 出力: results/<対象>/D_回答_{records|code}.md
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"

[ -d "$WORK/cond-D-records" ] || { echo "ERROR: 先に ./07_setup.sh $TARGET_FIELD を実行してください" >&2; exit 1; }
[ -s "$PROMPTS_TARGET/D_prompt.md" ] || { echo "ERROR: 質問セット $PROMPTS_TARGET/D_prompt.md がありません（config.shの注意を参照）" >&2; exit 1; }

run_d() { # $1=条件ディレクトリ名 $2=出力サフィックス
  out="$RESULTS/D_回答_$2.md"
  if [ -s "$out" ]; then echo "skip: ${out}（既存）"; return; fi
  echo "=== D テスト 条件$2 開始 $(date +%H:%M:%S) ==="
  (
    cd "$WORK/$1"
    # shellcheck disable=SC2046
    claude -p "$(cat "$PROMPTS_TARGET/D_prompt.md")" \
      $(model_args "$ANSWER_MODEL") \
      --allowedTools "$ANSWER_TOOLS"
  ) > "$out" || { echo "ERROR: 条件$2 が失敗しました（$out を削除して再実行してください）" >&2; exit 1; }
  echo "-> $out"
}

run_d cond-D-records records
run_d cond-D-none    code
echo "D テスト 全セッション完了"
