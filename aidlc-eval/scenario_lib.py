#!/usr/bin/env python3
"""シナリオ定義（scenarios/<名前>/scenario.json）の読み込み・検証・プラン出力。

C・D系ハーネスのコア（07/08/10/11）は本モジュール経由でのみシナリオ定義を読む。
シナリオを追加するときにコアのスクリプトを変更してはならない（README「新しいシナリオの
追加手順」参照）。

bash からの使い方:
  python3 scenario_lib.py <シナリオdir> workspace     対象ワークスペースの絶対パス
  python3 scenario_lib.py <シナリオdir> answer-tools  回答セッションの許可ツール
  python3 scenario_lib.py <シナリオdir> conditions    07_setup.sh 用の構築プラン（TSV）
  python3 scenario_lib.py <シナリオdir> runs          08_run.sh 用の実行プラン（TSV）
  python3 scenario_lib.py <シナリオdir> tasks         10_grade.sh 用の採点プラン（TSV）
11_report.py からは load_scenario() を import して使う。

scenario.json のスキーマ（"_" 始まりのキーはコメントとして無視される）:
  workspace     対象ワークスペース（シナリオdir基準の相対パス or 絶対パス）
  answer_tools  回答セッションの許可ツール（省略時 "Read,Glob,Grep"）
  conditions    実験条件。条件名 -> 以下のいずれか/組み合わせ
                  remove:       ワークスペース全コピー後に除去する相対パス（グロブ可）
                  include_only: 列挙した相対パスだけをコピーする（removeと排他）
                  like:         他条件の定義を流用する（条件名）
                  overlay:      条件dirに上書きコピーする追加ファイル群（シナリオdir相対）
                  setup_hook:   構築後に実行するスクリプト（シナリオdir相対。
                                環境変数 COND_DIR / SCENARIO_DIR が渡る）
  tasks         質問タスク。タスクID -> {
                  prompt:       実験セッションに投げる文面（シナリオdir相対。模範解答なし）
                  shield:       質問・模範解答・採点基準（シナリオdir相対。セッションに見せない）
                  grade_header: 採点ヘッダ（コア共通 prompts/ 内のファイル名）
                  runs:         実行名 -> { condition, trials, label, short? }
                  report:       { title, total, categories?, dummy?, diff?,
                                  style?("scores"|"coverage"), holes_from? }
                }
"""

import json
import sys
from pathlib import Path

EVAL_ROOT = Path(__file__).resolve().parent
GRADE_HEADERS_DIR = EVAL_ROOT / "prompts"

COND_KEYS = {"remove", "include_only", "like", "overlay", "setup_hook"}
TASK_KEYS = {"prompt", "shield", "grade_header", "runs", "report"}
RUN_KEYS = {"condition", "trials", "label", "short"}
REPORT_KEYS = {"title", "total", "categories", "dummy", "diff", "style", "holes_from"}


class ScenarioError(Exception):
    pass


def _strip_comments(obj):
    if isinstance(obj, dict):
        return {k: _strip_comments(v) for k, v in obj.items() if not k.startswith("_")}
    return obj


def load_scenario(scenario_dir) -> dict:
    scenario_dir = Path(scenario_dir).resolve()
    cfg_path = scenario_dir / "scenario.json"
    if not cfg_path.is_file():
        raise ScenarioError(f"{cfg_path} がありません（シナリオ定義の設定ファイル）")
    cfg = _strip_comments(json.loads(cfg_path.read_text(encoding="utf-8")))
    _validate(cfg, scenario_dir)
    cfg["_dir"] = scenario_dir
    return cfg


def workspace_path(cfg) -> Path:
    ws = Path(cfg["workspace"])
    if not ws.is_absolute():
        ws = cfg["_dir"] / ws
    return ws.resolve()


def resolved_conditions(cfg) -> dict:
    """like を解決した条件定義を返す（like の連鎖は循環を検出してエラー）。"""
    conds = cfg["conditions"]

    def resolve(name, seen):
        if name in seen:
            raise ScenarioError(f"conditions: like の循環参照です: {' -> '.join(seen)} -> {name}")
        c = conds[name]
        if "like" not in c:
            return dict(c)
        base = resolve(c["like"], seen + [name])
        base.update({k: v for k, v in c.items() if k != "like"})
        return base

    return {name: resolve(name, []) for name in conds}


