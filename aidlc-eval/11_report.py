#!/usr/bin/env python3
"""採点結果を集計し、results/<対象>/レポート.md を生成する。

使い方: ./11_report.py [評価対象フォルダ名]   （既定: brown-field）
"""
import os
import re
import sys
from pathlib import Path
from statistics import mean

TARGET_FIELD = (
    sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TARGET_FIELD", "brown-field")
)
RESULTS = Path(__file__).resolve().parent / "results" / TARGET_FIELD

C_CATEGORIES = {
    "設計判断の理由": range(1, 7),    # Q1-6  (満点12)
    "暗黙の仕様・制約": range(7, 15),  # Q7-14 (満点16)
    "運用": range(15, 18),            # Q15-17 (満点6)
    "ダミー(捏造検出)": range(18, 21), # Q18-20 (満点6)
}
C_TOTAL_Q = 20
D_TOTAL_Q = 17
D_DUMMY = {16, 17}

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


def report_c(lines: list[str]) -> None:
    per_cond: dict[str, list[dict[int, int]]] = {"A": [], "B": []}
    for f in sorted(RESULTS.glob("C_採点_*_*.md")):
        m = re.match(r"C_採点_([AB])_(\d+)", f.stem)
        if not m:
            continue
        per_cond[m.group(1)].append(parse_scores(f, C_TOTAL_Q))
    if not per_cond["A"] and not per_cond["B"]:
        return

    lines.append("## C. 理解度クイズ")
    lines.append("")
    n_a, n_b = len(per_cond["A"]), len(per_cond["B"])
    lines.append(f"試行数: 条件A={n_a} / 条件B={n_b}")
    lines.append("")
    lines.append("| 指標 | 条件A(コードのみ) | 条件B(+aidlc-docs) | 差分 B−A |")
    lines.append("| --- | --- | --- | --- |")

    def avg_total(trials):
        return mean(sum(t.values()) for t in trials) if trials else float("nan")

    def avg_cat(trials, qs):
        return mean(sum(t.get(q, 0) for q in qs) for t in trials) if trials else float("nan")

    ta, tb = avg_total(per_cond["A"]), avg_total(per_cond["B"])
    lines.append(f"| 総合 (40点満点) | {ta:.1f} | {tb:.1f} | {tb - ta:+.1f} |")
    for cat, qs in C_CATEGORIES.items():
        ca, cb = avg_cat(per_cond["A"], qs), avg_cat(per_cond["B"], qs)
        full = len(list(qs)) * 2
        lines.append(f"| {cat} ({full}点満点) | {ca:.1f} | {cb:.1f} | {cb - ca:+.1f} |")

    def fabrications(trials):
        return sum(1 for t in trials for q in C_CATEGORIES["ダミー(捏造検出)"] if t.get(q) == 0)

    fa, fb = fabrications(per_cond["A"]), fabrications(per_cond["B"])
    lines.append(f"| ダミー質問の捏造数 (各{3 * max(n_a, 1)}問中) | {fa} | {fb} | {fb - fa:+d} |")
    lines.append("")

    # 問別平均（どの質問で差が付いたか）
    lines.append("### 問別平均スコア (0-2)")
    lines.append("")
    lines.append("| 問 | A | B | 差 |")
    lines.append("| --- | --- | --- | --- |")
    for q in range(1, C_TOTAL_Q + 1):
        qa = mean(t.get(q, 0) for t in per_cond["A"]) if per_cond["A"] else float("nan")
        qb = mean(t.get(q, 0) for t in per_cond["B"]) if per_cond["B"] else float("nan")
        lines.append(f"| Q{q} | {qa:.1f} | {qb:.1f} | {qb - qa:+.1f} |")
    lines.append("")


def report_d(lines: list[str]) -> None:
    conds = {}
    for name, label in [("records", "記録あり(aidlc-docs)"), ("code", "記録なし(コードのみ)")]:
        f = RESULTS / f"D_採点_{name}.md"
        if f.exists():
            conds[name] = (label, parse_scores(f, D_TOTAL_Q))
    if not conds:
        return

    lines.append("## D. 説明責任テスト")
    lines.append("")
    lines.append("| 指標 | " + " | ".join(v[0] for v in conds.values()) + " |")
    lines.append("| --- |" + " --- |" * len(conds))

    def counts(scores):
        return (
            sum(1 for s in scores.values() if s == 2),
            sum(1 for s in scores.values() if s == 1),
            sum(1 for s in scores.values() if s == 0),
        )

    row2 = [f"{counts(v[1])[0]}/{D_TOTAL_Q}" for v in conds.values()]
    row1 = [str(counts(v[1])[1]) for v in conds.values()]
    row0 = [str(counts(v[1])[2]) for v in conds.values()]
    lines.append("| 回答可(2点) | " + " | ".join(row2) + " |")
    lines.append("| 部分可(1点) | " + " | ".join(row1) + " |")
    lines.append("| 不可(0点) | " + " | ".join(row0) + " |")
    lines.append("")

    if "records" in conds:
        holes = [
            q for q, s in conds["records"][1].items() if s == 0 and q not in D_DUMMY
        ]
        lines.append("### 記録の穴リスト（記録ありでも答えられなかった質問）")
        lines.append("")
        if holes:
            for q in sorted(holes):
                lines.append(f"- Q{q}（詳細は results/D_採点_records.md と shield/D_想定質問リスト.md を参照）")
        else:
            lines.append("- なし（想定質問はすべて記録から回答可能だった）")
        lines.append("")


def main() -> None:
    lines = [
        f"# 検証結果レポート（C・D領域） — {TARGET_FIELD}",
        "",
        "生成元: aidlc-eval/11_report.py",
        "",
    ]
    report_c(lines)
    report_d(lines)
    if len(lines) <= 4:
        print(
            f"採点ファイルが {RESULTS} に見つかりません。先に 10_grade.sh {TARGET_FIELD} を実行してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    out = RESULTS / "レポート.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
