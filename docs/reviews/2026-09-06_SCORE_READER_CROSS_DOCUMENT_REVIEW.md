# score-reader Cross-Document Review Record（2026-09-06）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | REVIEW-SCORE-READER-20260906-002 |
| Version（バージョン） | 0.4 |
| Status（ステータス） | Resolved |
| Review Date（レビュー日） | 2026-09-06 |
| Created Date（作成日） | 2026-09-06 |
| Last Updated（最終更新日） | 2026-09-06 |
| Repository（リポジトリ） | t-oikawa-sendai/score-reader |
| Branch（ブランチ） | main |
| Reviewed Commit（レビュー対象コミット） | 45b2004027df0f4c2efd465995d034a945d6c388 |
| Previous Review Record（前回レビュー記録） | docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md |
| Owner（管理者） | Takashi Oikawa |
| Reviewer（レビュアー） | GEM_REVIEWER_PERSONA |
| Related Documents（関連文書） | README.md / SKILL.md / NOTICE / docs/design/01_REQUEST_DEFINITION.md / docs/design/02_REQUIREMENTS_DEFINITION.md / docs/design/03_DATA_AND_SECURITY_DESIGN.md / docs/design/04_UI_AND_FLOW_DESIGN.md / docs/design/05_ARCHITECTURE_DESIGN.md / docs/design/06_OPERATION_AND_HANDOFF.md / docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md |

---

## 1. Purpose

本文書は、再レビュー RV-013〜RV-021 の検証結果と、プロジェクトオーナーが確定した設計判断を GitHub 管理対象として保存する。

レビュー対象は `45b2004027df0f4c2efd465995d034a945d6c388` 時点の正本文書である。正本設計文書への反映内容は各設計文書を正本として扱う。本文書はレビュー記録であり、法的助言ではない。

修正結果の再レビューは完了した。RV-013〜RV-021 の成立部分は正本文書へ反映済みである。本記録の Status は `Resolved` とする。

---

## 2. Review Scope and Decision

| 項目 | 内容 |
|---|---|
| 対象 | RV-013〜RV-021 の検証結果と確定した設計判断を正本設計文書へ反映する |
| 実施範囲 | 文書修正のみ |
| コード凍結 | 現行プロトタイプは凍結を維持する |
| Status | 本記録は `Resolved`。設計文書本体の Status は `Draft` のまま |
| Reviewer | `GEM_REVIEWER_PERSONA` |
| commit / push | 本記録作成時点で未実施。差分確認後にプロジェクトオーナーが判断する |

---

## 3. Findings and Judgments

| ID | 判定 | 成立範囲 | 反映先 |
|---|---|---|---|
| RV-013 | 一部成立 | 期限超過時運用の欠落と、公開判断期限情報の重複展開。固定期限 `2026-09-06` を廃止し、権利判断完了まで暫定公開を継続する。最終判断責任者は Takashi Oikawa。新しい期限は設定しない | README.md / NOTICE / 01 / 03 / 05 / 06 / 既存レビュー記録 |
| RV-014 | 一部成立 | `docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md` の Version・Change History・`Pending` 表記が、差し戻し反映 SHA 追記後の状態へ追随していなかった | 既存レビュー記録 |
| RV-015 | 成立 | 権利・法務未解決事項の一次追跡先を `03_DATA_AND_SECURITY_DESIGN.md` TBD-005 へ統一する。`05_ARCHITECTURE_DESIGN.md` TBD-005 はテスト素材の技術的な由来の確認に限定する | NOTICE / 01 / 03 / 05 / 06 / 既存レビュー記録 |
| RV-016 | 成立 | 対応 OS は macOS のみ。実行環境は macOS 上で動作する Python 3.x。特定の macOS バージョンは固定しない。Windows および Linux の動作保証・動作検証は対象外。Windows 確認 TBD は削除する | 05_ARCHITECTURE_DESIGN.md / 06_OPERATION_AND_HANDOFF.md |
| RV-017 | 成立 | SC-009 は「検査 [5] として Unpitched 件数を報告できる」ことだけに限定する。テキスト/JSON の現行表示差は `02` Appendix / FUT-003 で扱う | 01_REQUEST_DEFINITION.md / 02_REQUIREMENTS_DEFINITION.md |
| RV-018 | 成立 | `NOTICE` の music21 ソフトウェア帰属表示を公式 `v10.3.0` LICENSE に一致させる。ソフトウェア本体のライセンスと corpus 内エンコーディングの権利は分離する | NOTICE |
| RV-019 | 一部成立 | 全パート対応 TBD の分割自体は適切な責務分離として維持する。成立部分は、TBD 間の依存関係が明示されていなかったことに限定する | 02 / 05 / 06 |
| RV-020 | 成立（軽微） | README の実行例をリポジトリルート起点へ統一する | README.md |
| RV-021 | 成立（軽微） | GUI・Web UI・原本 PDF 横並び画面の対象外理由から、検査 [3][4] 全パート対応との別件注記を削除する。将来検討事項である分類は維持する | 05_ARCHITECTURE_DESIGN.md |

---

## 4. Limits of Partial Findings

RV-013、RV-014、RV-019 は一部成立である。次は成立範囲に含めない。

**RV-013**

- 「設定日と期限日が同じなので期限として機能しない」とは断定しない。
- 成立部分は、期限超過時運用の欠落と期限情報の重複展開に限定する。

**RV-014**

