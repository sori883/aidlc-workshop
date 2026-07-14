#!/usr/bin/env bash
# aidlc-eval 共通設定
# 自己完結・相対パス構成: このディレクトリごと aidlc-workshop リポジトリ直下
# （green-field / brown-field と同じ階層）に置いて使う。
set -euo pipefail

EVAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS="$EVAL_ROOT/prompts"    # 採点ヘッダなど対象非依存のプロンプト
SHIELD="$EVAL_ROOT/shield"      # シールド置き場のルート（実験セッションに見せない）

# 評価対象ワークスペース。各スクリプトの第1引数 > 環境変数 > 既定値(brown-field)
TARGET_FIELD="${TARGET_FIELD:-brown-field}"

# 対象ごとの質問セット。評価のコア（実行・採点スクリプト、prompts/grade_*.md）は
# 対象非依存で、対象固有の質問・模範解答・meta.json はこの2ディレクトリに置く。
PROMPTS_TARGET="$PROMPTS/$TARGET_FIELD"   # 実験セッションに渡す質問文（模範解答なし）
SHIELD_TARGET="$SHIELD/$TARGET_FIELD"     # 模範解答・採点基準・meta.json

# 出力・作業ディレクトリは対象ごとに分離する
RESULTS="$EVAL_ROOT/results/$TARGET_FIELD"
WORK="$EVAL_ROOT/work/$TARGET_FIELD"

# 質問セットの有無を確認（C・D領域を実行するには4ファイルすべて必要）
cd_question_set_ok() {
  [ -s "$PROMPTS_TARGET/C_prompt.md" ] && [ -s "$PROMPTS_TARGET/D_prompt.md" ] &&
  [ -s "$SHIELD_TARGET/C_理解度クイズ.md" ] && [ -s "$SHIELD_TARGET/D_想定質問リスト.md" ] &&
  [ -s "$SHIELD_TARGET/meta.json" ]
}
if ! cd_question_set_ok; then
  echo "注意: 対象 '$TARGET_FIELD' のC・D質問セットがありません。C・D領域を実行するには" >&2
  echo "      prompts/$TARGET_FIELD/{C_prompt.md,D_prompt.md} と" >&2
  echo "      shield/$TARGET_FIELD/{C_理解度クイズ.md,D_想定質問リスト.md,meta.json} を作成してください" >&2
  echo "      （brown-field のものが雛形になります。A領域は config.sh への対象定義のみで動きます）。" >&2
fi

# 対象ディレクトリの自動検出: 親ディレクトリ → このディレクトリ直下 の順。
# 明示指定する場合: FIELD_DIR=/path/to/brown-field ./07_setup.sh
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

TRIALS="${TRIALS:-3}"

# 回答セッションに許可するツール（読み取り専用）
# Q16でテスト実行まで許したい場合は "Read,Glob,Grep,Bash(pytest:*),Bash(pip:*),Bash(python:*)" などに変更
ANSWER_TOOLS="${ANSWER_TOOLS:-Read,Glob,Grep}"

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