def _validate(cfg, scenario_dir):
    def err(msg):
        raise ScenarioError(f"{scenario_dir / 'scenario.json'}: {msg}")

    if not isinstance(cfg.get("workspace"), str) or not cfg["workspace"]:
        err("workspace（対象ワークスペースのパス）は必須です")
    conds = cfg.get("conditions")
    if not isinstance(conds, dict) or not conds:
        err("conditions（実験条件）は1つ以上必要です")
    for name, c in conds.items():
        if not isinstance(c, dict):
            err(f"conditions.{name} はオブジェクトで定義してください")
        for k in c:
            if k not in COND_KEYS:
                err(f"conditions.{name}: 不明なキー '{k}'（許可: {sorted(COND_KEYS)}）")
        if "remove" in c and "include_only" in c:
            err(f"conditions.{name}: remove と include_only は同時に指定できません")
        if "like" in c and c["like"] not in conds:
            err(f"conditions.{name}: like の参照先 '{c['like']}' がありません")
        for key in ("overlay", "setup_hook"):
            if key in c and not (scenario_dir / c[key]).exists():
                err(f"conditions.{name}: {key} '{c[key]}' がシナリオdir内にありません")

    tasks = cfg.get("tasks")
    if not isinstance(tasks, dict) or not tasks:
        err("tasks（質問タスク）は1つ以上必要です")
    for tid, t in tasks.items():
        for k in t:
            if k not in TASK_KEYS:
                err(f"tasks.{tid}: 不明なキー '{k}'（許可: {sorted(TASK_KEYS)}）")
        for key in ("prompt", "shield"):
            if not isinstance(t.get(key), str):
                err(f"tasks.{tid}: {key} は必須です")
            if not (scenario_dir / t[key]).is_file():
                err(f"tasks.{tid}: {key} '{t[key]}' がシナリオdir内にありません")
        gh = t.get("grade_header")
        if not isinstance(gh, str) or not (GRADE_HEADERS_DIR / gh).is_file():
            err(f"tasks.{tid}: grade_header '{gh}' が {GRADE_HEADERS_DIR} にありません")
        runs = t.get("runs")
        if not isinstance(runs, dict) or not runs:
            err(f"tasks.{tid}: runs（実行定義）は1つ以上必要です")
        for rid, r in runs.items():
            for k in r:
                if k not in RUN_KEYS:
                    err(f"tasks.{tid}.runs.{rid}: 不明なキー '{k}'（許可: {sorted(RUN_KEYS)}）")
            if r.get("condition") not in conds:
                err(f"tasks.{tid}.runs.{rid}: condition '{r.get('condition')}' が conditions にありません")
            trials = r.get("trials", 1)
            if not isinstance(trials, int) or trials < 1:
                err(f"tasks.{tid}.runs.{rid}: trials は1以上の整数です")
        rep = t.get("report")
        if not isinstance(rep, dict):
            err(f"tasks.{tid}: report（集計定義）は必須です")
        for k in rep:
            if k not in REPORT_KEYS:
                err(f"tasks.{tid}.report: 不明なキー '{k}'（許可: {sorted(REPORT_KEYS)}）")
        total = rep.get("total")
        if not isinstance(total, int) or total < 1:
            err(f"tasks.{tid}.report: total（問数）は1以上の整数で必須です")
        for q in rep.get("dummy", []):
            if not (isinstance(q, int) and 1 <= q <= total):
                err(f"tasks.{tid}.report: dummy の問番号 {q} が 1..{total} の範囲外です")
        for cat, rng in rep.get("categories", {}).items():
            ok = (
                isinstance(rng, list) and len(rng) == 2
                and all(isinstance(x, int) for x in rng)
                and 1 <= rng[0] <= rng[1] <= total
            )
            if not ok:
                err(f"tasks.{tid}.report: categories['{cat}'] は [開始問, 終了問]（1..{total}内）です")
        diff = rep.get("diff")
        if diff is not None and (
            not isinstance(diff, list) or len(diff) != 2 or any(d not in runs for d in diff)
        ):
            err(f"tasks.{tid}.report: diff は runs の実行名2つ（[被減算, 減算]）です")
        if rep.get("style", "scores") not in ("scores", "coverage"):
            err(f"tasks.{tid}.report: style は 'scores' か 'coverage' です")
        hf = rep.get("holes_from")
        if hf is not None and hf not in runs:
            err(f"tasks.{tid}.report: holes_from '{hf}' が runs にありません")

    # like 解決（循環検出）を実行しておく
    resolved = resolved_conditions({"conditions": conds})
    for name, c in resolved.items():
        if "remove" in c and "include_only" in c:
            err(f"conditions.{name}: like 解決後に remove と include_only が両立しています")


def answer_file(task_id: str, run_id: str, trials: int, trial: int) -> str:
    """回答ファイル名。試行1回の実行は試行番号なし（sp1の命名と互換）。"""
    if trials > 1:
        return f"{task_id}_回答_{run_id}_{trial}.md"
    return f"{task_id}_回答_{run_id}.md"


def grade_file(task_id: str, run_id: str, trials: int, trial: int) -> str:
    return answer_file(task_id, run_id, trials, trial).replace("_回答_", "_採点_", 1)


def _emit_conditions(cfg):
    for name, c in resolved_conditions(cfg).items():
        print(f"COND\t{name}")
        if "include_only" in c:
            for p in c["include_only"]:
                print(f"INCLUDE\t{p}")
        else:
            print("COPY_ALL\t-")
            for p in c.get("remove", []):
                print(f"REMOVE\t{p}")
        if "overlay" in c:
            print(f"OVERLAY\t{(cfg['_dir'] / c['overlay']).resolve()}")
        if "setup_hook" in c:
            print(f"HOOK\t{(cfg['_dir'] / c['setup_hook']).resolve()}")


def _emit_runs(cfg):
    for tid, t in cfg["tasks"].items():
        prompt = (cfg["_dir"] / t["prompt"]).resolve()
        for rid, r in t["runs"].items():
            trials = r.get("trials", 1)
            for n in range(1, trials + 1):
                out = answer_file(tid, rid, trials, n)
                print(f"{tid}\t{rid}\t{n}\t{r['condition']}\t{prompt}\t{out}")


def _emit_tasks(cfg):
    for tid, t in cfg["tasks"].items():
        header = (GRADE_HEADERS_DIR / t["grade_header"]).resolve()
        shield = (cfg["_dir"] / t["shield"]).resolve()
        print(f"{tid}\t{header}\t{shield}")


def main(argv):
    if len(argv) != 3 or argv[2] not in (
        "workspace", "answer-tools", "conditions", "runs", "tasks"
    ):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        cfg = load_scenario(argv[1])
        cmd = argv[2]
        if cmd == "workspace":
            print(workspace_path(cfg))
        elif cmd == "answer-tools":
            print(cfg.get("answer_tools", "Read,Glob,Grep"))
        elif cmd == "conditions":
            _emit_conditions(cfg)
        elif cmd == "runs":
            _emit_runs(cfg)
        elif cmd == "tasks":
            _emit_tasks(cfg)
    except (ScenarioError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
