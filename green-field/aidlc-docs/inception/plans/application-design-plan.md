# アプリケーション設計計画 (Application Design Plan)

## 目的
会議室予約サービスの高レベルなコンポーネント構成・責務・サービス層・依存関係を設計する。
（詳細な業務ロジックは後続の Functional Design で扱う）

## 想定コンポーネント（初期案）
- **Room コンポーネント**: 会議室マスタの CRUD
- **Reservation コンポーデント**: 予約の作成・一覧・取得・キャンセル
- **Availability コンポーネント**: 重複判定と空き会議室検索（Reservation と密接）
- **サービス層**: 上記を束ねてユースケース（予約作成時の重複チェック等）をオーケストレーション
- **永続化層 (Repository)**: SQLite への読み書き

## 設計方針の質問（ユーザー回答）

### Q-D1: レイヤ構成
アプリの内部構成をどうしますか？

A) レイヤ分離（API層 router → サービス層 service → リポジトリ層 repository → DB）— 責務が明確・テストしやすい（推奨）

B) 簡易2層（router に処理をまとめ、DBアクセスも近接）— 記述量少・小規模向き

X) Other

[Answer]: A

### Q-D2: DBアクセス方式
SQLite へのアクセス方法は？

A) SQLAlchemy（ORM）を使う — モデル定義が明確、マイグレーション容易（推奨）

B) 標準ライブラリ sqlite3 で生SQL — 依存少・軽量だが記述は手作業

X) Other

[Answer]: A

### Q-D3: 識別子（ID）の型
Room / Reservation の ID の型は？

A) 整数の自動採番（AUTOINCREMENT）— シンプル・見やすい（推奨）

B) UUID 文字列 — 衝突しにくく分散向きだが冗長

X) Other

[Answer]: B

## 実行チェックリスト（承認後に実行）
- [x] components.md 生成（コンポーネント定義と責務）
- [x] component-methods.md 生成（メソッドシグネチャと入出力）
- [x] services.md 生成（サービス定義とオーケストレーション）
- [x] component-dependency.md 生成（依存関係とデータフロー）
- [x] application-design.md 生成（上記を統合）
- [x] 設計の完全性・一貫性を検証
