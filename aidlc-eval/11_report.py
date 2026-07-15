#!/usr/bin/env python3
"""採点結果を集計し、results/<シナリオ>/レポート.md を生成する。

使い方: ./11_report.py [シナリオ名]   （既定: brown-field）

コアはシナリオ非依存: 問数・カテゴリ・ダミー問番号・条件ラベル・差分列・集計形式は
すべて scenarios/<シナリオ>/scenario.json の tasks.<ID>.report から読む。

集計形式（report.style）:
- "scores"（既定）: 実行別の平均スコア表 + カテゴリ別 + ダミー捏造数 + 問別平均。
  report.diff = [x, y] を与えると差分列（x−y）を出す。
- "coverage": 回答可(2点)/部分可(1点)/不可(0点) の件数表。
  report.holes_from = <実行名> を与えると「記録の穴リスト」（0点かつ非ダミーの問）を出す。
"""
import os
import re
import sys
from pathlib import Path
from statistics import mean

from scenario_lib import ScenarioError, grade_file, load_scenario

TARGET = (
    sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TARGET_FIELD", "brown-field")
)
EVAL_ROOT = Path(__file__).resolve().parent
RESULTS = Path(os.environ.get("RESULTS_ROOT", EVAL_ROOT / "results")) / TARGET
SCENARIO_DIR = EVAL_ROOT / "scenarios" / TARGET

SCORE_RE = re.compile(r"^\s*Q(\d+)\s*[:：]?\s*([012])\b")


