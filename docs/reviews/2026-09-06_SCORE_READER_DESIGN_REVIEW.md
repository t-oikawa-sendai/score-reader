# score-reader Design Review Record（2026-09-06）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | REVIEW-SCORE-READER-20260906-001 |
| Version（バージョン） | 0.2 |
| Status（ステータス） | Changes Requested |
| Review Date（レビュー日） | 2026-09-06 |
| Created Date（作成日） | 2026-09-06 |
| Last Updated（最終更新日） | 2026-09-06 |
| Repository（リポジトリ） | t-oikawa-sendai/score-reader |
| Branch（ブランチ） | main |
| Baseline Commit（基準コミット） | 98a2a67d19146ea24dd4a5a9f3a5642f2e21c04b |
| Previous Review Commit（前回反映コミット） | 92b0d42 |
| Follow-up Commit SHA（差し戻し反映コミット） | 9965d36915e7a8df588a2bbef08ac6a7cd6fb9a8 |
| Owner（管理者） | Takashi Oikawa |
| Reviewer（レビュアー） | GEM_REVIEWER_PERSONA |
| Related Documents（関連文書） | README.md / SKILL.md / LICENSE-DOCS / docs/design/01_REQUEST_DEFINITION.md / docs/design/02_REQUIREMENTS_DEFINITION.md / docs/design/03_DATA_AND_SECURITY_DESIGN.md / docs/design/04_UI_AND_FLOW_DESIGN.md / docs/design/05_ARCHITECTURE_DESIGN.md / docs/design/06_OPERATION_AND_HANDOFF.md / NOTICE |

---

## 1. Purpose

本文書は、2026-09-06 の設計レビュー、再回答、検証結果、採用判断、未解決事項を GitHub 管理対象として保存する。

正本設計文書への反映内容は各設計文書を正とする。本文書はレビュー記録であり、法的助言ではない。

---

## 2. Review Scope and Decision

| 項目 | 内容 |
|---|---|
| 対象 | RV-001〜RV-012 の合意済み内容を正本設計文書へ反映する |
| 実施範囲 | 文書修正のみ |
| コード凍結 | 現行プロトタイプは凍結を維持する。`SKILL.md` へ一般的な改修例外規定は追加しない |
| 設計側の訂正 | project-bootstrap の全面導入は行わない。履歴保存の考え方だけを利用する |
| commit / push | 本記録作成時点で未実施。差分確認後にプロジェクトオーナーが判断する |

---

## 3. Reviewer Corrections

レビュー側が訂正した点:

1. RV-004 の検査 [5] の修正対象を、テキストと JSON の情報差として整理し直した。指摘は RV-004a と RV-004b に分割した。
2. RV-007 について、music21 ソフトウェア本体の BSD-3-Clause 義務を corpus 内エンコーディングへ一律適用する推論を採らない。

---

## 4. Findings and Final Judgments

