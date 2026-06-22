# Operation and Handoff Design（運用・詳細設計引き継ぎ）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | OPS-001 |
| Version（バージョン） | 0.2 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-21 |
| Last Updated（最終更新日） | 2026-06-21 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | README.md / 01_REQUEST_DEFINITION.md / 02_REQUIREMENTS_DEFINITION.md / 03_DATA_AND_SECURITY_DESIGN.md / 04_UI_AND_FLOW_DESIGN.md / 05_ARCHITECTURE_DESIGN.md / legacy/SCORE_READER_BASIC_DESIGN.md / legacy/MULTI_OMR_BASIC_DESIGN.md |

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

本文書は、score-reader プロトタイプの利用手順・確認手順・人間レビュー方針・設計引き継ぎ事項・既知の限界を定義し、実装・運用・引き継ぎフェーズの基準とすることを目的とする。

score-reader は本番サービスではなく、OMR 出力 MusicXML の内部整合性検査を行う Prototype / 検証支援ツールである。本文書は本番運用手順書としてではなく、**プロトタイプの利用・確認・引き継ぎの設計記録**として位置づける。

本文書の対象読者は、設計者・実装者・利用者・将来の保守者・プロジェクトオーナーである。

---

## 2. Scope（対象範囲）

| 対象 | 内容 |
|---|---|
| 運用スコープ | ローカル環境での score-reader プロトタイプ実行・確認・人間レビュー |
| 利用手順 | 環境構築・入力準備・実行・出力確認・人間レビュー・エラー対処 |
| データ取り扱い | 著作権確認・テスト素材管理・秘密情報の非混入 |
| 設計引き継ぎ | 設計意図・アーキテクチャ制約・既知の限界・拡張ポイントの記録と引き継ぎ |
| テスト・受け入れ | プロトタイプ段階での動作確認方針 |

---

## 3. Out of Scope（対象外範囲）

| 対象外項目 | 理由 |
|---|---|
| 本番サービスのデプロイ・リリース手順 | プロトタイプフェーズを対象とする。本番デプロイは将来フェーズで設計する |
| クラウド・コンテナ環境での運用 | ローカル実行ツールのためプロトタイプフェーズは対象外 |
| 監視・アラート・インシデント対応 | ローカル実行ツールのため対象外 |
| 完全自動化フローの運用手順 | score-reader の設計原則に反する |
| MuseScore 等の外部ツール操作手順 | 既存の外部ツールの操作は本文書の対象外 |

---

## 4. Assumptions（前提条件）

本文書の内容が成立するために必要な前提は `01_REQUEST_DEFINITION.md` §4 を継承する。以下は運用・引き継ぎフェーズで追加する前提を示す。

**利用環境の前提**

- Python 3.x が動作するローカル環境（macOS / Linux）であること
- Git リポジトリ（score-reader）をローカルにクローン済みであること
- インターネット接続（初回の `pip install` 時のみ必要）

**Prototype の位置づけ**

- `verify_score.py`（`prototype/src/`）は技術検証用プロトタイプであり、正式完成版ではない
- 検査結果（`[WARN]`/`[ANOMALY]` の有無）は「確認対象情報」であり、正確性の保証ではない
- **`[WARN]` / `[ANOMALY]` が 0 件であっても、MusicXML の完全無欠を保証しない**
- 最終的な正確性の担保は原本 PDF との人間による目視照合で行う

**既知の限界（Known Limitations）**

| 限界 | 内容 |
|---|---|
| 音高正誤の自動判定不可 | 符頭位置・加線・臨時記号・オクターブ違いは MusicXML のみでは確定できない |
| 調号・テンポ/拍子は第 1 パートのみ参照 | [3][4] 検査は `score.parts[0]` のみ対象。他パートの変化を検出しない |
| 和音正誤の断定不可 | 「何音であるべきか」は推測しない。分布報告のみ行う |
| パート間不一致の正解断定不可 | どのパートが正しいか・どの小節が欠落かは特定しない |
| タイ・スラー・連符・装飾音の検査対象外 | 現プロトタイプの検査スコープ外 |
| 完全無欠の保証なし | `[WARN]`/`[ANOMALY]` 0 件は「検査対象の構造的問題が検出されなかった」ことを意味するにすぎない |
| 本文書の v0.1 日付 | 移行元 Legacy Source（`legacy/SCORE_READER_BASIC_DESIGN.md`）の初版コミット日（2026-06-07）を引き継ぐ |

