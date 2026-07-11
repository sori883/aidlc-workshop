#!/usr/bin/env bash
# A領域: 全自動エントリポイント（検査対象の解決→ログ解析→品質測定→AI採点→レポート）
# 使い方: ./00_run_A.sh [green-field|brown-field]   （既定: brown-field）
#
# 各工程は個別スクリプト（01〜05）に分かれており、単体でも再実行できる。
# 生成済みの出力はスキップされるため、途中で失敗してもこのスクリプトの再実行で続きから走る。
# 人間の作業は、完了後の採点サンプル検証（README「実行後にやること」）のみ。
set -euo pipefail
TARGET="${1:-brown-field}"
cd "$(dirname "$0")"

echo "===== A領域 検査パイプライン: $TARGET ====="
./01_setup_A.sh   "$TARGET"
./02_measure_A.py "$TARGET"
./03_quality_A.sh "$TARGET"
./04_grade_A.sh   "$TARGET"
./05_report_A.py  "$TARGET"
echo "===== 完了: results/$TARGET/レポートA.md ====="