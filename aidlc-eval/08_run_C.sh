#!/usr/bin/env bash
# C. 理解度クイズ: 2条件 × TRIALS試行 の回答セッションを実行する
# 使い方: ./08_run_C.sh [評価対象フォルダ名]   （既定: brown-field）
# 出力: results/<対象>/C_回答_{A|B}_{n}.md（既存ファイルはスキップ = 中断後の再実行可）
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"

[ -d "$WORK/cond-A" ] || { echo "ERROR: 先に ./07_setup.sh $TARGET_FIELD を実行してください" >&2; exit 1; }
[ -s "$PROMPTS_TARGET/C_prompt.md" ] || { echo "ERROR: 質問セット $PROMPTS_TARGET/C_prompt.md がありません（config.shの注意を参照）" >&2; exit 1; }

for cond in A B; do
  for t in $(seq 1 "$TRIALS"); do
    out="$RESULTS/C_回答_${cond}_${t}.md"
    if [ -s "$out" ]; then echo "skip: ${out}（既存）"; continue; fi
    echo "=== C クイズ 条件$cond 試行$t 開始 $(date +%H:%M:%S) ==="
    (
      cd "$WORK/cond-$cond"
      # shellcheck disable=SC2046
      claude -p "$(cat "$PROMPTS_TARGET/C_prompt.md")" \
        $(model_args "$ANSWER_MODEL") \
        --allowedTools "$ANSWER_TOOLS"
    ) > "$out" || { echo "ERROR: 条件$cond 試行$t が失敗しました（$out を削除して再実行してください）" >&2; exit 1; }
    echo "-> $out"
  done
done
echo "C クイズ 全セッション完了"