---

## 5. Definition Details（定義内容）

### 5.1 Handoff Items to Detail Design（詳細設計への引き継ぎ事項）

| ID | Handoff Item（引き継ぎ事項） | Details / Background（詳細・背景） |
|---|---|---|
| HO-001 | 「推測しない・断定しない」設計原則の継承 | 各検査 [1]〜[8] において、確定できない結果は `[WARN]`/`[INFO]` で列挙する。黙殺・自動補完を行わない。将来の検査項目追加時も同原則を維持すること（`02_REQUIREMENTS_DEFINITION.md` §5.2 参照） |
| HO-002 | [3][4] 第 1 パート限定制約の明示 | 調号・テンポ/拍子は `score.parts[0]` のみ参照する制約を実装コメントと出力注記に明示すること。全パート対応は TBD-001 として管理する（`05_ARCHITECTURE_DESIGN.md` §5.3 参照） |
| HO-003 | 非破壊仕様の実装レベルでの保持 | 入力 MusicXML の読み取りのみ許可。書き込み・削除・派生ファイル生成は禁止。将来フェーズでも変更しないこと（`03_DATA_AND_SECURITY_DESIGN.md` §5.3 参照） |
| HO-004 | 警告 0 件時の「完全無欠を保証しない」注記の出力組み込み | Output Formatter において `[WARN]`/`[ANOMALY]` が 0 件でも注記を省略しないこと（`02_REQUIREMENTS_DEFINITION.md` §5.2 参照） |
| HO-005 | music21 バージョン固定の維持 | `music21==10.3.0` を `prototype/requirements.txt` で固定する。バージョンアップ時は全検査項目の再検証を義務付ける（`05_ARCHITECTURE_DESIGN.md` §5.5 参照） |
| HO-006 | 著作権・秘密情報の非混入の継続 | テスト素材はパブリックドメイン限定。API キー・トークン・個人情報をソース・Git・ログ・出力に含めないこと（`03_DATA_AND_SECURITY_DESIGN.md` §5.4 参照） |

### 5.2 Local Execution Procedure and Output Review（ローカル実行手順・出力確認手順）

#### 環境構築（初回のみ）

作業ディレクトリは score-reader リポジトリルートとする。

```bash
# 1. 仮想環境の作成（初回のみ）
python3 -m venv .venv

# 2. 仮想環境の有効化
source .venv/bin/activate

# 3. 依存ライブラリのインストール（初回のみ）
pip install -r prototype/requirements.txt
# → music21==10.3.0 のみがインストールされる
```

#### 実行手順（Local Execution Procedure）

```bash
# 4. prototype/src へ移動
cd prototype/src

# 5-A. テキスト形式で実行（デフォルト）
python3 verify_score.py ../tests/<file>.musicxml

# 5-B. JSON 形式で実行
python3 verify_score.py ../tests/<file>.musicxml --json

# 5-C. JSON をファイルに保存する場合（利用者がリダイレクト）
python3 verify_score.py ../tests/<file>.musicxml --json > result.json
```

#### 入力ファイルの準備（Input Preparation）

| 確認事項 | 内容 |
|---|---|
| 著作権確認 | 対象 MusicXML の著作権状況を確認すること（§5.6 参照） |
| 外部 OMR 実行 | Newzik 等の外部 OMR サービスで楽譜 PDF → MusicXML を取得済みであること |
| ファイルパス | 絶対パスまたは `prototype/src/` からの相対パスで指定する |
| テスト素材 | `prototype/tests/` 配下のパブリックドメイン素材を使用する場合は `../tests/<file>.musicxml` と指定する |

