# 要件確認の質問 (Requirements Verification Questions)

各質問について、`[Answer]:` タグの後に選択肢の記号（A, B, C...）を記入してください。
選択肢が合わない場合は、最後の「Other」を選び、`[Answer]:` の後に希望を記述してください。
すべて回答したら「done」または「完了」とお知らせください。

**ワークショップの前提**: 2〜3時間で完成する範囲に収めるため、スコープを絞る観点で質問しています。

---

## Question 1: 予約の時間管理方法
予約時間の管理方法はどれにしますか？

A) 開始時刻・終了時刻を自由に指定（分単位、例: 10:00-10:45）

B) 決まったタイムスロット制（例: 1時間単位のコマを予約）

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 2: 定期予約（繰り返し予約）
「毎週月曜10時」のような定期予約機能は必要ですか？

A) 不要（今回のスコープ外にする — ワークショップ向けに推奨）

B) 必要（繰り返しルールを指定して複数予約を一括作成）

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 3: 予約者の識別・権限
予約者の識別と権限管理はどうしますか？

A) 予約者は名前/メール等の文字列で入力するだけ（認証・権限なし — ワークショップ向けに推奨）

B) 簡易的なユーザー登録はするが、認証（ログイン）は行わない

C) 認証・ロール（管理者/一般）による権限管理を行う

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 4: キャンセルのルール
予約のキャンセルは誰が・いつできますか？

A) 誰でも予約IDを指定すればいつでもキャンセル可能（制約なし — ワークショップ向けに推奨）

B) 予約者本人のみキャンセル可能（予約者名/メールの一致で判定）

C) 開始時刻の一定時間前まで等、時間的な制約を設ける

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 5: 会議室の属性
会議室に持たせる情報はどこまで必要ですか？

A) 名前のみ（最小限 — ワークショップ向けに推奨）

B) 名前 + 収容人数

C) 名前 + 収容人数 + 設備（プロジェクター等）+ 場所

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 6: 空き状況の照会
「特定の日時に空いている会議室を探す」検索機能は必要ですか？

A) 不要 — 会議室ごとの予約一覧が見られれば十分（ワークショップ向けに推奨）

B) 必要 — 日時を指定して空いている会議室を検索できる

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 7: 営業時間・予約可能範囲の制約
予約可能な時間帯の制約は設けますか？

A) 制約なし（24時間いつでも予約可能 — ワークショップ向けに推奨）

B) 営業時間内のみ（例: 平日9:00-18:00）に制限する

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question: Security Extensions
セキュリティ拡張ルールをこのプロジェクトで強制しますか？

A) Yes — すべてのSECURITYルールをブロッキング制約として強制する（本番相当のアプリに推奨）

B) No — SECURITYルールをスキップする（PoC・プロトタイプ・実験的プロジェクトに適する。ワークショップ向けに推奨）

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question: Property-Based Testing Extension
プロパティベーステスト（PBT）ルールをこのプロジェクトで強制しますか？

A) Yes — すべてのPBTルールをブロッキング制約として強制する（ビジネスロジック・データ変換・シリアライズ・ステートフルな要素を持つプロジェクトに推奨）

B) Partial — 純粋関数とシリアライズのラウンドトリップに限りPBTルールを強制する

C) No — PBTルールをスキップする（単純なCRUDアプリ、UIのみ、薄い統合層に適する。ワークショップ向けに推奨）

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question: Resiliency Extensions
レジリエンシー（回復力）ベースラインをこのプロジェクトに適用しますか？

**概要**: AWS Well-Architected Framework（信頼性の柱）に基づく設計時のベストプラクティス群を、要件・設計・コードに反映させます。本番レディを保証するものではなく、あくまで出発点です。

A) Yes — レジリエンシーベースラインを設計時ガイダンスとして適用する（ビジネスクリティカルなワークロードに推奨）

B) No — レジリエンシーベースラインをスキップする（PoC・プロトタイプ・実験的プロジェクトに適する。ワークショップ向けに推奨）

X) Other (please describe after [Answer]: tag below)

[Answer]: B
