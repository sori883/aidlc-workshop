#!/usr/bin/env bash
# 実験条件を scenario.json の定義どおり $WORK（既定: リポジトリ外）に構築する
# 使い方: ./07_setup.sh [シナリオ名]   （既定: brown-field）
#
# 条件ごとの構築手順（scenario_lib.py が scenario.json から展開する）:
#   COPY_ALL     ワークスペースを丸ごとコピー
#   REMOVE       コピーから除去する相対パス（グロブ可）。
#                .git を除去する理由: git履歴には aidlc-docs が含まれ `git show` 経由で
#                シールドが破れるため。比較条件も揃えて削除し、条件差を
#                「ドキュメントの有無」だけにする。
#   INCLUDE      （include_only 条件）列挙した相対パスだけをコピー
#   OVERLAY      シナリオ同梱の追加ファイル群を上書きコピー
#   HOOK         シナリオ同梱スクリプトを実行（障害注入などシナリオ固有の準備用）
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"
scenario_required

WORKSPACE="$(python3 "$EVAL_ROOT/scenario_lib.py" "$SCENARIO_DIR" workspace)"
if [ ! -d "$WORKSPACE" ]; then
  echo "ERROR: 対象ワークスペース '$WORKSPACE' がありません（$SCENARIO_DIR/scenario.json の workspace を確認）" >&2
  exit 1
fi
echo "評価対象: $WORKSPACE"
echo "作業ディレクトリ: $WORK"
mkdir -p "$WORK" "$RESULTS"

cond_dir=""
while IFS=$'\t' read -r op arg; do
  case "$op" in
    COND)
      cond_dir="$WORK/cond-$arg"
      rm -rf "$cond_dir"
      mkdir -p "$cond_dir"
      echo "-- 条件 $arg" ;;
    COPY_ALL)
      cp -R "$WORKSPACE/." "$cond_dir/" ;;
    REMOVE)
      # shellcheck disable=SC2086  # グロブ展開を許すため arg は引用しない
      rm -rf "$cond_dir/"$arg ;;
    INCLUDE)
      if [ -e "$WORKSPACE/$arg" ]; then
        mkdir -p "$cond_dir/$(dirname "$arg")"
        cp -R "$WORKSPACE/$arg" "$cond_dir/$arg"
      else
        echo "   注意: include_only の '$arg' がワークスペースにありません（スキップ）" >&2
      fi ;;
    OVERLAY)
      cp -R "$arg/." "$cond_dir/" ;;
    HOOK)
      COND_DIR="$cond_dir" SCENARIO_DIR="$SCENARIO_DIR" bash "$arg" ;;
  esac
done < <(python3 "$EVAL_ROOT/scenario_lib.py" "$SCENARIO_DIR" conditions)

echo "OK: $WORK に実験条件を作成しました"
ls -d "$WORK"/cond-*