#### 出力確認手順（Output Review Procedure）

| 出力要素 | 確認内容 | 次のアクション |
|---|---|---|
| `[FATAL]` | パース失敗。MusicXML が破損・非対応形式の可能性 | OMR 再実行・MusicXML 形式確認・手動対応を検討する |
| `[ANOMALY]` | 小節長と拍子の構造的不一致 | 該当小節を最優先で原本 PDF と照合する |
| `[WARN]` | 要確認箇所（拍子未確定・リハーサルマーク・和音音数・パート間小節数不一致等） | 警告箇所をリストアップし、原本 PDF と照合する |
| `[INFO]` | 参考情報（単音の和音記譜・無音高要素件数等） | 必要に応じて原本 PDF で確認する |
| 警告・異常がすべて 0 件 | **注意: 完全無欠を保証しない。** 音高・声部・タイ/スラー等は検査対象外 | 原本 PDF との目視照合を省略しない |

#### 実装時の注意点・制約

| 制約 | 内容 |
|---|---|
| 入力は単一ファイルのみ | 複数ファイルの一括処理は現プロトタイプの対象外 |
| 出力は標準出力のみ | ファイル出力は利用者がリダイレクトで対応する |
| 終了コード | パース成功: 0、パース失敗: 1 |
| 依存ライブラリ | `music21==10.3.0` に固定。バージョン変更禁止（HO-005 参照） |

### 5.3 Test Policy and Human Review Checklist（テスト方針・人間レビューチェックリスト）

ビジネス観点での成功基準は `01_REQUEST_DEFINITION.md` §5.5 に記載する。

#### テスト方針

| Type（種別） | Policy / Criteria（方針・基準） |
|---|---|
| Unit Test（単体テスト） | プロトタイプフェーズでは正式な単体テストフレームワークを整備しない。各検査関数の動作はパブリックドメイン素材（`prototype/tests/`）を用いた手動確認で代替する |
| Integration Test（結合テスト） | `verify_score.py` をパブリックドメイン MusicXML ファイルで実際に実行し、各検査 [1]〜[8] の出力・終了コードを目視確認する |
| System Test（システムテスト） | 正常系（パース成功・警告あり・警告なし）と異常系（パース失敗・非対応ファイル）の動作を手動確認する |
| Acceptance Test（受け入れテスト） | `01_REQUEST_DEFINITION.md` §5.5 の SC-001〜SC-008 を満たしていること。HC-001〜HC-005 の「判定しないこと」が出力に含まれていないこと |

#### 人間レビューチェックリスト（Human Review Checklist）

score-reader 実行後、利用者が実施する人間レビューのチェックリストを示す。

```
【実行前チェック】
□ 対象楽譜の著作権状況を確認した（パブリックドメイン or 利用規約確認済み）
□ 外部 OMR サービスの利用規約を確認した（著作権保護楽譜を送信する場合）
□ 仮想環境を有効化した（source .venv/bin/activate）

【実行後チェック: 出力確認】
□ [FATAL] がある場合: OMR 再実行または MusicXML の形式を確認した
□ [ANOMALY] がある場合: 該当小節を最優先の確認対象としてリストアップした
□ [WARN] がある場合: 警告箇所をリストアップし、原本 PDF 照合の優先対象とした
□ [INFO] を参考情報として確認した
□ 警告・異常が 0 件であっても「完全無欠を保証しない」ことを確認した

【人間レビュー: 原本 PDF との照合】
□ MuseScore 等で対象 MusicXML を開いた
□ [ANOMALY] / [WARN] 箇所を中心に原本 PDF と目視照合した
□ 警告なし箇所も必要に応じて原本 PDF と照合した
□ 音高の正誤は人間が原本 PDF を見て判断した（score-reader は判定しない）
□ 和音構成音数の正誤は人間が原本 PDF を見て判断した
□ タイ・スラー・連符・装飾音は人間が原本 PDF を見て確認した
□ 最終的な正確性は原本 PDF との目視照合で担保した

【注意事項の確認】
□ [3][4]（調号・テンポ/拍子）は第 1 パートのみ参照である。他パートの変化は検出されない
□ 複数 OMR の結果が一致しても、正解の保証にはならない
□ 修正後、必要に応じて score-reader を再実行して追加の異常がないか確認した
```

