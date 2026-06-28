# Data and Security Design（データ・セキュリティ設計）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | DATA-001 |
| Version（バージョン） | 0.2 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-06-28 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | README.md / 02_REQUIREMENTS_DEFINITION.md / 05_ARCHITECTURE_DESIGN.md / legacy/MULTI_OMR_BASIC_DESIGN.md / legacy/SCORE_READER_BASIC_DESIGN.md |

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

本設計書群は、完成版 MusicXML 作成支援システムへ到達するための検証結果・設計判断・未確定事項を整理したプロトタイプ段階の設計ガイドラインである。本文書は**プロトタイプ検証段階**における `verify_score.py` が扱うデータの種別・取り扱い方針、および著作権・外部サービス利用・秘密情報に関するセキュリティ設計仕様を定義し、実装・運用フェーズの基準とすることを目的とする。

将来本実装候補（複数 MusicXML 比較、差分可視化、比較レポート生成）における比較データ・レポート出力の取り扱いは、本文書の Open Issues で管理する。セキュリティ要求レベルは `02_REQUIREMENTS_DEFINITION.md` §5.2 に記載する。本文書の対象読者は、設計者・実装者・プロジェクトオーナーである。

---

## 2. Scope（対象範囲）

| 対象 | 内容 |
|---|---|
| 入力データ | score-reader が読み込む MusicXML ファイル |
| 出力データ | 標準出力に出力するテキスト形式・JSON 形式の検査結果 |
| テスト素材 | `prototype/tests/` 配下に配置する検証用 MusicXML |
| 外部 OMR サービス連携データ | 外部 OMR サービスへ送信する楽譜 PDF・画像（score-reader の入力生成過程で発生する） |
| 秘密情報・認証情報 | API キー・トークン・秘密鍵・個人情報の取り扱い方針 |
| 著作権・ライセンス | 楽譜素材および外部サービス利用に関する著作権・ライセンスポリシー |

---

## 3. Out of Scope（対象外範囲）

| 対象外項目 | 理由 |
|---|---|
| データベース設計（テーブル・ER図） | score-reader はデータベースを持たないローカル実行 CLI ツールである |
| ユーザー認証・認可設計 | ローカル実行ツールのためユーザー管理機能を持たない |
| ネットワーク通信設計 | score-reader 自体はネットワーク通信を行わない（外部 OMR サービス連携はツール外の操作） |
| クラウドストレージ・外部ストレージ設計 | プロトタイプ検証段階では外部ストレージを使用しない |
| アクセスログの集中管理 | プロトタイプ検証段階では対象外（TBD-001） |

---

## 4. Assumptions（前提条件）

本文書の内容が成立するために必要な前提は `01_REQUEST_DEFINITION.md` §4 を継承する。以下はデータ・セキュリティ設計フェーズで追加する前提を示す。

- score-reader はデータベースを持たない。データは「入力 MusicXML（読み取り専用）」と「標準出力（テキスト/JSON）」のみで完結する
- OMR 出力 MusicXML は「正解データ」ではなく「確認対象データ」として扱う。score-reader の検査結果も同様に確認対象であり、正確性の保証とは区別する
- 外部 OMR サービスへの楽譜送信は、score-reader の処理スコープ外（利用者が事前に行う操作）であるが、著作権・利用規約の観点から本文書で方針を定める
- 本文書の v0.1 日付は、移行元 Legacy Source（`legacy/MULTI_OMR_BASIC_DESIGN.md`）の初版コミット日（2026-06-04）を引き継ぐ

---

## 5. Definition Details（定義内容）

### 5.1 Entity Definition and ER Diagram（エンティティ定義・ER図）

本文書では ER 図・エンティティ定義は対象外。理由: score-reader はデータベースを持たないローカル実行 CLI ツールであり、データは実行ごとにオンメモリで処理される。

代わりに、score-reader が扱うデータ種別を以下に整理する。

#### Entity List（データ種別一覧）

| Entity Name（データ種別） | Description（説明） |
|---|---|
| 入力 MusicXML | 利用者が指定する検査対象ファイル。読み取り専用・非破壊 |
| 出力テキスト / JSON | 検査結果。標準出力のみ。score-reader はファイルを生成しない |
| テスト素材 MusicXML | `prototype/tests/` 配下。パブリックドメイン楽譜に限定 |
| 楽譜 PDF・画像（外部 OMR 入力） | score-reader の処理スコープ外。著作権・利用規約の確認が必要 |

**OMR 出力 MusicXML の位置づけ**

