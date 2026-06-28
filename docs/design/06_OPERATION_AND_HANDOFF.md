# Operation and Handoff Design（運用・詳細設計引き継ぎ）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | OPS-001 |
| Version（バージョン） | 0.2 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-06-28 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | README.md / 01_REQUEST_DEFINITION.md / 02_REQUIREMENTS_DEFINITION.md / 03_DATA_AND_SECURITY_DESIGN.md / 04_UI_AND_FLOW_DESIGN.md / 05_ARCHITECTURE_DESIGN.md |

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

本設計書群は、完成版 MusicXML 作成支援システムへ到達するための検証結果・設計判断・未確定事項を整理したプロトタイプ段階の設計ガイドラインである。本文書は**プロトタイプ検証段階**における `verify_score.py`（単一 MusicXML 構造検査の検証実装）の利用手順・確認手順・人間レビュー方針・設計引き継ぎ事項を定義し、実装・運用・引き継ぎフェーズの基準とすることを目的とする。

**完成版MusicXML作成支援システムの本実装段階**（複数 MusicXML 比較、差分可視化、比較レポート生成）への引き継ぎ事項は、本文書 §5.1 および Open Issues で管理する。開発段階の分類は `README.md` §1 Development Stage Classification を参照する。本文書の対象読者は、設計者・実装者・利用者・将来の保守者・プロジェクトオーナーである。

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
| 自動修正・自動統合・Web UI・原本 PDF 横並び画面の運用手順 | 自動修正、自動統合、Web UI、原本 PDF 横並び画面は、現時点で定義する本実装段階には含めず、将来検討事項として扱う（`README.md` §1 参照） |
| MuseScore 等の外部ツール操作手順 | 外部ツールの操作は対象外 |

---

## 4. Assumptions（前提条件）

本文書の内容が成立するために必要な前提は `01_REQUEST_DEFINITION.md` §4 を継承する。以下は運用・引き継ぎフェーズで追加する前提を示す。

**利用環境**

- Python 3.x が動作するローカル環境（macOS / Linux）
- Git リポジトリをローカルにクローン済み

**Prototype の位置づけ**

- `verify_score.py` は技術検証用プロトタイプであり、正式完成版ではない
- **`[WARN]` / `[ANOMALY]` が 0 件であっても、MusicXML の完全無欠を保証しない**
- 最終的な正確性の担保は原本 PDF との人間による目視照合で行う

**既知の限界（Known Limitations）**

| 限界 | 内容 |
|---|---|
| 音高正誤の自動判定不可 | MusicXML のみでは確定できない |
| [3][4] は第 1 パートのみ参照 | 他パートの調号・拍子/テンポ変化は検出されない |
| 和音・パート不一致の正解断定不可 | 原本 PDF 照合が必要 |
| タイ・スラー・連符・装飾音 | プロトタイプ検証段階の検査スコープ外 |

---

## 5. Definition Details（定義内容）

### 5.1 Handoff Items to Detail Design（詳細設計への引き継ぎ事項）

| ID | Handoff Item（引き継ぎ事項） | Details / Background（詳細・背景） |
|---|---|---|
| HO-001 | 「推測しない・断定しない」原則 | 確定できない結果は `[WARN]`/`[INFO]` で列挙。黙殺・自動補完を行わない |
| HO-002 | [3][4] 第 1 パート限定制約 | 実装コメントと出力注記に明示（TBD-001） |
| HO-003 | 非破壊仕様 | 入力 MusicXML の読み取りのみ。派生ファイル生成禁止 |
| HO-004 | 警告 0 件時の注記 | 「完全無欠を保証しない」注記を Output Formatter に組み込む |
| HO-005 | music21 バージョン固定 | `music21==10.3.0`。変更時は全検査再検証 |
| HO-006 | 著作権・秘密情報の非混入 | テスト素材はパブリックドメイン限定 |

#### プロトタイプ検証項目（技術検証済み [1]〜[8]）

以下の検査項目 `[1]`〜`[8]` は、**正式仕様ではない**。現行 `prototype/src/verify_score.py` で確認済みの**プロトタイプ検証段階の技術検証項目**として記録する。機能要件の詳細は `02_REQUIREMENTS_DEFINITION.md` §5.1、実装上の参照範囲・制約は `05_ARCHITECTURE_DESIGN.md` §5.3 を参照する。

