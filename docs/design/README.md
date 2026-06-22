# Design Documents Index（設計書一覧）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | README-001 |
| Version（バージョン） | 0.2 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-21 |
| Last Updated（最終更新日） | 2026-06-21 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | LICENSE / legacy/MULTI_OMR_BASIC_DESIGN.md / legacy/SCORE_READER_BASIC_DESIGN.md |

---

## Table of Contents（目次）

1. [Project Overview（プロジェクト・機能の概要）](#1-project-overviewプロジェクト機能の概要)
2. [Design Documents Index（設計書一覧）](#2-design-documents-index設計書一覧)
3. [Overall Design Policy（設計上の全体方針・前提）](#3-overall-design-policy設計上の全体方針前提)
4. [Glossary（用語集・略語定義）](#4-glossary用語集略語定義)
5. [Document Owners and Reviewers（文書管理者・レビュアー一覧）](#5-document-owners-and-reviewers文書管理者レビュアー一覧)
6. [Change History（変更履歴）](#6-change-history変更履歴)

---

## 1. Project Overview（プロジェクト・機能の概要）

### Design Document Overview（設計書概要）

本ディレクトリは score-reader プロジェクトの設計書群を管理する。

score-reader は **OMR（Optical Music Recognition）出力 MusicXML の内部整合性検査を行う Prototype / 検証支援ツール**である。完成アプリケーションの実装を目的としない。

### Project Position（プロジェクトの位置づけ）

| 項目 | 内容 |
|---|---|
| システム種別 | 独立したローカル実行 CLI ツール（他システムとの連携なし） |
| フェーズ | プロトタイプ・技術検証フェーズ |
| 目的 | OMR 出力の構造的異常・要確認箇所を自動抽出し、人間の確認作業を省力化する |
| 完全自動化 | 目的としない。現技術では音高・音価・声部の正誤を機械的に確定できない |
| 人間確認 | 省略しない。最終的な正確性は原本 PDF との目視照合で担保する |

### Recommended Reading Order（推奨参照順）

設計書を初めて参照する場合は以下の順で読むことを推奨する。

```
README.md（本文書）
  ↓
01_REQUEST_DEFINITION.md   ← 背景・課題・要求・成功基準
  ↓
02_REQUIREMENTS_DEFINITION.md  ← 機能要件・非機能要件・検査項目[1]〜[8]
  ↓
03_DATA_AND_SECURITY_DESIGN.md ← データ取り扱い・著作権・秘密情報
  ↓
04_UI_AND_FLOW_DESIGN.md   ← CLI操作・業務フロー・人間レビューチェックリスト
  ↓
05_ARCHITECTURE_DESIGN.md  ← システム構成・技術スタック・拡張ポイント
  ↓
06_OPERATION_AND_HANDOFF.md ← 利用手順・テスト方針・設計引き継ぎ
```

実装担当者は `06_OPERATION_AND_HANDOFF.md` §5.1 Handoff Items および §7 Handoff を最初に確認すること。

---

## 2. Design Documents Index（設計書一覧）

### Current Status（現在のステータス）

| File（ファイル名） | Document Name（文書名） | Status | Version | Owner |
|---|---|---|---|---|
| [01_REQUEST_DEFINITION.md](./01_REQUEST_DEFINITION.md) | Request Definition（要求定義） | Draft | 0.2 | Takashi Oikawa |
| [02_REQUIREMENTS_DEFINITION.md](./02_REQUIREMENTS_DEFINITION.md) | Requirements Definition（要件定義） | Draft | 0.2 | Takashi Oikawa |
| [03_DATA_AND_SECURITY_DESIGN.md](./03_DATA_AND_SECURITY_DESIGN.md) | Data and Security Design（データ・セキュリティ設計） | Draft | 0.2 | Takashi Oikawa |
| [04_UI_AND_FLOW_DESIGN.md](./04_UI_AND_FLOW_DESIGN.md) | UI and Flow Design（UI・フロー設計） | Draft | 0.2 | Takashi Oikawa |
| [05_ARCHITECTURE_DESIGN.md](./05_ARCHITECTURE_DESIGN.md) | Architecture Design（アーキテクチャ設計） | Draft | 0.2 | Takashi Oikawa |
| [06_OPERATION_AND_HANDOFF.md](./06_OPERATION_AND_HANDOFF.md) | Operation and Handoff Design（運用・詳細設計引き継ぎ） | Draft | 0.2 | Takashi Oikawa |

各文書はすべて **Draft** ステータスであり、プロトタイプ・技術検証フェーズの設計記録として位置づける。

### Legacy Source（参照元 Legacy 文書）

以下の2文書は `legacy/` に保持する。削除済みではなく、上記6文書の記入時の参照元（Legacy Source）として保存している。

| File（ファイル名） | 内容の概要 | 初版コミット日 | 主に移行された設計書 |
|---|---|---|---|
| [legacy/MULTI_OMR_BASIC_DESIGN.md](./legacy/MULTI_OMR_BASIC_DESIGN.md) | OMRサービス概要・精度・複数OMR比較の必要性・完全自動化が困難な技術要因 | 2026-06-04 | 01, 03 |
| [legacy/SCORE_READER_BASIC_DESIGN.md](./legacy/SCORE_READER_BASIC_DESIGN.md) | verify_score.py の入出力仕様・検査項目[1]〜[8]・実行方法・制約・著作権注意 | 2026-06-07 | 02, 04, 05, 06 |

---

## 3. Overall Design Policy（設計上の全体方針・前提）

### Important Premises（重要前提）

以下の前提は、すべての設計書に共通して適用する。個別文書での繰り返し記述を防ぐため、ここにまとめて定義する。

| 前提 | 内容 |
|---|---|
| 完成アプリではない | score-reader はプロトタイプ・検証支援ツールである。正式完成版として扱わない |
| 完全自動化しない | 現技術では音高・音価・声部・タイ/スラー等の正誤を機械的に確定できない |
| 人間確認を省略しない | score-reader の目的は確認対象を絞り込むことであり、原本 PDF との目視照合は必須 |
| 推測しない・断定しない | 確定できない結果は `[WARN]`/`[INFO]` で列挙し、黙殺・自動補完を行わない |
| 警告なし≠正確 | `[WARN]`/`[ANOMALY]` が 0 件でも MusicXML の完全無欠を保証しない |
| OMR 出力は確認対象データ | OMR が生成した MusicXML は「正解データ」ではなく「確認対象データ」である |
| 独立したシステム | score-reader は他のシステムとは無関係の独立したローカル実行ツールである |

### License / Copyright Notes（ライセンス・著作権）

- score-reader のライセンスは **CC BY-NC-SA 4.0**（`LICENSE` ファイル参照）
- **非商用（NonCommercial）**: 商業目的での利用・派生物の配布は禁止
- **継承（ShareAlike）**: 改変・再配布時は同一ライセンス（CC BY-NC-SA 4.0）を適用すること
- **帰属（Attribution）**: 利用・再配布時は原著者（Takashi Oikawa）を表示すること

**著作権保護楽譜の取り扱い**

- 著作権保護された楽譜 PDF・MusicXML・画像を公開リポジトリ（GitHub 等）へ登録しない
- テスト素材（`prototype/tests/`）はパブリックドメイン楽譜に限定する
- 外部 OMR サービスへ楽譜を送信する前に、利用規約・著作権条件を確認する
- API キー・トークン・秘密鍵・個人情報をソース・Git・ログ・出力に含めない

詳細は `03_DATA_AND_SECURITY_DESIGN.md` §5.4 を参照。

### Open Issues Summary（未決事項サマリー）

各設計書の Open Issues のうち、設計書群を横断する主要な未決事項を示す。詳細は各文書の §6 を参照。

| テーマ | 主な関連文書 |
|---|---|
| 複数 MusicXML 比較機能の将来要件化 | 01, 02, 05 |
| 検査項目 [3][4] の全パート対応拡張 | 02, 05, 06 |
| 外部 OMR サービス API 連携の設計 | 03, 05 |
| プロトタイプから正式版への移行基準 | 01, 05 |
| 削減効果概算（§5.5）の実測による検証 | 01 |

---

## 4. Glossary（用語集・略語定義）

| Term / Abbreviation（用語・略語） | Definition（定義） |
|---|---|
| OMR | Optical Music Recognition。楽譜 PDF・画像から MusicXML 等の機械可読形式へ変換する処理 |
| MusicXML | 楽譜を XML 形式で表現した標準フォーマット。OMR の出力形式として利用する |
| score-reader | 本プロジェクト。OMR 出力 MusicXML の内部整合性検査を行う Prototype / 検証支援 CLI ツール |
| verify_score.py | score-reader のプロトタイプ実装ファイル（`prototype/src/verify_score.py`） |
| Prototype | 技術検証用の実装。正式完成版ではない。現フェーズの `verify_score.py` を指す |
| Legacy Source | 標準7文書化前の旧設計書（`legacy/` 配下）。削除済みではなく参照元として保持する |
| `[FATAL]` | MusicXML パース失敗を示す出力レベル。終了コード 1 で終了する |
| `[ANOMALY]` | 小節長と拍子の不一致など、構造上の異常を示す出力レベル |
| `[WARN]` | 要確認の疑いがある箇所を示す出力レベル |
| `[INFO]` | 参考情報を示す出力レベル |
| 確認対象データ | OMR 出力 MusicXML の位置づけ。「正解データ」ではなく人間が確認すべきデータ |
| パブリックドメイン | 著作権保護期間が満了または権利放棄された楽譜。テスト素材として使用可能 |
| CC BY-NC-SA 4.0 | score-reader 本体のライセンス。非商用・継承・帰属の3条件が適用される |

---

## 5. Document Owners and Reviewers（文書管理者・レビュアー一覧）

| Role（役割） | Name（氏名） | Assigned Documents（担当文書） |
|---|---|---|
| Document Owner（文書管理者） | Takashi Oikawa | 全文書（README / 01〜06 / legacy/） |
| Reviewer（レビュアー） | 未定 | 未定 |

---

## 6. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-04 | Legacy Source 初版（legacy/MULTI_OMR_BASIC_DESIGN.md 初版コミット日を引き継ぐ。設計Doc群の中で最も古い元Doc作成日を採用） | Takashi Oikawa |
| 0.2 | 2026-06-21 | 標準7文書への移行完了に伴い README を記入。01〜06 各設計書・legacy 2文書・LICENSE ファイルを参照し全セクションを記入 | Takashi Oikawa |
