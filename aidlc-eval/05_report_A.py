#!/usr/bin/env python3
"""A領域: 検査結果を集計し、results/<対象>/レポートA.md を生成する。

既に完了したAI-DLC開発の事後検査。プロセス内在指標を絶対値で記録する
（素のClaude Codeとの比較はしない）。速度・コスト系は観測値として記録のみ。

使い方: ./05_report_A.py [green-field|brown-field]   （既定: brown-field）
入力: A_測定_*.json（02）/ A_品質_*.json（03）/ A_採点_*.md（04）
"""
import json
import os
import re
import sys
from pathlib import Path

TARGET_FIELD = (
    sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TARGET_FIELD", "brown-field")
)
RESULTS = Path(__file__).resolve().parent / "results" / TARGET_FIELD


def fmt_dur(sec) -> str:
    if sec is None or sec < 0:
        return "-"
    return f"{int(sec // 3600)}:{int(sec % 3600 // 60):02d}:{int(sec % 60):02d}"


def load_json(pattern: str) -> dict[str, dict]:
    out = {}
    for f in sorted(RESULTS.glob(pattern)):
        key = re.sub(r"^A_(測定|品質)_|\.json$", "", f.name)
        out[key] = json.loads(f.read_text(encoding="utf-8"))
    return out


def parse_lines(path: Path, regex: str) -> dict:
    found = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(regex, line.strip())
        if m:
            found.setdefault(m.group(1), m.group(2))
    return found


