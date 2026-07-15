#!/usr/bin/env bash
# 採点: results/<シナリオ>/ にある回答ファイルを1件ずつ別モデルで採点する
# 使い方: ./10_grade.sh [シナリオ名]   （既定: brown-field）
# 出力: results/<シナリオ>/<タスク>_採点_*.md（既存はスキップ）
# ブラインド性: 採点セッションには回答本文のみを渡す（ファイル名・条件ラベルは渡らない）
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"
scenario_required

grade_one() { # $1=採点ヘッダ $2=シールドファイル $3=回答ファイル $4=出力
  if [ -s "$4" ]; then echo "skip: $4（既存）"; return; fi
  echo "=== 採点: $(basename "$3") ==="
  {
    cat "$1"
    echo
    echo "--- 質問・模範解答・採点基準 ---"
    cat "$2"
    echo
    echo "--- 採点対象の回答 ---"
    cat "$3"
  } | (
    cd "$EVAL_ROOT"
    # shellcheck disable=SC2046
    claude -p $(model_args "$GRADE_MODEL") --allowedTools ""
  ) > "$4" || { echo "ERROR: 採点失敗（$4 を削除して再実行してください）" >&2; exit 1; }
  echo "-> $4"
}

shopt -s nullglob
while IFS=$'\t' read -r task header shield; do
  for f in "$RESULTS/${task}_回答_"*.md; do
    base="$(basename "$f" .md)"
    grade_one "$header" "$shield" "$f" "$RESULTS/${base/回答/採点}.md"
  done
done < <(python3 "$EVAL_ROOT/scenario_lib.py" "$SCENARIO_DIR" tasks)
echo "採点完了。次: ./11_report.py $TARGET_FIELD"
