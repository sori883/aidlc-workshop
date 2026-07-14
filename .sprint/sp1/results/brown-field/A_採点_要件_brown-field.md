REQ FR-1.1: 2 | 新規 `POST /reservations/recurring` を series/router.py で追加し既存単発APIは無変更、test_create_series_by_count で201を検証。
REQ FR-1.2: 2 | RecurringReservationCreate が room/開始終了/予約者/count・until を受け取り、create_series 系テストで送信・生成を検証。
REQ FR-1.3: 2 | generate_occurrences が7日刻みで同時刻を生成し、test_series_weekly_7_day_step / test_count_is_weekly_7_day_step で検証。
REQ FR-1.4: 2 | count/until 排他を service とスキーマで実装、両方・両方未指定の400を test_both/neither_*_400 で、until inclusive を境界テストで検証。
REQ FR-1.5: 2 | MAX_OCCURRENCES=52 で len>52 時に400、test_over_max_count_400（count=53）で検証。
REQ FR-1.6: 2 | 全回の has_conflict を INSERT 前に走査し1件でも重複なら ConflictError(409)、test_conflict_rejects_whole_series_atomically で409かつ0件登録を検証。
REQ FR-1.7: 2 | AvailabilityService.has_conflict（半開区間 overlaps）を再利用し、重複拒否テストで実効性を検証。
REQ FR-1.8: 2 | occurrences[0] 開始が datetime.now() 未満で400、test_past_start_400 で検証。
REQ FR-1.9: 2 | start>=end・booker_name空・room存在を検証し、test_bad_time_order_400 と test_missing_room_404 で検証（名前必須のみ未テストだが主要検証は網羅）。
REQ FR-1.10: 2 | 201で series_id と ReservationOut リストを返し、test_create_series_by_count で series_id と occurrences を検証。
REQ FR-2.1: 2 | `POST /reservations/recurring/{series_id}/cancel` を実装し test_cancel_series_* で呼び出しを検証。
REQ FR-2.2: 1 | list_future_active_by_series（start_time>now かつ active）で実装は正しいが、全回が未来のケースしかテストが無く「過去/cancelled回を変更しない」挙動を検証していない。
REQ FR-2.3: 2 | cancel_series は未来active無しでも200を返し冪等、test_cancel_series_idempotent で2回実行の200を検証。
REQ FR-2.4: 2 | get_series が NotFoundError(404) を送出、test_cancel_missing_series_404 で検証。
REQ FR-2.5: 2 | SeriesOut で occurrences 各状態を返し、test_cancel_series で200と cancelled 状態を検証。
REQ FR-3.1: 2 | 個別回は新規API無しで既存 `/reservations/{id}/cancel` を流用、test_individual_occurrence_cancel_via_existing_api で検証。
REQ FR-3.2: 2 | 各回は series_id を持つ通常予約行で既存キャンセルが機能し、他回 active 維持を同テストで検証。
REQ FR-4.1: 2 | ReservationOut に series_id(str|None) を追加、test_single_reservation_has_null_series_id で null を検証。
REQ FR-4.2: 2 | 一覧に series_id が含まれ test_series_id_shown_in_listing で、詳細 GET も個別キャンセルテスト内で status 取得により検証。
REQ FR-4.3: 2 | `GET /reservations/recurring/{series_id}` を実装、test_get_series / test_get_missing_series_404 で検証。
REQ FR-5.1: 2 | reservation_series テーブルを id/繰返しルール/予約者/created_at 付きで定義し、test_get_series の occurrence_count 検証で永続化を確認。
REQ FR-5.2: 2 | reservations.series_id を String(36)/NULL可/FK で追加、occurrences の series_id と単発 null テストで検証。
REQ FR-5.3: 1 | _ensure_series_id_column で既存DBへの ALTER 追加を create_all 前に実装しているが、既存DBへの列追加パスを検証するテストが無い。
TESTS_KEPT: yes