| ID | 検証項目 | 概要 |
|---|---|---|
| [1] | 移調楽器テーブル | 各パートの移調楽器情報（有無・半音差・方向）を報告する |
| [2] | 小節長の検算 | 各パートの各小節について、拍子記号に対する音価合計を検算する |
| [3] | 調号 | 第 1 パートから調号を列挙する（参照範囲は第 1 パートのみ） |
| [4] | テンポ・拍子イベント | 第 1 パートから拍子記号とテンポ変化を小節番号順に列挙する（参照範囲は第 1 パートのみ） |
| [5] | 未確定要素の列挙 | スコア全体の `Unpitched`（無音高）要素の件数を報告する |
| [6] | リハーサルマークと小節番号の対応 | 全パートからリハーサルマークを収集し、小節番号との対応を出力する |
| [7] | 和音の音数チェック | 各パートの和音について構成音数を集計・報告する |
| [8] | パート間小節数整合チェック | 各パートの小節数を比較し、一致・不一致を報告する |

### 5.2 Implementation Constraints and Notes（実装時の注意点・制約）

| 制約 | 内容 |
|---|---|
| 入力は単一ファイルのみ | 複数ファイル一括処理はプロトタイプ検証段階のスコープ外 |
| 出力は標準出力のみ | ファイル出力は利用者がリダイレクト |
| 終了コード | パース成功: 0、パース失敗: 1 |
| 非破壊 | 入力 MusicXML を変更・上書きしない |
| 派生 MusicXML 禁止 | 修正済み MusicXML を出力しない |
| 依存ライブラリ | `music21==10.3.0` に固定 |

#### プロトタイプ保守履歴（2026-06-28）

| 項目 | 内容 |
|---|---|
| 日付 | 2026-06-28 |
| 理由 | レビュアー指摘に基づくプロトタイプ保守 |
| 対象 | `prototype/src/verify_score.py` |
| 内容 | アウフタクト判定の誤判定リスク低減 / 空パート入力時のクラッシュ防止 / テンポ表示の None 安全化 / 和音処理の可読性改善 |
| 位置づけ | 正式実装化ではない。技術検証用プロトタイプの検証継続性を保つための限定修正 |

#### 将来課題（Prototype 実装）

- 人間可読出力と JSON コレクタの二重実装は将来統合候補である。現時点では全面統合しない。
- Web UI 化する場合は `load(path)` に許可ディレクトリ検証を追加する。
- 現時点の CLI ローカル実行では path 検証強化は本修正対象外とする。

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

ビジネス観点での成功基準は `01_REQUEST_DEFINITION.md` §5.5 に記載する。

| Type（種別） | Policy / Criteria（方針・基準） |
|---|---|
| Unit Test（単体テスト） | プロトタイプ検証段階では正式な単体テストフレームワークを整備しない。パブリックドメイン素材で手動確認 |
| Integration Test（結合テスト） | `verify_score.py` を実際に実行し、検査 [1]〜[8] の出力・終了コードを目視確認 |
| System Test（システムテスト） | 正常系（警告あり・なし）と異常系（パース失敗）を手動確認 |
| Acceptance Test（受け入れテスト） | SC-001〜SC-008 を満たすこと。HC-001〜HC-005 の「判定しないこと」を出力で確認 |

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
| テスト素材 | `prototype/tests/` はパブリックドメインのみ |
| 著作権 | 著作権保護楽譜をリポジトリへ登録しない |
| 秘密情報 | API キー・トークン・個人情報をソース・Git・出力に含めない |
| 定期メンテナンス | プロトタイプ検証段階では対象外 |
| データ保持 | score-reader は出力ファイルを生成しない。保存期間は利用者に委ねる |
| ライセンス | score-reader 本体は CC BY-NC-SA 4.0（LICENSE 参照） |

---

## 6. Open Issues（未決事項）

| ID | Open Issue（未決事項） | Owner（担当者） | Due Date（期限） | Status（ステータス） |
|---|---|---|---|---|
| TBD-001 | 検査 [3][4] 全パート対応時の運用・テスト手順更新 | Takashi Oikawa | 未定 | Open |
| TBD-002 | `[WARN]`/`[ANOMALY]` 発生パターンのナレッジ化 | Takashi Oikawa | 未定 | Open |
| TBD-003 | 将来検討事項の本番運用手順（デプロイ・監視等） | Takashi Oikawa | 未定 | Open |
| TBD-004 | ソースコード用と設計文書用ライセンスの分離 | Takashi Oikawa | 未定 | Open |
| TBD-005 | Windows 環境での動作確認と手順書更新 | Takashi Oikawa | 未定 | Open |

---

## 7. Handoff to Detail Design（詳細設計への引き継ぎ）

§5.1 から実装担当者・将来の保守者が最初に確認すべき最重要事項:

1. **「推測しない・断定しない」原則は変更しない**（HO-001）
2. **「完全無欠を保証しない」注記は省略しない**（HO-004）
3. **著作権・秘密情報の非混入を設計レベルで保持する**（HO-006）

---

## 8. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-09 | 初版作成 | Takashi Oikawa |
| 0.2 | 2026-06-28 | 正本記入・開発段階分類表記統一・将来検討事項表記統一 | Takashi Oikawa |
