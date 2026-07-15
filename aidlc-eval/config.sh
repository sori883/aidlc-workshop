#!/usr/bin/env bash
# aidlc-eval 共通設定
# 自己完結・相対パス構成: このディレクトリごと aidlc-workshop リポジトリ直下
# （green-field / brown-field と同じ階層）に置いて使う。
set -euo pipefail

EVAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS="$EVAL_ROOT/prompts"    # 採点ヘッダなどシナリオ非依存のプロンプト
SHIELD="$EVAL_ROOT/shield"      # A領域用シールド置き場（実験セッションに見せない）

# 評価対象。各スクリプトの第1引数 > 環境変数 > 既定値(brown-field)。
# A領域では対象フォルダ名、C・D系ではシナリオ名（scenarios/ 配下のディレクトリ名）を指す。
TARGET_FIELD="${TARGET_FIELD:-brown-field}"

# A領域の対象別シールド（C・D系のシールドは scenarios/<シナリオ>/shield/ に移動済み）
SHIELD_TARGET="$SHIELD/$TARGET_FIELD"

# C・D系のシナリオ定義。実験条件・質問セット・試行回数などはすべてここに定義する
# （コアの 07/08/10/11 はシナリオ非依存。README「新しいシナリオの追加手順」参照）。
SCENARIOS="$EVAL_ROOT/scenarios"
SCENARIO_DIR="$SCENARIOS/$TARGET_FIELD"

# 出力は対象ごとに分離する
RESULTS_ROOT="${RESULTS_ROOT:-$EVAL_ROOT/results}"
RESULTS="$RESULTS_ROOT/$TARGET_FIELD"

# 実験条件のコピー置き場。既定でリポジトリの外に置く:
# work/ が aidlc-workshop リポジトリ内部にあると、実験セッションが親の .git
# （aidlc-docs と shield の履歴を平文で含む。reflog 等は Read だけで読める）に
# 相対パスで到達でき、シールドが破れるため（sp1 の green-field 実行で実際に発生）。
WORK_ROOT="${WORK_ROOT:-$HOME/.cache/aidlc-eval/work}"
WORK="$WORK_ROOT/$TARGET_FIELD"

# シナリオ定義の有無（C・D系スクリプトの冒頭で呼ぶ）
scenario_required() {
  if [ ! -s "$SCENARIO_DIR/scenario.json" ]; then
    echo "ERROR: シナリオ '$TARGET_FIELD' の定義（$SCENARIO_DIR/scenario.json）がありません。" >&2
    echo "  scenarios/ 配下にシナリオ定義ディレクトリを作成してください" >&2
    echo "  （手順は README「新しいシナリオの追加手順」、雛形は scenarios/smoke-test/）。" >&2
    exit 1
  fi
}

# 対象ディレクトリの自動検出（A領域用。C・D系の対象パスは scenario.json の workspace）:
# 親ディレクトリ → このディレクトリ直下 の順。
# 明示指定する場合: FIELD_DIR=/path/to/brown-field ./01_setup_A.sh
if [ -z "${FIELD_DIR:-}" ]; then
  if [ -d "$EVAL_ROOT/../$TARGET_FIELD" ]; then
    FIELD_DIR="$(cd "$EVAL_ROOT/../$TARGET_FIELD" && pwd)"
  elif [ -d "$EVAL_ROOT/$TARGET_FIELD" ]; then
    FIELD_DIR="$EVAL_ROOT/$TARGET_FIELD"
  else
    FIELD_DIR=""
  fi
fi

# モデル設定（採点は回答生成と別モデルにするのが原則）
ANSWER_MODEL="${ANSWER_MODEL:-}"      # 空 = デフォルトモデル
GRADE_MODEL="${GRADE_MODEL:-opus}"

# 回答セッションの許可ツールと試行回数は scenario.json に定義する。
# ANSWER_TOOLS を環境変数で与えた場合のみ、全条件一律で上書きされる（08_run.sh 参照）。

model_args() { # $1: モデル名（空なら何も出力しない）
  if [ -n "${1:-}" ]; then printf -- "--model %s" "$1"; fi
}

# ---- A領域（開発効率・品質）設定 ----
# 既に完了したAI-DLC開発の成果物とセッションログを事後検査する（新規セッションは走らせない）。
# 検査対象は第1引数で green-field / brown-field を選択。対象ごとに
# 「開発セッションのJSONL」と「生成コードのコミット境界(base..head)」を定義する。
# 静的解析はuvx経由で実行（未導入でも動く）。cdk-nag相当のPython代替
UVX="${UVX:-uvx}"
# カバレッジ測定用venv（03が自動作成）
QUALITY_VENV="$EVAL_ROOT/.venv-quality"
# セッションログの保存元
CLAUDE_PROJECTS="${CLAUDE_PROJECTS:-$HOME/.claude/projects}"
# 検査対象リポジトリ（aidlc-workshop）のルート = FIELD_DIR の親
REPO_ROOT="${REPO_ROOT:-$(dirname "${FIELD_DIR:-$EVAL_ROOT/..}")}"

# 対象ごとの既定値（環境変数で上書き可）。コミットは aidlc-workshop の実履歴:
#   f6d03df(init) → 227a8ca(green-field構築, 当時はリポジトリ直下) → 69a4905(整理) → 878f9bd(定期予約追加)
case "$TARGET_FIELD" in
  green-field)
    A_SESSION_JSONL="${A_SESSION_JSONL:-$CLAUDE_PROJECTS/-Users-const-sori883-aidlc-workshop/8bdfff0b-0f29-49c6-a28e-a95573d77908.jsonl}"
    A_BASE_COMMIT="${A_BASE_COMMIT:-f6d03df}"   # 構築前（init直後）
    A_HEAD_COMMIT="${A_HEAD_COMMIT:-227a8ca}"   # 構築完了コミット
    A_DIFF_PREFIX="${A_DIFF_PREFIX:-}"          # 当時はリポジトリ直下に生成されたため接頭辞なし
    ;;
  brown-field)
    A_SESSION_JSONL="${A_SESSION_JSONL:-$CLAUDE_PROJECTS/-Users-const-sori883-aidlc-workshop-brown-field/154a1501-aebc-4038-bfe1-eb7fffd47fc0.jsonl}"
    A_BASE_COMMIT="${A_BASE_COMMIT:-69a4905}"   # 定期予約追加前
    A_HEAD_COMMIT="${A_HEAD_COMMIT:-878f9bd}"   # 定期予約追加コミット
    A_DIFF_PREFIX="${A_DIFF_PREFIX:-brown-field/}"  # コミット内の対象パス接頭辞
    ;;
  *)
    A_SESSION_JSONL="${A_SESSION_JSONL:-}"; A_BASE_COMMIT="${A_BASE_COMMIT:-}"
    A_HEAD_COMMIT="${A_HEAD_COMMIT:-}"; A_DIFF_PREFIX="${A_DIFF_PREFIX:-}"
    ;;
esac
# 生成コードのdiffから常に除外するもの（AI-DLCの足場・ドキュメント・実行時生成物）
A_DIFF_EXCLUDES=(':(exclude,glob)**/aidlc-docs/**' ':(exclude,glob)**/.aidlc-rule-details/**'
                 ':(exclude,glob)**/CLAUDE.md' ':(exclude,glob)**/*.db'
                 ':(exclude,glob)**/__pycache__/**' ':(exclude,glob)**/.hypothesis/**'
                 ':(exclude,glob)**/.pytest_cache/**' ':(exclude,glob)**/docs/**'
                 ':(exclude,glob)**/README*.md' ':(exclude,glob)**/.gitignore')