| ID | 最終判定 | 内容 | 反映先 |
|---|---|---|---|
| RV-001 | Adopted | ライセンスは分離構成を正とする。ソースコードは MIT（`LICENSE-CODE`）、設計文書・README・作業ルールは CC BY-NC-SA 4.0（`LICENSE-DOCS`）。`LICENSE` は旧ライセンス記録として残置。テスト素材は両区分に自動含めない。03 / 06 のライセンス分離 TBD は commit `77ea651`（2026-06-22）を根拠に Resolved | README.md / LICENSE-DOCS / 03_DATA_AND_SECURITY_DESIGN.md / 04_UI_AND_FLOW_DESIGN.md / 06_OPERATION_AND_HANDOFF.md |
| RV-002 | Adopted | 検査 [3][4] は第 1 パートだけを参照する。現行 CLI 出力にこの制約の注記はない。凍結中の受容済み制約とする。出力注記の実装は将来実装要求へ移す。全パート対応 TBD と混同しない | 02_REQUIREMENTS_DEFINITION.md / 05_ARCHITECTURE_DESIGN.md / 06_OPERATION_AND_HANDOFF.md |
| RV-003 | Adopted | リハーサルマーク 0 件は異常でも `[WARN]` でもない。レベルタグを付けない確認用注記とする。`[INFO]` タグが出るとは記載しない | 02_REQUIREMENTS_DEFINITION.md |
| RV-004 | Split | 検査 [5] だけを単一の修正対象とせず、RV-004a と RV-004b へ分割した | 本記録 / 02_REQUIREMENTS_DEFINITION.md |
| RV-004a | Adopted | 検査 [1][7] の注記は現行テキスト出力だけにあり、JSON には存在しない | 02_REQUIREMENTS_DEFINITION.md |
| RV-004b | Adopted | 検査 [5] は JSON では 0 件を含む件数を出すが、テキストでは 0 件時に件数行を出さない | 01_REQUEST_DEFINITION.md / 02_REQUIREMENTS_DEFINITION.md |
| RV-005 | Adopted | `--json` 指定時でも、入力パース失敗時は現行実装が JSON ではなくプレーンテキスト `[FATAL]` を標準出力へ出し、終了コード 1 で終了する。将来の JSON エラー形式は未確定 | 02_REQUIREMENTS_DEFINITION.md / 04_UI_AND_FLOW_DESIGN.md / 05_ARCHITECTURE_DESIGN.md |
| RV-006 | Adopted | TBD-ID・SC-ID の文書横断衝突を解消する。TBD 参照は文書名付きとする。NOTICE などの誤参照を修正する。04 の操作シナリオ ID を `FLOW-001`〜`FLOW-005` へ変更する | 01_REQUEST_DEFINITION.md / 02_REQUIREMENTS_DEFINITION.md / 03_DATA_AND_SECURITY_DESIGN.md / 04_UI_AND_FLOW_DESIGN.md / 05_ARCHITECTURE_DESIGN.md / 06_OPERATION_AND_HANDOFF.md / NOTICE |
| RV-007 | Adopted | music21 ソフトウェア本体の BSD-3-Clause と、corpus 内エンコーディングの個別利用条件を分ける。corpus へ BSD が当然に適用されるとは記載しない | NOTICE / 05_ARCHITECTURE_DESIGN.md |
| RV-008 | Adopted | README の Version と Change History の不一致を、Git 履歴で確認できる範囲に限定して解消する。存在しない標準文書へのリンクを削除する。CLI プロジェクトに不要なスクリーンショット運用記述を削除する | README.md |
| RV-009 | Adopted | FR-006 に対応する成功基準が欠落していたため SC-009 を追加する。和音音数の最頻値が同率の場合の正式ルールは未定義である。現行実装は最初に出現した候補に依存し、正式ルールは将来実装要求 FUT-005 として残す | 01_REQUEST_DEFINITION.md / 02_REQUIREMENTS_DEFINITION.md / README.md / 06_OPERATION_AND_HANDOFF.md |
| RV-010 | Adopted | 現行プロトタイプは凍結を維持する。文書修正は凍結対象ではない。HO-002 は現行実装で完了済みと読める表現を改める。2026-06-28 の限定保守について、承認者・承認経緯は確認不能として扱い、推測で補完しない | 02_REQUIREMENTS_DEFINITION.md / 05_ARCHITECTURE_DESIGN.md / 06_OPERATION_AND_HANDOFF.md |
| RV-011 | Adopted | FR-001〜FR-012 は現行プロトタイプの実際の動作を記載する。将来実装で実現したい仕様は独立した将来実装要求へ分離する | 02_REQUIREMENTS_DEFINITION.md |
| RV-012 | Adopted / Open remainder | 楽曲・作曲物の権利、MusicXML エンコーディングの権利、派生成果物、公開 GitHub からの再配布範囲を分離して確認する。パブリックドメイン楽譜なら MusicXML も公開可能とは読ませない。準拠法域および公開可否の最終判断は未解決のまま残す | 01_REQUEST_DEFINITION.md / 03_DATA_AND_SECURITY_DESIGN.md / NOTICE / SKILL.md / LICENSE-DOCS |

RV-012 のうち、最終判断責任者・判断期限・暫定公開継続は §11 SB-002 で確定した。公開可否の法的確定、MusicXML エンコーディングの個別利用条件、準拠法域は未解決のまま残す。

JSON との情報量統一、JSON 形式の FATAL、検査 [5] の 0 件表示統一は将来実装要求として分離した。フィールド名や JSON エラー構造は今回確定していない。

---

## 5. Documents Changed in This Review Response

次の文書を変更した。

- `README.md`
- `SKILL.md`
- `LICENSE-DOCS`
- `docs/design/01_REQUEST_DEFINITION.md`
- `docs/design/02_REQUIREMENTS_DEFINITION.md`
- `docs/design/03_DATA_AND_SECURITY_DESIGN.md`
- `docs/design/04_UI_AND_FLOW_DESIGN.md`
- `docs/design/05_ARCHITECTURE_DESIGN.md`
- `docs/design/06_OPERATION_AND_HANDOFF.md`
- `NOTICE`
- `docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md`（新規）

---

## 6. Documents and Artifacts Not Changed

次は変更していない。

- `prototype/src/verify_score.py`
- `prototype/tests/` 配下の全ファイル
- `prototype/requirements.txt`
- `LICENSE`
- `LICENSE-CODE`
- その他のソースコード、依存関係、Git 設定

コード変更はなく、commit および push は本記録作成時点で実施していない。

---

## 7. Facts Confirmed by Execution During Review

次は設計レビュー過程で確認済みの事実である。本文書修正の後にプロトタイプを再実行した結果ではない。