### 5.4 Setup and Verification Procedure（セットアップ・動作確認手順）

クラウドデプロイ・本番リリースはプロトタイプフェーズの対象外。代わりにローカルセットアップと動作確認手順を記載する。

| Step（ステップ） | Task（作業内容） | Owner（担当） |
|---|---|---|
| 1 | リポジトリを git clone する（または最新を git pull で更新する） | 利用者 |
| 2 | `python3 -m venv .venv` で仮想環境を作成する（初回のみ） | 利用者 |
| 3 | `source .venv/bin/activate` で仮想環境を有効化する | 利用者（毎回） |
| 4 | `pip install -r prototype/requirements.txt` で依存ライブラリをインストールする（初回のみ） | 利用者 |
| 5 | `cd prototype/src` で作業ディレクトリに移動する | 利用者 |
| 6 | `python3 verify_score.py ../tests/<パブリックドメイン素材>.musicxml` で動作確認する | 利用者 |
| 7 | 出力に `[FATAL]` がなく、検査結果が出力されることを確認する | 利用者 |
| 8 | `python3 verify_score.py ../tests/<file>.musicxml --json` で JSON 出力を確認する | 利用者 |

### 5.5 Failure and Warning Handling（障害・警告対応方針）

サーバー監視・アラート・インシデント対応はローカル実行ツールのためプロトタイプフェーズでは対象外。代わりに実行時の異常・警告への対処方針を示す。

| Aspect（観点） | Policy / Procedure（方針・手順） |
|---|---|
| Monitoring Targets（監視対象） | 対象外。理由: ローカル実行ツールのためサーバー監視は不要 |
| Alert Recipients（アラート通知） | 対象外。理由: 同上 |
| `[FATAL]`（パース失敗）発生時 | 入力ファイルの形式・破損を確認する。OMR を再実行するか、別の MusicXML ファイルで試みる。終了コード 1 を確認する |
| `[ANOMALY]`（小節長不一致）発生時 | 該当パート・小節番号を確認し、原本 PDF の該当小節を照合する。OMR の誤認識か小節線の扱い差かを人間が判断する |
| `[WARN]` 多発時 | OMR 出力の精度が低い可能性がある。別の OMR サービスで再変換し結果を比較することを検討する |
| 警告・異常が 0 件の場合 | **「完全無欠を保証しない」。** 音高・声部・タイ/スラー等は検査対象外である。原本 PDF 照合を省略しない |
| music21 の動作不良時 | `pip install -r prototype/requirements.txt` を再実行し `music21==10.3.0` が正しくインストールされているか確認する |
| Escalation（エスカレーション） | プロトタイプフェーズでは対象外。設計上の問題は設計者（Takashi Oikawa）に報告する |

### 5.6 Data and License Handling（データ取り扱い・ライセンス方針）

詳細は `03_DATA_AND_SECURITY_DESIGN.md` §5.4〜5.6 に記載する。以下は運用・引き継ぎ観点での要約を示す。

#### 著作権・ライセンスポリシー（Copyright / License Policy）

| 方針 | 内容 |
|---|---|
| テスト素材の制限 | `prototype/tests/` に配置するすべての MusicXML・楽譜素材は**パブリックドメインに限定する** |
| リポジトリへの登録禁止 | 著作権保護された楽譜 PDF・MusicXML・画像を公開リポジトリ（GitHub 等）へ登録しない |
| 外部 OMR サービス利用前の確認 | 外部 OMR サービスへ楽譜を送信する前に、利用規約・プライバシーポリシー・著作権条件を確認する |
| score-reader のライセンス | CC BY-NC-SA 4.0（非商用・継承・帰属。LICENSE ファイル参照）|

