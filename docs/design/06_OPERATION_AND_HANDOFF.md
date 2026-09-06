# Operation and Handoff Design（運用・詳細設計引き継ぎ）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | OPS-001 |
| Version（バージョン） | 0.3.4 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-09-06 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | README.md / 01_REQUEST_DEFINITION.md / 02_REQUIREMENTS_DEFINITION.md / 03_DATA_AND_SECURITY_DESIGN.md / 04_UI_AND_FLOW_DESIGN.md / 05_ARCHITECTURE_DESIGN.md / docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md / docs/reviews/2026-09-06_SCORE_READER_CROSS_DOCUMENT_REVIEW.md |

---

## Table of Contents（目次）

1. [Purpose（目的）](#1-purpose目的)
2. [Scope（対象範囲）](#2-scope対象範囲)
3. [Out of Scope（対象外範囲）](#3-out-of-scope対象外範囲)
4. [Assumptions（前提条件）](#4-assumptions前提条件)
5. [Definition Details（定義内容）](#5-definition-details定義内容)
6. [Open Issues（未決事項）](#6-open-issues未決事項)
7. [Handoff to Detail Design（詳細設計への引き継ぎ）](#7-handoff-to-detail-design詳細設計への引き継ぎ)
8. [Change History（変更履歴）](#8-change-history変更履歴)

---

## 1. Purpose（目的）

本文書は**プロトタイプ検証段階**における `verify_score.py`（単一 MusicXML 構造検査の検証実装）の利用手順・確認手順・人間レビュー方針、および将来の開発者・保守者への引き継ぎ事項を定義し、実装・運用・引き継ぎフェーズの基準とすることを目的とする。

引き継ぎ思想は、「機械にできること」「機械では確定できないこと」「人間が判断すべきこと」の境界判断を将来の開発者・保守者へ渡すことである。全体思想は `README.md`、開発目的の分類は `01_REQUEST_DEFINITION.md` §1 を参照する。

開発段階の分類は `README.md` §1 Development Stage Classification を参照する。現行プロトタイプは凍結中である。完成版MusicXML作成支援システムの本実装段階（確定スコープ: 複数 MusicXML 入力、正規化、比較可能性判定、差分比較、差分可視化、比較レポート生成）への引き継ぎ事項は、本文書 §5.1 および Open Issues で管理する。比較機能の実装可否は確定済みである。本文書の対象読者は、設計者・実装者・利用者・将来の保守者・プロジェクトオーナーである。

---

## 2. Scope（対象範囲）

| 対象 | 内容 |
|---|---|
| 運用スコープ | ローカル環境での score-reader **プロトタイプ検証段階**の実行・確認・人間レビュー |
| 利用手順 | 環境構築・入力準備・実行・出力確認・人間レビュー・エラー対処 |
| データ取り扱い | 著作権確認・テスト素材管理・秘密情報の非混入 |
| 設計引き継ぎ | 設計意図・アーキテクチャ制約・既知の限界の記録 |
| テスト・受け入れ | プロトタイプ検証段階での動作確認方針 |

---

## 3. Out of Scope（対象外範囲）

| 対象外項目 | 理由 |
|---|---|
| 本番サービスのデプロイ・リリース手順 | プロトタイプ検証段階を対象とする |
| クラウド・コンテナ環境での運用 | ローカル実行ツール |
| 監視・アラート・インシデント対応 | ローカル実行ツール |
| 自動修正・自動統合・Web UI の運用手順 | 将来検討事項（`README.md` §1 Development Stage Classification 参照） |
| 原本 PDF 横並び画面の運用手順 | 本リポジトリの対象外。本リポジトリでは設計・実装方針を定義しない。人間が MuseScore 等を使用して原本 PDF と目視照合する既存運用は維持する（`README.md` §1 Development Stage Classification 参照） |
| MuseScore 等の外部ツール操作手順 | 外部ツールの操作は対象外 |

---

## 4. Assumptions（前提条件）

本文書の内容が成立するために必要な前提は `01_REQUEST_DEFINITION.md` §4 を継承する。以下は運用・引き継ぎフェーズで追加する前提を示す。

**利用環境**

- macOS 上で動作する Python 3.x のローカル環境。特定の macOS バージョンは固定しない。Windows および Linux の動作保証・動作検証は対象外
- Git リポジトリをローカルにクローン済み

**Prototype の位置づけ**

- `verify_score.py` は技術検証用プロトタイプであり、正式完成版ではない
- 現行プロトタイプは凍結中である
- **`[WARN]` / `[ANOMALY]` が 0 件であっても、MusicXML の完全無欠を保証しない**
- 最終的な正確性の担保は原本 PDF との人間による目視照合で行う

**既知の限界（Known Limitations）**

| 限界 | 内容 |
|---|---|
| 音高正誤の自動判定不可 | MusicXML のみでは確定できない |
| [3][4] は第 1 パートのみ参照 | 他パートの調号・拍子/テンポ変化は検出されない。現行 CLI はこの制約の注記を出力しない |
| 和音・パート不一致の正解断定不可 | 原本 PDF 照合が必要 |
| タイ・スラー・連符・装飾音 | プロトタイプ検証段階の検査スコープ外 |
| `--json` 時のパース失敗 | 現行は JSON ではなくプレーンテキスト `[FATAL]` |

---

## 5. Definition Details（定義内容）

### 5.1 Handoff Items to Detail Design（詳細設計への引き継ぎ事項）

将来の開発者・保守者へ渡す引き継ぎ事項を示す。

| ID | Handoff Item（引き継ぎ事項） | Details / Background（詳細・背景） |
|---|---|---|
| HO-001 | 「推測しない・断定しない」原則 | 確定できない結果は `[WARN]`/`[INFO]` で列挙。黙殺・自動補完を行わない |
| HO-002 | [3][4] 第 1 パート限定制約 | 現行実装の参照範囲は第 1 パートのみ。現行 CLI は制約注記を出力しない。凍結中はこの欠落を受容する。将来実装時に出力注記を追加する（`02_REQUIREMENTS_DEFINITION.md` §5.7 FUT-004）。全パート対応の採用判断は `02_REQUIREMENTS_DEFINITION.md` TBD-002（親）。実装方針は `05_ARCHITECTURE_DESIGN.md` TBD-002。運用・テスト手順は本文書 TBD-001。現行実装で注記追加まで完了済みとは扱わない |
| HO-003 | 非破壊仕様 | 入力 MusicXML の読み取りのみ。派生ファイル生成禁止 |
| HO-004 | 警告 0 件時の注記 | 「完全無欠を保証しない」注記を Output Formatter に組み込む |
| HO-005 | music21 バージョン固定 | `music21==10.3.0`。変更時は全検査再検証 |
| HO-006 | 著作権・秘密情報の非混入 | テスト素材は楽曲の権利、MusicXML エンコーディングの権利、加工・再配布条件を分けて確認する。現行公開中素材は権利確認中であり、公開可否は法的に未確定である |
| HO-007 | 本実装確定スコープ | 複数 MusicXML 入力、正規化、比較可能性判定、差分比較、差分可視化、比較レポート生成。未実装であり、未確定ではない。現行プロトタイプは単一 MusicXML 構造検査のまま凍結する。自動修正、自動統合、Web UI は将来検討事項。原本 PDF 横並び表示は本リポジトリの対象外であり、本リポジトリでは設計・実装方針を定義しない。人間が MuseScore 等を使用して原本 PDF と目視照合する既存運用は維持する |
| HO-008 | テスト素材公開の確定事項と未解決事項 | 最終判断責任者: Takashi Oikawa。公開判断の固定期限は設けない。暫定措置: 権利確認中である旨を明示して公開継続。未解決: MusicXML エンコーディングの個別利用条件、再配布可否の法的確定、準拠法域（`03_DATA_AND_SECURITY_DESIGN.md` TBD-005）。技術的由来は `05_ARCHITECTURE_DESIGN.md` TBD-005 |
| HO-009 | 性能の定量基準 | プロトタイプ検証段階では性能の定量的な合否基準を設けない。実行時間は必要に応じて測定対象にできる。本実装段階の性能基準は、必要時に別途定義する |

#### プロトタイプ検証項目（技術検証済み [1]〜[8]）

以下の検査項目 `[1]`〜`[8]` は、**正式仕様ではない**。現行 `prototype/src/verify_score.py` で確認済みの**プロトタイプ検証段階の技術検証項目**として記録する。機能要件の詳細は `02_REQUIREMENTS_DEFINITION.md` §5.1、実装上の参照範囲・制約は `05_ARCHITECTURE_DESIGN.md` §5.3 を参照する。

| ID | 検証項目 | 概要 |
|---|---|---|
| [1] | 移調楽器テーブル | 各パートの移調楽器情報（有無・半音差・方向）を報告する |
| [2] | 小節長の検算 | 各パートの各小節について、拍子記号に対する音価合計を検算する |
| [3] | 調号 | 第 1 パートから調号を列挙する（参照範囲は第 1 パートのみ） |
| [4] | テンポ・拍子イベント | 第 1 パートから拍子記号とテンポ変化を小節番号順に列挙する（参照範囲は第 1 パートのみ） |
| [5] | Unpitched（無音高）要素の報告 | スコア全体の `Unpitched`（無音高）要素の件数を報告する |
| [6] | リハーサルマークと小節番号の対応 | 全パートからリハーサルマークを収集し、小節番号との対応を出力する |
| [7] | 和音の音数チェック | 各パートの和音について構成音数を集計・報告する |
| [8] | パート間小節数整合チェック | 各パートの小節数を比較し、一致・不一致を報告する |

### 5.2 Implementation Constraints and Notes（実装時の注意点・制約）

| 制約 | 内容 |
|---|---|
| 入力は単一ファイルのみ | 複数ファイル一括処理は現行プロトタイプのスコープ外。本実装確定スコープは複数 MusicXML 入力を含む（HO-007） |
| 出力は標準出力のみ | ファイル出力は利用者がリダイレクト |
| 終了コード | パース成功: 0、パース失敗: 1 |
| 非破壊 | 入力 MusicXML を変更・上書きしない |
| 派生 MusicXML 禁止 | 修正済み MusicXML を出力しない |
| 依存ライブラリ | `music21==10.3.0` に固定 |
| コード凍結 | 現行プロトタイプは凍結中である。設計文書の更新・検証は継続する |
| 性能 | プロトタイプ検証段階では性能の定量的な合否基準を設けない（HO-009） |

#### プロトタイプ保守履歴（2026-06-28）

| 項目 | 内容 |
|---|---|
| 日付 | 2026-06-28 |
| 理由 | レビュアー指摘に基づくプロトタイプ保守 |
| 対象 | `prototype/src/verify_score.py` |
| 内容 | アウフタクト判定の誤判定リスク低減 / 空パート入力時のクラッシュ防止 / テンポ表示の None 安全化 / 和音処理の可読性改善 |
| 位置づけ | 正式実装化ではない。技術検証用プロトタイプの検証継続性を保つための限定修正 |
| 承認記録 | 承認者および承認経緯は、確認できる記録からは特定できない。推測で補完しない |

#### 将来課題（Prototype 実装）

- 人間可読出力と JSON コレクタの二重実装は将来統合候補である。現時点では全面統合しない。
- Web UI 化する場合は `load(path)` に許可ディレクトリ検証を追加する。
- 現時点の CLI ローカル実行では path 検証強化は本修正対象外とする。
- テキストと JSON の情報量統一、JSON 形式の FATAL、検査 [5] の 0 件表示統一は `02_REQUIREMENTS_DEFINITION.md` §5.7 を参照する。

#### 環境構築・実行（概要）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r prototype/requirements.txt
cd prototype/src
python3 verify_score.py ../tests/<file>.musicxml
python3 verify_score.py ../tests/<file>.musicxml --json
```

### 5.3 Test Policy and Acceptance Criteria（テスト方針・受け入れ基準）

ビジネス観点での成功基準は `01_REQUEST_DEFINITION.md` §5.5 の SC-001〜SC-009 に記載する。

| Type（種別） | Policy / Criteria（方針・基準） |
|---|---|
| Unit Test（単体テスト） | プロトタイプ検証段階では正式な単体テストフレームワークを整備しない。現行テスト素材で手動確認する。現行テスト素材は権利確認中（暫定公開継続）であり、権利確認済み素材ではない |
| Integration Test（結合テスト） | `verify_score.py` を実際に実行し、検査 [1]〜[8] の出力・終了コードを目視確認 |
| System Test（システムテスト） | 正常系（警告あり・なし）と異常系（パース失敗）を手動確認 |
| Acceptance Test（受け入れテスト） | `01_REQUEST_DEFINITION.md` SC-001〜SC-009 を満たすこと。HC-001〜HC-005 の「判定しないこと」を出力で確認 |

#### 人間レビューチェックリスト（Human Review Checklist）

```
【実行前】
□ 著作権状況・外部 OMR 利用規約を確認した
□ 仮想環境を有効化した

【実行後】
□ [FATAL] / [ANOMALY] / [WARN] を確認した
□ 警告 0 件でも完全無欠を保証しないことを確認した

【原本 PDF 照合】
□ MuseScore 等で MusicXML を開き、原本 PDF と目視照合した
□ 音高・和音・タイ/スラー等は人間が判断した（score-reader は判定しない）
```

### 5.4 Deployment and Release Overview（デプロイ・リリース手順概要）

プロトタイプ検証段階ではクラウドデプロイ・本番リリースは対象外。ローカルセットアップ手順を示す。

| Step（ステップ） | Task（作業内容） | Owner（担当） |
|---|---|---|
| 1 | リポジトリを clone / pull する | 利用者 |
| 2 | 仮想環境を作成・有効化する（初回 / 毎回） | 利用者 |
| 3 | `pip install -r prototype/requirements.txt`（初回） | 利用者 |
| 4 | `cd prototype/src` で検査を実行する | 利用者 |
| 5 | テキスト・JSON 出力を確認する | 利用者 |

### 5.5 Monitoring, Alerts, and Incident Response（監視・アラート・障害対応方針）

| Aspect（観点） | Policy / Procedure（方針・手順） |
|---|---|
| Monitoring Targets and Methods（監視対象・監視方法） | プロトタイプ検証段階では対象外。ローカル実行ツール |
| Alert Recipients and Conditions（アラート通知先・条件） | プロトタイプ検証段階では対象外 |
| Incident Confirmation Procedure（障害確認手順） | `[FATAL]`: 入力形式・破損を確認。OMR 再実行を検討 |
| Recovery Procedure（復旧手順） | `[ANOMALY]`/`[WARN]`: 該当箇所を原本 PDF 照合。music21 不調時は `pip install` 再実行 |
| Escalation（エスカレーション先） | 設計上の問題は Document Owner（Takashi Oikawa）へ報告 |

### 5.6 Operational Constraints and Maintenance（運用上の制約・定期メンテナンス）

| 項目 | 方針 |
|---|---|
| テスト素材 | `prototype/tests/` は楽曲の権利、MusicXML エンコーディングの権利、加工・再配布条件を分けて確認する。現行公開中素材は権利確認中の暫定公開継続 |
| 著作権 | 著作権保護楽譜をリポジトリへ登録しない。公開可否の法的確定は `03_DATA_AND_SECURITY_DESIGN.md` TBD-005。最終判断責任者・暫定措置は HO-008。公開判断の固定期限は設けない |
| 秘密情報 | API キー・トークン・個人情報をソース・Git・出力に含めない |
| 定期メンテナンス | プロトタイプ検証段階では対象外 |
| データ保持 | score-reader は出力ファイルを生成しない。保存期間は利用者に委ねる |
| ライセンス | ソースコードは MIT License（`LICENSE-CODE`）。設計文書・README・作業ルールは CC BY-NC-SA 4.0（`LICENSE-DOCS`）。`LICENSE` は旧ライセンス記録。テスト素材は両区分に自動含めない |

---

## 6. Open Issues（未決事項）

| ID | Open Issue（未決事項） | Owner（担当者） | Due Date（期限） | Status（ステータス） |
|---|---|---|---|---|
| TBD-001 | `02_REQUIREMENTS_DEFINITION.md` TBD-002 および `05_ARCHITECTURE_DESIGN.md` TBD-002 に依存する子項目。全パート対応の採用判断と実装方針の確定後に、運用・テスト手順を定義する。FUT-004（制約注記）とは別件 | Takashi Oikawa | 未定 | Open |
| TBD-002 | `[WARN]`/`[ANOMALY]` 発生パターンのナレッジ化 | Takashi Oikawa | 未定 | Open |
| TBD-003 | 将来検討事項の本番運用手順（デプロイ・監視等） | Takashi Oikawa | 未定 | Open |

テスト素材の未解決権利事項は `03_DATA_AND_SECURITY_DESIGN.md` TBD-005、技術的由来は `05_ARCHITECTURE_DESIGN.md` TBD-005 を参照する。最終判断責任者・暫定公開継続は `03_DATA_AND_SECURITY_DESIGN.md` で確定済みである。公開判断の固定期限は設けない。

### Resolved Issues（解決済み事項）

| ID | Resolved Issue（解決済み事項） | Resolution（解決内容） | Status（ステータス） |
|---|---|---|---|
| TBD-004 | ソースコード用と設計文書用ライセンスの分離 | 2026-06-22 の git commit `77ea651` で分離構成を決定した。ソースコードは MIT（`LICENSE-CODE`）、設計文書・README・作業ルールは CC BY-NC-SA 4.0（`LICENSE-DOCS`）。`LICENSE` は旧ライセンス記録として残置。テスト素材は両区分に自動含めない。 | Resolved |

---

## 7. Handoff to Detail Design（詳細設計への引き継ぎ）

将来の開発者・保守者が最初に確認すべき最重要事項（§5.1）:

1. **「推測しない・断定しない」原則は変更しない**（HO-001）
2. **「完全無欠を保証しない」注記は省略しない**（HO-004）
3. **著作権・秘密情報の非混入を設計レベルで保持する**（HO-006）
4. **現行プロトタイプの受容済み制約と将来改善要求を混同しない**（HO-002）。凍結中は制約注記の欠落を受容し、将来実装時に注記を追加する。現行実装で完了済みと扱わない
5. **本実装確定スコープを未確定と扱わない**（HO-007）。現行プロトタイプ凍結を維持する
6. **本実装開始条件（権利）**: テスト素材の権利確認は未完了である（HO-008）。本実装を開始する前に、未解決権利事項（MusicXML エンコーディングの個別利用条件、再配布可否の法的確定、準拠法域）を解消するか、暫定公開継続のまま進めるかを Document Owner（Takashi Oikawa）が判断する。公開判断の固定期限は設けない。権利判断が完了するまでの暫定措置は公開継続である
7. **性能の定量基準は現段階では未設定**（HO-009）。根拠のない秒数を合否基準として追加しない

---

## 8. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-09 | 初版作成 | Takashi Oikawa |
| 0.2 | 2026-06-28 | 正本記入・開発段階分類表記統一・将来検討事項表記統一 | Takashi Oikawa |
| 0.3 | 2026-09-06 | 設計レビュー反映。分離ライセンス構成へ修正。HO-002 を現行未完了として記載。SC-001〜SC-009 参照を明示。ライセンス分離 TBD を Resolved へ変更 | Takashi Oikawa |
| 0.3.1 | 2026-09-06 | 設計レビュー差し戻し反映。本実装確定スコープ・権利確認未完了・性能定量基準なしを引き継ぎ事項へ追加。現行プロトタイプ凍結を維持 | Takashi Oikawa |
| 0.3.2 | 2026-09-06 | 文書表現の整理。機械と人間の境界判断を将来の開発者・保守者へ引き継ぐ思想を明示。仕様の追加・変更は行っていない | Takashi Oikawa |
| 0.3.3 | 2026-09-06 | 横断レビュー反映。公開判断の固定期限を廃止。対応環境を macOS 上の Python 3.x に統一。全パート対応運用 TBD の依存を明記 | Takashi Oikawa |
| 0.3.4 | 2026-09-06 | 原本 PDF 横並び画面を将来検討事項から外し、本リポジトリでは設計・実装方針を定義しない対象へ変更。人間が MuseScore 等で原本 PDF と目視照合する既存運用は維持する | Takashi Oikawa |