- 3 件のテスト素材の実行は終了コード 0 である
- `--json` 指定中のパース失敗は、JSON ではなくプレーンテキストの `[FATAL]` になる
- テスト素材と music21 corpus の音列が一致し、現行 3 ファイルが music21 corpus の BWV 66.6 系データに由来する可能性が高い

由来する可能性が高いことは技術的確認であり、権利者・利用条件・公開可否の確定ではない。

---

## 8. Unresolved Items

| 項目 | 追跡先 |
|---|---|
| テスト素材エンコーディングの個別利用条件 | `05_ARCHITECTURE_DESIGN.md` TBD-005 / `NOTICE` |
| 世界向け再配布可否の法的確定 | `03_DATA_AND_SECURITY_DESIGN.md` TBD-005 |
| 準拠法域 | `03_DATA_AND_SECURITY_DESIGN.md` TBD-005 |
| 2026-06-28 限定保守の明示的な承認記録 | `06_OPERATION_AND_HANDOFF.md` §5.2。確認できる記録からは特定できない |
| 将来実装での JSON 仕様（情報量統一、JSON エラー形式、フィールド名） | `02_REQUIREMENTS_DEFINITION.md` §5.7 |
| プロトタイプを再利用・置換・廃止する判断 | `01_REQUEST_DEFINITION.md` TBD-002 / `SKILL.md` §7（本文書ではコードを変更しない） |
| 本実装比較の CLI フロー詳細 | `04_UI_AND_FLOW_DESIGN.md` TBD-001 |
| 本実装比較のアーキテクチャ詳細 | `05_ARCHITECTURE_DESIGN.md` TBD-001 |
| 本実装比較結果ファイルの保存先・廃棄方針 | `03_DATA_AND_SECURITY_DESIGN.md` TBD-002 |

最終判断責任者（Takashi Oikawa）、判断期限（2026-09-06）、暫定公開継続は未解決ではない。複数 MusicXML 比較を本実装対象にするか自体も未解決ではない。

---

## 9. Disclaimer

本記録は法的助言ではない。テスト素材の公開可能性、再配布の許否、準拠法域、権利者の確定を述べない。

---

## 10. Change History

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-09-06 | 初版。RV-001〜RV-012 の最終判定、文書反映、未解決事項を記録。RV-006 / RV-008 / RV-009 は原レビュー定義に合わせて記録 | Takashi Oikawa |
| 0.2 | 2026-09-06 | Status を Changes Requested へ変更。Reviewer を GEM_REVIEWER_PERSONA に統一。差し戻し事項と設計判断結果を記録。差し戻し反映コミットは Pending | Takashi Oikawa |

---

## 11. Send-back Items and Design Judgments（差し戻し事項・設計判断）

Reviewer: `GEM_REVIEWER_PERSONA`

前回反映コミット: `92b0d42`（文書のみ。プロトタイプ凍結維持）

差し戻し反映コミット: `9965d36915e7a8df588a2bbef08ac6a7cd6fb9a8`

設計文書本体（README / 01〜06）の Status は `Draft` のまま維持する。本レビュー記録の Status `Changes Requested` とは別概念である。

| ID | 差し戻し事項 | 設計判断結果 |
|---|---|---|
| SB-001 | 複数 MusicXML 比較を実装対象にするか自体が TBD-001 として未確定のまま残っていた | 本実装確定スコープとする。対象は複数 MusicXML 入力、正規化、比較可能性判定、差分比較、差分可視化、比較レポート生成。現行プロトタイプは単一 MusicXML 構造検査のまま。未実装と未確定を混同しない。自動修正、自動統合、Web UI、原本 PDF 横並び表示は将来検討事項のまま。`01_REQUEST_DEFINITION.md` TBD-001 および `02_REQUIREMENTS_DEFINITION.md` TBD-001 を Resolved とする |
| SB-002 | 公開中テスト素材について、最終判断責任者・判断期限・暫定措置が未確定のまま残っていた | 暫定公開継続。最終判断責任者: Takashi Oikawa。判断期限: 2026-09-06。判断完了までの暫定措置: 権利確認中・公開可否未確定であることを明示して公開継続。未解決として残すのは MusicXML エンコーディングの個別利用条件、再配布可否の法的確定、準拠法域。法的に公開可能とは断定しない |
| SB-003 | 性能要件で「数秒以内」と「定量基準は規定しない」が併記されていた | 「数秒以内」を削除する。プロトタイプ検証段階では性能の定量的な合否基準を設けない。実行時間は必要に応じて測定対象にできる。本実装段階の性能基準は必要時に別途定義する。`02_REQUIREMENTS_DEFINITION.md` TBD-004 を Resolved とする |
| SB-004 | README の Reviewer が未定、レビュー記録 Status が Reviewed のままだった | README の Reviewer を `GEM_REVIEWER_PERSONA` に統一する。設計文書 Status は `Draft` を維持する。本レビュー記録 Status は `Changes Requested` とする |
