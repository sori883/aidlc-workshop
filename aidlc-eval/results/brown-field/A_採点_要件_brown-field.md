REQ FR-1.1: 2 | `POST /reservations/recurring` を新設し既存単発APIは無変更、test_create_series_by_count で検証されている。
REQ FR-1.2: 2 | RecurringReservationCreate が会議室・開始/終了・予約者・count/until を受け取り、API テストで実際に送信・検証している。
REQ FR-1.3: 2 | generate_occurrences が 7日刻み・同時刻・同室で生成し、test_series_weekly_7_day_step 等で検証されている。
REQ FR-1.4: 2 | `(count is None)==(until is None)` で両方/両方未指定を400にし、test_both/neither_400 で検証されている。
REQ FR-1.5: 2 | 上限52を超えると len>52 で ValidationError→400、count=53 の test_over_max_count_400 で検証されている。
REQ FR-1.6: 2 | 全回を先に has_conflict チェックし1回でも重複なら commit 前に409、原子性を test_conflict_rejects_whole_series_atomically で検証している。
REQ FR-1.7: 2 | AvailabilityService.has_conflict（既存半開区間ロジック）を再利用し、重複拒否テストで間接的に検証されている。
REQ FR-1.8: 2 | occurrences[0][0] < datetime.now() で過去開始を400、test_past_start_400 で検証されている。
REQ FR-1.9: 2 | start<end・名前必須・会議室存在を検証し、test_bad_time_order_400 と test_missing_room_404 で主要検証がテストされている。
REQ FR-1.10: 2 | 201 で series_id と ReservationOut リストを返し、test_create_series_by_count でレスポンス内容を検証している。
REQ FR-2.1: 2 | `POST /reservations/recurring/{series_id}/cancel` を新設し、cancel テスト群で検証されている。
REQ FR-2.2: 2 | list_future_active_by_series が start_time>now かつ active のみ抽出しキャンセルし、test_cancel_series_cancels_future_active_only で検証している（過去回の非変更は未検証）。
REQ FR-2.3: 2 | 未来active回が無ければ状態を変えず200を返し、test_cancel_series_idempotent で冪等性を検証している。
REQ FR-2.4: 2 | get_series が NotFoundError→404、test_cancel_missing_series_404 で検証されている。
REQ FR-2.5: 2 | SeriesOut で occurrences 付きシリーズ情報を200返却し、キャンセルテストで各回状態を検証している。
REQ FR-3.1: 2 | 新規APIを作らず既存 `POST /reservations/{id}/cancel` を流用し、test_individual_occurrence_cancel_via_existing_api で検証している。
REQ FR-3.2: 2 | 各回は series_id を持つ通常予約行で既存キャンセルAPIが機能し、他回がactiveのまま残ることをテストで検証している。
REQ FR-4.1: 2 | ReservationOut に `series_id: str|None=None` を追加し、test_single_reservation_has_null_series_id で単発nullを検証している。
REQ FR-4.2: 2 | 一覧レスポンスに series_id が含まれ、test_series_id_shown_in_listing で検証されている（詳細GETはフィールド共有で実装済）。
REQ FR-4.3: 2 | 任意の `GET /reservations/recurring/{series_id}` を実装し、test_get_series と test_get_missing_series_404 で検証している。
REQ FR-5.1: 2 | reservation_series テーブルを追加しシリーズ作成・GETの機能テストで永続化を実質的に検証している。
REQ FR-5.2: 2 | reservations に series_id（String(36), NULL可, FK）を追加し、単発null・シリーズ付与をテストで検証している。
REQ FR-5.3: 1 | _ensure_series_id_column による既存DBへの列追加を create_all に統合しているが、その移行パスを検証するテストが無い。
TESTS_KEPT: yes