OMR が出力した MusicXML は「正解データ」ではなく「確認対象データ」である。`[WARN]` / `[ANOMALY]` が 0 件であっても、MusicXML の完全無欠を保証しない。

#### ER Diagram（ER図）

```
（対象外: データベースを持たない CLI ツールのため ER 図なし）
```

### 5.2 Table Definitions（テーブル定義）

本文書ではテーブル定義は対象外。理由: score-reader はデータベースを持たない。代わりに入出力データの仕様を定義する。

#### 入力データ（Input MusicXML）

| 項目 | 内容 |
|---|---|
| 形式 | MusicXML ファイル（`.musicxml` 等、`music21.converter.parse` が対応する形式） |
| 指定方法 | コマンドライン第 1 引数（絶対パス・相対パスいずれも可） |
| 件数 | 1 実行 = 1 ファイル |
| 取り扱い | 読み取り専用。score-reader は入力ファイルを変更・削除・複製しない |
| 著作権 | 利用者が著作権状況を事前に確認する責任を負う（§5.4 参照） |

#### 出力データ（Output: テキスト / JSON）

| 項目 | 内容 |
|---|---|
| 出力先 | 標準出力（stdout）のみ |
| 形式 | 人間可読テキスト（デフォルト）または JSON（`--json` 指定時） |
| ファイル保存 | score-reader は出力ファイルを生成しない。保存は利用者のリダイレクト操作に委ねる |
| 含まれる情報 | 検査結果のみ。個人情報・秘密情報を含めない |
| JSON フィールド | `02_REQUIREMENTS_DEFINITION.md` §5.1 JSON 出力フィールド定義 参照 |

#### テスト素材（Test Data）

| 項目 | 内容 |
|---|---|
| 配置場所 | `prototype/tests/` |
| 著作権条件 | **パブリックドメイン楽譜に限定する**（§5.4 参照） |
| 禁止事項 | 著作権保護された楽譜 PDF・MusicXML・画像をリポジトリに含めない |

### 5.3 Data Access and Role Design（データアクセス権限・ロール設計）

score-reader はシングルユーザーのローカル実行 CLI ツールであり、認証・認可機能を持たない。データアクセス権限はローカルファイルシステムの OS 権限に委ねる。

| Role Name（ロール名） | Accessible Data / Permitted Operations（アクセス可能なデータ / 操作範囲） |
|---|---|
| 利用者（CLI 実行者） | 入力 MusicXML の読み取り（Read only）。標準出力の参照 |
| score-reader プロセス | 入力 MusicXML の読み取りのみ。ファイルの書き込み・削除・派生ファイル生成は禁止 |
| 開発者 | `prototype/tests/` 配下のテスト素材の追加・更新（パブリックドメイン楽譜に限定） |

### 5.4 Personal and Confidential Data Policy（個人情報・機密データの取り扱い方針）

#### 個人情報

score-reader は利用者の個人情報を収集・保存・送信しない。出力（テキスト/JSON）に個人情報を含めない設計とする。

#### 著作権保護データ（Copyright Policy）

| 方針 | 内容 |
|---|---|
| リポジトリへの登録禁止 | 著作権保護された楽譜 PDF・MusicXML・画像・その他楽譜素材を公開リポジトリ（GitHub 等）へ登録しない |
| テスト素材の制限 | `prototype/tests/` 配下に配置するテスト素材は**パブリックドメイン楽譜に限定する** |
| MusicXML メタデータの確認 | 作曲者名・著作権者名等のメタデータが含まれる場合、公開前に除去または公開可否を確認する |
| 利用者の責任 | 入力 MusicXML の著作権状況は、利用者が事前に確認する責任を負う |
| 外部 OMR サービス利用時 | 外部 OMR サービスへ楽譜 PDF・画像を送信する場合は、利用規約・著作権条件を事前に確認する |

#### 秘密情報・認証情報（Confidential Data Policy）

| 禁止事項 | 対象 |
|---|---|
| ソースコードへの記載禁止 | API キー・トークン・秘密鍵・パスワード・個人情報 |
| Git 管理対象への記載禁止 | 同上（`.env`・設定ファイル・コメントを含む） |
| ログ・標準出力への出力禁止 | 同上（検査結果への混入を禁止） |

プロトタイプ検証段階では外部サービス連携を持たないため API キー等は不要である。

#### 外部 OMR サービスデータポリシー