#### 秘密情報の取り扱いポリシー（Confidential Data Policy）

| 禁止事項 | 対象 |
|---|---|
| ソースコードへの記載禁止 | API キー・トークン・秘密鍵・パスワード・個人情報 |
| Git 管理対象への記載禁止 | 同上（コメント・設定ファイル・`.env` ファイルを含む） |
| ログ・標準出力への出力禁止 | 同上（検査結果への混入を禁止）|

#### 定期メンテナンス・保持期間

| 項目 | 方針 |
|---|---|
| 定期メンテナンス | プロトタイプフェーズでは対象外 |
| バッチ処理 | なし（1 実行 = 1 ファイルのオンデマンド処理のみ） |
| データ保持期間 | score-reader は出力ファイルを生成しない。利用者がリダイレクト保存した JSON/テキストの保持期間は利用者に委ねる |
| アーカイブ | プロトタイプフェーズでは対象外 |

---

## 6. Open Issues（未決事項）

| ID | Open Issue（未決事項） | Owner（担当者） | Due Date（期限） | Status（ステータス） |
|---|---|---|---|---|
| TBD-001 | 検査項目 [3][4] を第 1 パートから全パート対応へ拡張する場合の運用・テスト手順の更新方針を定義するか。 | Takashi Oikawa | 未定 | Open |
| TBD-002 | プロトタイプ検証で蓄積された `[WARN]`/`[ANOMALY]` 発生パターンをナレッジとして記録・共有する仕組みを整備するか。 | Takashi Oikawa | 未定 | Open |
| TBD-003 | 将来フェーズで本番サービス化する際の、デプロイ・リリース・監視・インシデント対応手順を設計するか。 | Takashi Oikawa | 未定 | Open |
| TBD-004 | 現在の LICENSE（CC BY-NC-SA 4.0）はソフトウェア本体への適用に適さない場合がある。ソースコード用ライセンス（MIT 等）と設計文書用ライセンス（CC BY-NC-SA 4.0）を分離するかを引き継ぎ先で判断するか。 | Takashi Oikawa | 未定 | Open |
| TBD-005 | Windows 環境での動作確認（仮想環境有効化コマンドの差異: `source .venv/bin/activate` → `.venv\Scripts\activate`、パス表記・改行コードの差異等）を実施し、手順書を更新するか。現手順は macOS / Linux 前提。 | Takashi Oikawa | 未定 | Open |

---

## 7. Handoff to Detail Design（詳細設計への引き継ぎ）

§5.1 から実装担当者・将来の保守者が最初に確認すべき最重要事項を3点に絞って示す。

1. **「推測しない・断定しない」原則は変更しない**（HO-001）: 音高・和音・パート正解の自動判定を追加する変更は、本プロジェクトの設計思想に反する。新機能追加時はこの原則との整合を確認すること。

2. **「完全無欠を保証しない」注記は省略しない**（HO-004）: `[WARN]`/`[ANOMALY]` 0 件時でも Output Formatter が注記を出力すること。利用者の誤解防止のために必須の実装である。

3. **著作権・秘密情報の非混入は設計レベルで保持する**（HO-006）: テスト素材・ソースコード・Git 履歴に著作権保護素材・API キー・個人情報が混入しないこと。将来フェーズで外部 API 連携を追加する際は、秘密情報管理方式を先に設計すること。

---

## 8. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-07 | Legacy Source 初版（legacy/SCORE_READER_BASIC_DESIGN.md 初版コミット日を引き継ぐ） | Takashi Oikawa |
| 0.2 | 2026-06-21 | 標準7文書への移行・記入。legacy/SCORE_READER_BASIC_DESIGN.md（初版 2026-06-07）・legacy/MULTI_OMR_BASIC_DESIGN.md（初版 2026-06-04）・01〜05 各設計書・LICENSE ファイルを参照し全セクションを記入 | Takashi Oikawa |
