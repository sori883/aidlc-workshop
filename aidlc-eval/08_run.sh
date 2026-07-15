#!/usr/bin/env bash
# 回答セッション実行: scenario.json の tasks × runs × trials を claude -p で回す
# 使い方: ./08_run.sh [シナリオ名]   （既定: brown-field）
# 出力: results/<シナリオ>/<タスク>_回答_<実行名>[_<試行>].md（既存はスキップ = 中断後の再実行可）
#
# シールド原則: セッションは work のコピー（$WORK/cond-*）をカレントディレクトリとして
# 起動し、質問文（プロンプトファイル）のみを受け取る。shield/ は絶対に渡さない。
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"
scenario_required

# 許可ツール: 環境変数 ANSWER_TOOLS > scenario.json の answer_tools
TOOLS="${ANSWER_TOOLS:-$(python3 "$EVAL_ROOT/scenario_lib.py" "$SCENARIO_DIR" answer-tools)}"

ran=0
while IFS=$'\t' read -r task run trial cond prompt outname; do
  if [ ! -d "$WORK/cond-$cond" ]; then
    echo "ERROR: 条件 '$cond' が未構築です。先に ./07_setup.sh $TARGET_FIELD を実行してください" >&2
    exit 1
  fi
  out="$RESULTS/$outname"
  if [ -s "$out" ]; then echo "skip: ${out}（既存）"; continue; fi
  echo "=== タスク$task 実行$run 試行$trial 開始 $(date +%H:%M:%S) ==="
  (
    cd "$WORK/cond-$cond"
    # shellcheck disable=SC2046
    claude -p "$(cat "$prompt")" \
      $(model_args "$ANSWER_MODEL") \
      --allowedTools "$TOOLS"
  ) > "$out" || { echo "ERROR: タスク$task 実行$run 試行$trial が失敗しました（$out を削除して再実行してください）" >&2; exit 1; }
  echo "-> $out"
  ran=$((ran + 1))
done < <(python3 "$EVAL_ROOT/scenario_lib.py" "$SCENARIO_DIR" runs)

echo "回答セッション完了（新規実行: $ran）"