score-reader 自体は外部ネットワーク通信を行わない。入力 MusicXML の生成過程で利用者が外部 OMR サービス（Newzik 等）を利用する場合、利用規約・著作権条件を事前確認し、出力 MusicXML を正解データとして扱わない。

### 5.5 Encryption, Masking, and Logging Policy（暗号化・マスキング・ログ取得方針）

| Type（種別） | Target（対象） | Policy / Method（方式・方針） |
|---|---|---|
| Encryption（暗号化） | 入力 MusicXML・出力データ | 本文書では対象外。理由: ローカル実行ツールであり、OS のファイルシステム保護に委ねる |
| Masking（マスキング） | 秘密情報 | ソースコード・出力・ログに秘密情報を含めないことで対応 |
| Logging（ログ取得） | 実行ログ | プロトタイプ検証段階では対象外。標準出力への検査結果出力のみ（TBD-001） |

**データ保持方針**

| データ種別 | 保持方針 |
|---|---|
| 入力 MusicXML | 利用者のローカル環境で管理。score-reader はコピーを作成しない |
| 出力テキスト / JSON | 標準出力のみ。保存期間は利用者に委ねる |
| テスト素材 | リポジトリに含める場合はパブリックドメインに限定 |

### 5.6 Security Design Specifications（セキュリティ設計仕様）

セキュリティ要求レベルは `02_REQUIREMENTS_DEFINITION.md` §5.2 に記載する。

| Type（種別） | Design Specification（設計仕様） |
|---|---|
| Authentication（認証） | 対象外。理由: ローカル実行ツールであり、ユーザー認証機能を持たない |
| Authorization（認可） | 対象外。理由: ユーザー管理機能を持たない。OS のファイルシステム権限に委ねる |
| Access Control（権限管理） | score-reader プロセスは入力 MusicXML の読み取りのみ許可。書き込み・削除・派生ファイル生成は禁止 |
| Communication（通信） | score-reader 自体はネットワーク通信を行わない |
| Data Storage（データ保存） | ファイルを永続保存しない。入力は読み取り専用、出力は標準出力のみ |
| Data Disposal（データ廃棄） | score-reader が生成するデータはない（標準出力は OS が管理） |
| Personal Data Protection（個人情報保護） | 個人情報を収集・保存・送信しない |

#### セキュリティリスクの整理

| リスク | 対策方針 |
|---|---|
| 著作権保護楽譜のリポジトリ混入 | テスト素材はパブリックドメインのみ許可。レビュー時に確認 |
| 外部 OMR サービスへの著作権楽譜送信 | 送信前に利用者が著作権状況・利用規約を確認 |
| API キー等の秘密情報混入 | プロトタイプ検証段階では外部 API 連携なし。将来検討事項として環境変数管理を検討（TBD-001） |
| OMR 出力の誤信 | 出力に「確認対象データ」「完全無欠を保証しない」旨の注記を含める |

---

## 6. Open Issues（未決事項）

| ID | Open Issue（未決事項） | Owner（担当者） | Due Date（期限） | Status（ステータス） |
|---|---|---|---|---|
| TBD-001 | 将来検討事項で外部 API 連携を実装する場合の API キー・トークン管理方式を設計するか。 | Takashi Oikawa | 未定 | Open |
| TBD-002 | 将来検討事項で複数 MusicXML 比較機能を実装する場合、比較結果ファイルの保存先・廃棄方針を定義するか。 | Takashi Oikawa | 未定 | Open |
| TBD-003 | 外部 OMR サービスの利用規約確認をチェックリスト等で運用化するか。 | Takashi Oikawa | 未定 | Open |
| TBD-004 | ソースコード用と設計文書用のライセンス分離（MIT 等）を検討するか。 | Takashi Oikawa | 未定 | Open |

---

## 7. Handoff to Detail Design（詳細設計への引き継ぎ）

1. **非破壊仕様の徹底**: 入力 MusicXML ファイルを変更・削除・複製しないこと（§5.3 参照）。
2. **秘密情報の混入防止**: API キー・トークンをソースコード・標準出力・ログに含めないこと（TBD-001）。
3. **テスト素材の著作権確認**: `prototype/tests/` 追加前にパブリックドメインであることを確認すること（§5.4 参照）。
4. **OMR 出力の誤信防止**: 検査結果に「確認対象データ」「完全無欠を保証しない」旨の注記を含めること（§5.6 参照）。

---

## 8. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-09 | 初版作成 | Takashi Oikawa |
| 0.2 | 2026-06-28 | legacy/03 を内容抽出元として正本記入・開発段階分類表記統一 | Takashi Oikawa |
