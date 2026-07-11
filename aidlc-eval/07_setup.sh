#!/usr/bin/env bash
# 実験条件（4ディレクトリ）を work/<対象>/ 配下に作成する
# 使い方: ./07_setup.sh [評価対象フォルダ名]   （既定: brown-field）
set -euo pipefail
if [ $# -ge 1 ]; then export TARGET_FIELD="$1"; fi
source "$(dirname "$0")/config.sh"

if [ -z "$FIELD_DIR" ] || [ ! -d "$FIELD_DIR" ]; then
  echo "ERROR: 評価対象 '$TARGET_FIELD' が見つかりません。" >&2
  echo "  この aidlc-eval ディレクトリを green-field / brown-field と同じ階層（リポジトリ直下）に置くか、" >&2
  echo "  FIELD_DIR=/path/to/$TARGET_FIELD ./07_setup.sh のように明示指定してください。" >&2
  exit 1
fi
echo "評価対象: $FIELD_DIR"

mkdir -p "$WORK" "$RESULTS"

# 条件A: コードのみ（C評価用）
rm -rf "$WORK/cond-A"
mkdir -p "$WORK/cond-A"
cp -R "$FIELD_DIR/." "$WORK/cond-A/"
rm -rf "$WORK/cond-A/aidlc-docs" "$WORK/cond-A/.aidlc-rule-details" \
       "$WORK/cond-A/CLAUDE.md" "$WORK/cond-A/docs" "$WORK/cond-A/.git"

# 条件B: コード + aidlc-docs 一式（C評価用）
rm -rf "$WORK/cond-B"
mkdir -p "$WORK/cond-B"
cp -R "$FIELD_DIR/." "$WORK/cond-B/"
rm -rf "$WORK/cond-B/.git"

# 条件D-records: 記録のみ（aidlc-docs + Vision。コード・テストなし）
rm -rf "$WORK/cond-D-records"
mkdir -p "$WORK/cond-D-records"
cp -R "$FIELD_DIR/aidlc-docs" "$WORK/cond-D-records/aidlc-docs"
if [ -d "$FIELD_DIR/docs" ]; then cp -R "$FIELD_DIR/docs" "$WORK/cond-D-records/docs"; fi

# 条件D-none: コードのみ（条件Aと同一）
# 注意: git履歴にはaidlc-docsのコミットが含まれ`git show`で読めてしまうため、.gitは与えない
rm -rf "$WORK/cond-D-none"
cp -R "$WORK/cond-A" "$WORK/cond-D-none"

echo "OK: $WORK に実験条件を作成しました"
ls -d "$WORK"/cond-*
