# NFR Design 計画 — Unit-1: reservation-service

## 質問カテゴリの評価（適用可否）
NFR Requirements と Functional Design で関連する判断が確定済みのため、新規の質問は不要と判断した（曖昧点なし）。各カテゴリの適用可否:

| カテゴリ | 適用 | 判断 |
|---|---|---|
| Resilience Patterns | 限定的 | ローカル・低同時実行。トランザクション整合性のみ扱う。リトライ/サーキットブレーカーは N/A |
| Scalability Patterns | N/A | 単一プロセス・少人数（Q-N1=A）。スケール機構なし |
| Performance Patterns | 限定的 | SQLite ローカルで即応。キャッシュ不要。重複判定はインデックス活用のみ |
| Security Patterns | 限定的 | 認証なし（要件）。入力バリデーションと ORM による SQLi 回避のみ |
| Logical Components | N/A | キュー/キャッシュ/CB 等の追加インフラ部品なし。単一アプリ＋SQLite |

## 実行チェックリスト
- [x] nfr-design-patterns.md 生成（採用パターンと適用箇所）
- [x] logical-components.md 生成（論理コンポーネント構成）