def parse_scores(path: Path, max_q: int) -> dict[int, int]:
    scores: dict[int, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = SCORE_RE.match(line)
        if m:
            q, s = int(m.group(1)), int(m.group(2))
            if 1 <= q <= max_q and q not in scores:
                scores[q] = s
    missing = [q for q in range(1, max_q + 1) if q not in scores]
    if missing:
        print(f"WARN: {path.name} でQ{missing}の点数を読み取れませんでした", file=sys.stderr)
    return scores


def load_run_scores(task_id: str, task: dict) -> dict[str, list[dict[int, int]]]:
    """実行名 -> 試行ごとの {問番号: 点数}。採点ファイルが無い試行は除く。"""
    total = task["report"]["total"]
    out: dict[str, list[dict[int, int]]] = {}
    for rid, run in task["runs"].items():
        trials = run.get("trials", 1)
        files = [RESULTS / grade_file(task_id, rid, trials, t) for t in range(1, trials + 1)]
        out[rid] = [parse_scores(f, total) for f in files if f.exists()]
    return out


def run_label(run: dict, rid: str) -> str:
    return run.get("label", rid)


def report_scores(lines: list[str], task_id: str, task: dict, scores) -> None:
    rep = task["report"]
    runs = task["runs"]
    total_q = rep["total"]
    dummy = set(rep.get("dummy", []))
    categories = {
        name: range(lo, hi + 1) for name, (lo, hi) in rep.get("categories", {}).items()
    }
    diff = rep.get("diff")
    rids = list(runs)

    shorts = {rid: runs[rid].get("short", run_label(runs[rid], rid)) for rid in rids}
    lines.append("試行数: " + " / ".join(f"{shorts[r]}={len(scores[r])}" for r in rids))
    lines.append("")
    header = "| 指標 | " + " | ".join(run_label(runs[r], r) for r in rids) + " |"
    ncols = len(rids)
    if diff:
        header += f" 差分 {diff[0]}−{diff[1]} |"
        ncols += 1
    lines.append(header)
    lines.append("| --- |" + " --- |" * ncols)

    def avg_total(trials):
        return mean(sum(t.values()) for t in trials) if trials else float("nan")

    def avg_cat(trials, qs):
        return mean(sum(t.get(q, 0) for q in qs) for t in trials) if trials else float("nan")

    def row(label: str, vals: dict[str, float], fmt: str) -> str:
        cells = [format(vals[r], fmt) for r in rids]
        if diff:
            cells.append(format(vals[diff[0]] - vals[diff[1]], "+" + fmt))
        return f"| {label} | " + " | ".join(cells) + " |"

    totals = {r: avg_total(scores[r]) for r in rids}
    lines.append(row(f"総合 ({total_q * 2}点満点)", totals, ".1f"))
    for cat, qs in categories.items():
        vals = {r: avg_cat(scores[r], qs) for r in rids}
        lines.append(row(f"{cat} ({len(list(qs)) * 2}点満点)", vals, ".1f"))

    if dummy:
        def fabrications(trials):
            return sum(1 for t in trials for q in dummy if t.get(q) == 0)

        fabs = {r: fabrications(scores[r]) for r in rids}
        n_first = max(len(scores[rids[0]]), 1)
        lines.append(row(f"ダミー質問の捏造数 (各{len(dummy) * n_first}問中)", fabs, "d"))
    lines.append("")

    # 問別平均（どの質問で差が付いたか）
    lines.append("### 問別平均スコア (0-2)")
    lines.append("")
    qheader = "| 問 | " + " | ".join(rids) + " |"
    if diff:
        qheader += " 差 |"
    lines.append(qheader)
    lines.append("| --- |" + " --- |" * ncols)
    for q in range(1, total_q + 1):
        vals = {
            r: (mean(t.get(q, 0) for t in scores[r]) if scores[r] else float("nan"))
            for r in rids
        }
        lines.append(row(f"Q{q}", vals, ".1f"))
    lines.append("")


def report_coverage(lines: list[str], task_id: str, task: dict, scores) -> None:
    rep = task["report"]
    runs = task["runs"]
    total_q = rep["total"]
    dummy = set(rep.get("dummy", []))
    # 採点ファイルのある実行のみ（coverage は各実行の第1試行を使う）
    present = {rid: scores[rid][0] for rid in runs if scores[rid]}

    lines.append("| 指標 | " + " | ".join(run_label(runs[r], r) for r in present) + " |")
    lines.append("| --- |" + " --- |" * len(present))

    def counts(s):
        return (
            sum(1 for v in s.values() if v == 2),
            sum(1 for v in s.values() if v == 1),
            sum(1 for v in s.values() if v == 0),
        )

    lines.append("| 回答可(2点) | " + " | ".join(f"{counts(s)[0]}/{total_q}" for s in present.values()) + " |")
    lines.append("| 部分可(1点) | " + " | ".join(str(counts(s)[1]) for s in present.values()) + " |")
    lines.append("| 不可(0点) | " + " | ".join(str(counts(s)[2]) for s in present.values()) + " |")
    lines.append("")

    hf = rep.get("holes_from")
    if hf in present:
        holes = [q for q, s in present[hf].items() if s == 0 and q not in dummy]
        lines.append("### 記録の穴リスト（記録ありでも答えられなかった質問）")
        lines.append("")
        if holes:
            gf = grade_file(task_id, hf, task["runs"][hf].get("trials", 1), 1)
            for q in sorted(holes):
                lines.append(
                    f"- Q{q}（詳細は results/{TARGET}/{gf} と"
                    f" scenarios/{TARGET}/{task['shield']} を参照）"
                )
        else:
            lines.append("- なし（想定質問はすべて記録から回答可能だった）")
        lines.append("")


def main() -> None:
    try:
        sc = load_scenario(SCENARIO_DIR)
    except ScenarioError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    lines = [
        f"# {sc.get('report_title', '検証結果レポート')} — {TARGET}",
        "",
        "生成元: aidlc-eval/11_report.py",
        "",
    ]
    found = False
    for task_id, task in sc["tasks"].items():
        scores = load_run_scores(task_id, task)
        if not any(scores.values()):
            continue
        found = True
        rep = task["report"]
        lines.append(f"## {rep.get('title', task_id)}")
        lines.append("")
        if rep.get("style", "scores") == "coverage":
            report_coverage(lines, task_id, task, scores)
        else:
            report_scores(lines, task_id, task, scores)

    if not found:
        print(
            f"採点ファイルが {RESULTS} に見つかりません。先に 10_grade.sh {TARGET} を実行してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    out = RESULTS / "レポート.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