- 「本記録作成時点で未実施」という過去時点の記述と、後日の SHA 追記が必ず自己矛盾するとは扱わない。
- レビュー記録自身を含むコミット SHA が同じ文書に記載されていないこと自体は不具合としない。
- 成立部分は、Version・Change History・`Pending` 表記が SHA 追記後の状態へ追随していなかったことに限定する。

**RV-019**

- 要件・実装・運用の TBD 分割自体は適切な責務分離として維持する。
- TBD の統合・削除は行わない。
- 成立部分は、TBD 間の依存関係が明示されていなかったことに限定する。

---

## 5. Confirmed Design Judgments

| 項目 | 確定判断 |
|---|---|
| 公開判断期限 | 固定期限 `2026-09-06` を廃止する。新しい期限は設定しない。「判断期限は未定」へ置き換えない |
| 暫定公開 | 権利判断が完了するまで、現在公開中のテスト素材を暫定公開する。権利確認中・公開可否未確定である旨の表示を維持する |
| 最終判断責任者 | Takashi Oikawa |
| 権利一次追跡先 | `03_DATA_AND_SECURITY_DESIGN.md` TBD-005（個別利用条件、世界向け再配布可否の法的確定、適用される法域） |
| 技術的な由来 | `05_ARCHITECTURE_DESIGN.md` TBD-005 に限定する |
| 対応 OS | macOS のみ。特定バージョンは固定しない。実行環境は macOS 上で動作する Python 3.x |
| Windows / Linux | 動作保証・動作検証の対象外。将来 TBD として追加しない |
| SC-009 | Unpitched 件数の報告。現行表示差は含めない |
| 全パート対応 TBD | `02` TBD-002 が親。`05` TBD-002 はその子（実装方針）。`06` TBD-001 は両者に依存する子（運用・テスト手順） |
| FUT-004 | 全パート対応 TBD とは別件のまま維持する |
| 自動修正・自動統合・Web UI | 将来検討事項 |
| 原本 PDF 横並び画面 | 本リポジトリの対象外。本リポジトリでは設計・実装方針を定義しない。人間が MuseScore 等を使用して原本 PDF と目視照合する既存運用は維持する |
| 複数 MusicXML 比較 | 本実装確定スコープのまま維持する |
| 設計文書 Status | `Draft` のまま維持する |

法的な結論は新たに記載しない。テスト素材の公開可否を法的に確定したとは記載しない。

---

## 6. Documents Changed in This Review Response

次の文書を変更した。

- `README.md`
- `NOTICE`
- `docs/design/01_REQUEST_DEFINITION.md`
- `docs/design/02_REQUIREMENTS_DEFINITION.md`
- `docs/design/03_DATA_AND_SECURITY_DESIGN.md`
- `docs/design/05_ARCHITECTURE_DESIGN.md`
- `docs/design/06_OPERATION_AND_HANDOFF.md`
- `docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md`
- `docs/reviews/2026-09-06_SCORE_READER_CROSS_DOCUMENT_REVIEW.md`（新規）

次は変更していない。

- `SKILL.md`（Windows / Linux を対応環境とする記載がなく、期限・追跡先の不整合もなかった）
- `docs/design/04_UI_AND_FLOW_DESIGN.md`（実行手順は `cd prototype/src` と相対パスが一致しており、README とは起点が異なるが単独で成立する）

---

## 7. Documents and Artifacts Not Changed

次は変更していない。

- `prototype/src/verify_score.py`
- `prototype/tests/` 配下の全ファイル
- `prototype/requirements.txt`
- `LICENSE`
- `LICENSE-CODE`
- `LICENSE-DOCS`
- その他のソースコード、依存関係、Git 設定
- FR-001〜FR-012 の既存動作仕様
- ライセンス体系

コード変更はなく、commit および push は本記録作成時点で実施していない。

---

## 8. TBD Dependency Recorded

検査 [3][4] 全パート対応に関する TBD は統合しない。依存順序は次のとおりである。

1. `02_REQUIREMENTS_DEFINITION.md` TBD-002（親）: 検査 [3][4] を全パート対応へ拡張するか否かを決定する
2. `05_ARCHITECTURE_DESIGN.md` TBD-002（子）: 全パート対応を採用した場合の実装方針を決定する
3. `06_OPERATION_AND_HANDOFF.md` TBD-001（子）: 採用判断と実装方針の確定後、運用・テスト手順を定義する

Owner、期限「未定」、Status `Open` は変更していない。

---

## 9. Disclaimer

本記録は法的助言ではない。テスト素材の公開可能性、再配布の許否、適用される法域、権利者の確定を述べない。

---

## 10. Change History

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-09-06 | 初版。RV-013〜RV-021 の判定と確定した設計判断を記録。Status は Changes Requested | Takashi Oikawa |
| 0.2 | 2026-09-06 | 修正結果を再レビューし、RV-013〜RV-021の成立部分が正本文書へ反映済みであることを確認。StatusをResolvedへ更新 | Takashi Oikawa |
| 0.3 | 2026-09-06 | プロジェクトオーナーの追加決定を記録。原本 PDF 横並び画面を将来検討事項から外し、本リポジトリでは設計・実装方針を定義しない対象へ分割。自動修正・自動統合・Web UI は将来検討事項のまま。人間が MuseScore 等を使用して原本 PDF と目視照合する既存運用は維持。Status は Resolved を維持 | Takashi Oikawa |
| 0.4 | 2026-09-06 | 日本語表現の明確化。判定・設計判断の変更なし | Takashi Oikawa |