def main() -> None:
    measures = load_json("A_測定_*.json")
    quality = load_json("A_品質_*.json")
    lines = [f"# 検査結果レポート（A. 開発効率・品質） — {TARGET_FIELD}", "",
             "生成元: aidlc-eval/05_report_A.py",
             "測定方式: 完了済みAI-DLC開発の事後検査（プロセス内在指標の絶対値記録。素のClaude Code比較なし）", ""]

    # --- 速度・コスト（観測値） ---
    for key, m in measures.items():
        lines += [f"## 速度・コスト（観測値。比較対象を持たないため良否判定はせず記録のみ） — {key}", "",
                  "| 指標 | 値 |", "| --- | --- |",
                  f"| リードタイム（意図表明→セッション終了） | {fmt_dur(m['lead_time_sec'])} |",
                  f"| セッション期間 | {m.get('session_start', '?')[:19]} 〜 {m.get('session_end', '?')[:19]} |",
                  f"| 人間拘束時間（近似・上限） | {fmt_dur(m['human_bound_approx_sec'])} |",
                  f"| 介入回数（意図表明を除く） | {m['interventions']} |",
                  f"| うち承認系（簡易分類） | {m['interventions_approval_like']} |",
                  f"| 出力トークン | {m['tokens']['output']:,} |",
                  f"| 入力トークン（cache込） | {m['tokens']['input'] + m['tokens']['cache_read'] + m['tokens']['cache_creation']:,} |",
                  f"| APIメッセージ数 | {m['api_messages']} |",
                  "",
                  "※拘束時間は「直前のAI応答→人間入力」の間隔合計（離席込みの上限近似）。"
                  "承認後やり直し回数は A_介入一覧 から人間が数える（承認後の差し戻し発言）。", ""]

    # --- 品質（機械検査） ---
    for key, q in quality.items():
        lines += [f"## 品質（機械検査） — {key}（{q.get('commit_range', '?')}）", "",
                  "| 指標 | 値 |", "| --- | --- |",
                  f"| テスト（passed/failed。既存テスト含む全件） | {q['tests']['passed']}/{q['tests']['failed']} |",
                  f"| 生成コードのカバレッジ% | {q['coverage_changed_files_pct']} |",
                  f"| ruff所見（持ち込み分 = head−base） | {q['static']['ruff_delta']:+d}（head {q['static']['ruff_head']}） |",
                  f"| bandit所見（持ち込み分） | {q['static']['bandit_delta']:+d}（head {q['static']['bandit_head']}） |",
                  f"| 依存脆弱性（pip-audit） | {q['pip_audit_vulns']} |",
                  f"| 生成コードの規模（変更行数） | {q['churn_total_lines']} |",
                  f"| 変更・追加された app/ ファイル数 | {len(q['changed_app_files'])} |",
                  ""]

    # --- 要件カバレッジ（AI採点） ---
    for f in sorted(RESULTS.glob("A_採点_要件_*.md")):
        key = f.stem.replace("A_採点_要件_", "")
        scores = {q: int(s) for q, s in parse_lines(f, r"REQ\s+(\S+?)\s*[:：]\s*([012])\b").items()}
        lines += [f"## 要件カバレッジ（AI採点: 2=実装+テスト / 1=実装のみ / 0=未実装） — {key}", ""]
        if not scores:
            lines += [f"- スコア行を読み取れず（{f.name} を確認）", ""]
            continue
        n = len(scores)
        impl = sum(1 for s in scores.values() if s >= 1)
        tested = sum(1 for s in scores.values() if s == 2)
        lines.append(f"- 機能要件 {n}件: 実装 **{impl}/{n}**・テストまで **{tested}/{n}**")
        gaps = [q for q, s in scores.items() if s < 2]
        if gaps:
            lines.append(f"- 2点未満の要件: {', '.join(f'{q}={scores[q]}' for q in gaps)}（詳細は {f.name}）")
        kept = parse_lines(f, r"(TESTS_KEPT)\s*[:：]\s*(yes|no)\b")
        if kept.get("TESTS_KEPT") == "no":
            lines.append(f"- ⚠ 既存テストを壊す変更（削除・骨抜き化）が検出された（{f.name} 参照）")
        lines.append("")

    # --- 承認記録カバレッジ（AI採点） ---
    for f in sorted(RESULTS.glob("A_採点_承認記録_*.md")):
        key = f.stem.replace("A_採点_承認記録_", "")
        vals = parse_lines(f, r"(AUDIT_COVERAGE|AUDIT_PARTIAL)\s*[:：]\s*([\d/]+)")
        judges = parse_lines(f, r"J(\d+)\s*[:：]\s*(yes|partial|no)\b")
        lines += [f"## 承認記録カバレッジ（AI採点: 重要判断がaudit.md単体で追える割合） — {key}", "",
                  f"- カバレッジ **{vals.get('AUDIT_COVERAGE', '?')}**（partial {vals.get('AUDIT_PARTIAL', '?')}件） "
                  f"内訳: {' '.join(f'J{q}={s}' for q, s in sorted(judges.items(), key=lambda x: int(x[0])))}"]
        holes = [q for q, s in judges.items() if s == "no"]
        if holes:
            lines.append(f"- 記録の穴: J{', J'.join(sorted(holes, key=int))}（詳細は {f.name}。audit.mdの改善材料）")
        lines.append("")

    # --- D4 曖昧要件検出（事後検査版） ---
    for f in sorted(RESULTS.glob("A_採点_D4_*.md")):
        key = f.stem.replace("A_採点_D4_", "")
        scores = {q: int(s) for q, s in parse_lines(f, r"P(\d+)\s*[:：]\s*([012])\b").items()}
        lines += [f"## D4 曖昧要件検出（2=人間に確認 / 1=独断で文書化 / 0=未検討） — {key}", ""]
        if not scores:
            lines += [f"- スコア行を読み取れず（{f.name} を確認）", ""]
            continue
        n = len(scores)
        detected = sum(1 for s in scores.values() if s == 2)
        lines += [f"- 曖昧要件検出率（人間に確認）: **{detected}/{n}** "
                  f"（{' '.join(f'P{q}={s}' for q, s in sorted(scores.items(), key=lambda x: int(x[0])))}）", ""]

    # --- D2 仕様変更（判定→事象があれば指標どおり評価、なければ「なし」を記録） ---
    for f in sorted(RESULTS.glob("A_採点_D2判定_*.md")):
        key = f.stem.replace("A_採点_D2判定_", "")
        det = parse_lines(f, r"(D2_PRESENT|D2_SUMMARY)\s*[:：]\s*(.+)$")
        present = det.get("D2_PRESENT", "").strip().lower().startswith("yes")
        lines += [f"## D2 仕様変更テスト — {key}", ""]
        if not present:
            lines += ["- 判定: セッション内に仕様変更事象**なし**（該当なし。"
                      "注入型テストの資材は prompts/future/・shield/future/ に保管済み）", ""]
            continue
        lines.append(f"- 判定: 仕様変更事象**あり** — {det.get('D2_SUMMARY', '?')}")
        g = RESULTS / f"A_採点_D2_{key}.md"
        if g.exists():
            v = parse_lines(g, r"(HIT|MISS|EXTRA|REGRESSIONS_TRUE)\s*[:：]\s*(-?\d+)")
            m2 = (measures.get(key) or {}).get("d2_injected") or {}
            lines += ["",
                      "| 影響範囲: 的中 | 漏れ | 過剰 | 正味退行数 | 変更対応時間 | 変更後の介入 |",
                      "| --- | --- | --- | --- | --- | --- |",
                      f"| {v.get('HIT', '?')} | {v.get('MISS', '?')} | {v.get('EXTRA', '?')} "
                      f"| {v.get('REGRESSIONS_TRUE', '?')} | {fmt_dur(m2.get('time_to_session_end_sec', -1))} "
                      f"| {m2.get('interventions_after', '-')} |",
                      "",
                      "※変更対応時間・変更後の介入は注入マーカー（【仕様変更】）がある場合のみ自動計測。"
                      f"判定理由は {g.name} を参照。"]
        else:
            lines.append(f"- ⚠ 評価ファイル A_採点_D2_{key}.md が未生成（./04_grade_A.sh を再実行）")
        lines.append("")

    # --- D5 拡張の記述的検査 ---
    for key, q in quality.items():
        ext = q.get("extensions") or {}
        if ext.get("opt_in"):
            lines += [f"## D5 Extension検査（記述的） — {key}", "",
                      "| Extension | opt-in |", "| --- | --- |"]
            lines += [f"| {name} | {state} |" for name, state in ext["opt_in"].items()]
            pbt = ext.get("pbt_test_files") or []
            lines += ["", f"- PBT（Property-Based Testing）の痕跡: {len(pbt)}ファイル（{', '.join(pbt) if pbt else 'なし'}）",
                      "- ※有効/無効の所見数差分の比較は、比較セッションが必要なため将来実施。", ""]

    lines += ["## 対象外（将来実施）", "",
              "- **潜在欠陥数**: Phase 2 の障害注入実験と接続して測定する。",
              "- **仕込み型D4・注入型D2の統制実験**: 意図的に曖昧点/仕様変更を仕込む方式は"
              "新規セッションで将来実施（資材は prompts/future/・shield/future/ に保管済み）。", "",
              "## 解釈上の注意", "",
              "- 各指標は完了済みAI-DLC開発1件の絶対値。良否は「各ゲート/フェーズが機能しているか」"
              "（要件の取りこぼし・記録の穴・曖昧点の見逃しの有無）で読む。",
              "- 速度・コスト系は観測値であり、この数値単体で速い/遅いの判定はしない。",
              "- AI採点はサンプル検証（15%目安）で妥当性を確認すること（READMEの手順参照）。", ""]

    if not measures and not quality:
        print(f"集計対象が {RESULTS} にありません。01→02→03→04を先に実行してください。", file=sys.stderr)
        sys.exit(1)
    out = RESULTS / "レポートA.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
