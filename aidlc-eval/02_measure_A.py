#!/usr/bin/env python3
"""A領域: 既存の開発セッションJSONLから速度・コスト系指標を機械集計する（事後検査）。

使い方: ./02_measure_A.py [green-field|brown-field]   （既定: brown-field）
入力  : results/<対象>/A_sessions.tsv（01が生成）
出力  : results/<対象>/
  A_測定_<キー>.json    … リードタイム・介入回数・拘束時間近似・トークン
  A_介入一覧_<キー>.md  … 人間介入の全文（時刻つき。承認後やり直し回数の人間集計・拘束時間の補正用）
  A_会話録_<キー>.md    … 会話録（AIのテキスト応答＋人間入力のみ。04のAI採点入力）

測定上の注意:
- トークンは message.id で重複除去して合計する（JSONLは同一メッセージを複数回記録するため、
  素朴な合計は約2倍に過大計上される）。サブエージェント(sidechain)消費も含む。
- 人間拘束時間は「直前のAI応答時刻→人間入力時刻」の間隔合計による近似（離席時間を含む上限値）。
  正確な値が必要な場合は A_介入一覧 を見て手動補正する。
- 人間入力は origin.kind=human かつ promptSource が typed/sdk のエントリ
  （SDK経由で投入された初回指示も含む）。
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

TARGET_FIELD = (
    sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TARGET_FIELD", "brown-field")
)
RESULTS = Path(__file__).resolve().parent / "results" / TARGET_FIELD
MANIFEST = RESULTS / "A_sessions.tsv"

HUMAN_SOURCES = {"typed", "sdk"}
D2_MARKER = "【仕様変更】"  # 注入型D2のマーカー（prompts/future/A_D2_inject.md 冒頭）
# 介入の簡易分類: 全文がこのいずれかに一致（前後空白無視）すれば承認系とみなす
APPROVAL_WORDS = {"承認", "続けて", "はい", "ok", "yes", "続行", "continue", "approve", "y"}


def ts(entry) -> datetime | None:
    t = entry.get("timestamp")
    if not t:
        return None
    return datetime.fromisoformat(t.replace("Z", "+00:00"))


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def parse_session(jsonl: Path) -> tuple[dict, list]:
    entries = []
    with jsonl.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # --- トークン（message.idで重複除去、最後の値を採用） ---
    usage_by_id: dict[str, dict] = {}
    for e in entries:
        if e.get("type") != "assistant":
            continue
        m = e.get("message", {})
        u = m.get("usage")
        if m.get("id") and u:
            usage_by_id[m["id"]] = u
    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    for u in usage_by_id.values():
        tokens["input"] += u.get("input_tokens") or 0
        tokens["output"] += u.get("output_tokens") or 0
        tokens["cache_read"] += u.get("cache_read_input_tokens") or 0
        tokens["cache_creation"] += u.get("cache_creation_input_tokens") or 0

    # --- 時系列イベント（人間入力・AI応答テキスト） ---
    events = []  # [dt, kind, text]   kind: human | ai
    seen_ai_ids: dict[str, int] = {}
    for e in entries:
        t = ts(e)
        if t is None:
            continue
        if (
            e.get("type") == "user"
            and (e.get("origin") or {}).get("kind") == "human"
            and e.get("promptSource") in HUMAN_SOURCES
        ):
            events.append([t, "human", text_of(e.get("message", {}).get("content"))])
        elif e.get("type") == "assistant":
            if e.get("isSidechain"):
                continue  # 会話録はメインスレッドのみ（トークンは全体を計上済み）
            m = e.get("message", {})
            txt = text_of(m.get("content"))
            mid = m.get("id")
            if mid in seen_ai_ids:
                events[seen_ai_ids[mid]][0] = t
                events[seen_ai_ids[mid]][2] = txt
            else:
                events.append([t, "ai", txt])
                if mid:
                    seen_ai_ids[mid] = len(events) - 1

    all_ts = [ts(e) for e in entries if ts(e)]
    humans = [ev for ev in events if ev[1] == "human"]

    # --- 拘束時間近似: 各人間入力(初回除く)について直前のAIイベントからの間隔 ---
    bound = 0.0
    for i, ev in enumerate(events):
        if ev[1] != "human" or (humans and ev is humans[0]):
            continue
        prev_ai = next((events[j][0] for j in range(i - 1, -1, -1) if events[j][1] == "ai"), None)
        if prev_ai:
            bound += (ev[0] - prev_ai).total_seconds()

    approvals = sum(
        1 for ev in humans[1:] if ev[2].strip().lower().rstrip("。.！!") in APPROVAL_WORDS
    )

    # --- D2（注入型マーカーがあれば時間系を機械計測し、直後のAI回答=影響範囲列挙を抽出） ---
    d2 = None
    d2_idx = next((i for i, ev in enumerate(events) if ev[1] == "human" and D2_MARKER in ev[2]), None)
    if d2_idx is not None:
        after = events[d2_idx + 1:]
        resp = []
        for ev in after:
            if ev[1] == "human":
                break
            resp.append(ev[2])
        d2 = {
            "injected_at": events[d2_idx][0].isoformat(),
            "time_to_session_end_sec": (max(all_ts) - events[d2_idx][0]).total_seconds(),
            "interventions_after": sum(1 for ev in after if ev[1] == "human"),
            "_answer": "\n".join(p for p in resp if p.strip()),
        }

    measured = {
        "d2_injected": {k: v for k, v in d2.items() if k != "_answer"} if d2 else None,
        "lead_time_sec": (max(all_ts) - min(all_ts)).total_seconds() if all_ts else None,
        "session_start": min(all_ts).isoformat() if all_ts else None,
        "session_end": max(all_ts).isoformat() if all_ts else None,
        "interventions": max(len(humans) - 1, 0),  # 初回の意図表明は除く
        "interventions_approval_like": approvals,
        "human_bound_approx_sec": bound,
        "tokens": tokens,
        "api_messages": len(usage_by_id),
    }
    return measured, events, (d2["_answer"] if d2 else None)


def fmt_dur(sec) -> str:
    if sec is None:
        return "-"
    return f"{int(sec // 3600)}:{int(sec % 3600 // 60):02d}:{int(sec % 60):02d}"


def main() -> None:
    if not MANIFEST.exists():
        print(f"ERROR: {MANIFEST} がありません。先に ./01_setup_A.sh を実行してください。", file=sys.stderr)
        sys.exit(1)

    rows = [r.split("\t") for r in MANIFEST.read_text(encoding="utf-8").splitlines()[1:] if r.strip()]
    printed = False
    for row in rows:
        key, jsonl_path = row[0], row[1]
        if not Path(jsonl_path).exists():
            print(f"WARN: {key} のセッションJSONLが見つかりません（{jsonl_path}）。スキップ。", file=sys.stderr)
            continue
        m, events, d2_answer = parse_session(Path(jsonl_path))
        if d2_answer:
            (RESULTS / f"A_D2影響範囲回答_{key}.md").write_text(d2_answer + "\n", encoding="utf-8")
        if not any(ev[1] == "human" for ev in events):
            print(f"WARN: {key} で人間入力を1件も検出できませんでした。JSONLのスキーマが想定"
                  f"（origin.kind=human, promptSource=typed/sdk）と異なる可能性があります。", file=sys.stderr)

        (RESULTS / f"A_測定_{key}.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        humans = [ev for ev in events if ev[1] == "human"]
        lines = [f"# 人間介入一覧 — {key}", "", f"介入回数（初回の意図表明を除く）: {m['interventions']}", ""]
        for ev in humans:
            lines += [f"## {ev[0].isoformat()}", "", "```", ev[2], "```", ""]
        (RESULTS / f"A_介入一覧_{key}.md").write_text("\n".join(lines), encoding="utf-8")

        lines = [f"# 会話録 — {key}", ""]
        for ev in events:
            if not ev[2].strip():
                continue
            who = "人間" if ev[1] == "human" else "AI"
            lines += [f"### [{ev[0].strftime('%H:%M:%S')}] {who}", "", ev[2], ""]
        (RESULTS / f"A_会話録_{key}.md").write_text("\n".join(lines), encoding="utf-8")

        if not printed:
            print(f"{'キー':<14} {'リードタイム':>10} {'介入':>4} {'承認系':>4} {'拘束近似':>10} {'出力トークン':>10} {'入力+cache':>12}")
            printed = True
        tk = m["tokens"]
        print(
            f"{key:<14} {fmt_dur(m['lead_time_sec']):>10} {m['interventions']:>4} "
            f"{m['interventions_approval_like']:>4} {fmt_dur(m['human_bound_approx_sec']):>10} "
            f"{tk['output']:>10,} {tk['input'] + tk['cache_read'] + tk['cache_creation']:>12,}"
        )

    if not printed:
        print("測定対象がありませんでした。", file=sys.stderr)
        sys.exit(1)
    print(f"\n-> {RESULTS}/A_測定_*.json ほか")
    print("次: ./03_quality_A.sh で品質測定、./04_grade_A.sh でAI採点")


if __name__ == "__main__":
    main()
