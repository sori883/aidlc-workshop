#!/usr/bin/env bash
# 全領域一括エントリポイント: A（事後検査）→ C・D（理解度クイズ・説明責任テスト）
# 使い方: ./00_run_all.sh [green-field|brown-field]   （既定: brown-field）
#
# レポートは対象ごとに results/<対象>/ に分かれて出力される:
#   results/<対象>/レポートA.md … A領域（開発効率・品質の事後検査）
#   results/<対象>/レポート.md  … C・D領域（コンテキスト喪失耐性・説明責任）
#
# 各工程は生成済みの出力をスキップするため、途中で失敗しても再実行すれば続きから走る。
# 所要時間の目安: A領域は数分＋AI採点3回。C・D領域は回答8セッション＋採点で1時間前後。
set -euo pipefail
TARGET="${1:-brown-field}"
cd "$(dirname "$0")"

echo "===== [1/2] A領域: 完了済みAI-DLC開発の事後検査（${TARGET}） ====="
./00_run_A.sh "$TARGET"

echo
echo "===== [2/2] C・D領域: 理解度クイズ・説明責任テスト（${TARGET}） ====="
if [ -s "scenarios/$TARGET/scenario.json" ]; then
  ./07_setup.sh  "$TARGET"
  ./08_run.sh    "$TARGET"
  ./10_grade.sh  "$TARGET"
  ./11_report.py "$TARGET"
  CD_DONE=1
else
  echo "スキップ: シナリオ '$TARGET' の定義（scenarios/$TARGET/scenario.json）が未整備です。"
  echo "  追加手順は README「新しいシナリオの追加手順」を参照してください"
  echo "  （scenarios/smoke-test/ が最小の雛形、scenarios/brown-field/ が実例になります）。"
  CD_DONE=0
fi

echo
echo "===== 完了 ====="
echo "A領域   : results/$TARGET/レポートA.md"
if [ "$CD_DONE" = 1 ]; then
  echo "C・D領域: results/$TARGET/レポート.md"
else
  echo "C・D領域: スキップ（質問セット未整備）"
fi
echo "実行後にやること（採点のサンプル検証など）は README を参照。"
