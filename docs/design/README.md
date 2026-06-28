# Design Documents Index（設計書一覧）

<!--
README Writing Policy（README作成方針）
- README は設計書群の表紙・入口とする
- 文章は最短にする。詳細は個別 Doc へ誘導する
- スクリーンショットは最小サイズの代表画像のみ掲載する
- `screenshots/thumbnail/` は README 用の小さい代表スクリーンショットを配置する
- `screenshots/full/` は個別 Doc 用の大きいスクリーンショットを配置する
- README では thumbnail の代表画像のみを使用し、詳細画像は 04_UI_AND_FLOW_DESIGN.md から full を参照する
- 大きいスクリーンショット・画面項目説明・操作フローは 04_UI_AND_FLOW_DESIGN.md へ分離する
- 個人情報・機密情報・APIキー・トークンが写る画像は使用禁止
- Change History は作業メモにしない
-->

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | README-001 |
| Version（バージョン） | 0.3.3 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-06-28 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | docs/standards/DESIGN_DOCUMENT_STANDARD.md / legacy/ |

---

## Table of Contents（目次）

1. [Project Overview（プロジェクト・機能の概要）](#1-project-overviewプロジェクト機能の概要)
2. [Problem / Solution / Benefit Summary（問題・解決・効果の概要）](#2-problem-solution-benefit-summary問題解決効果の概要)
3. [Screen Overview（画面概要）](#3-screen-overview画面概要)
4. [Design Documents Index（設計書一覧）](#4-design-documents-index設計書一覧)
5. [Overall Design Policy（設計上の全体方針・前提）](#5-overall-design-policy設計上の全体方針前提)
6. [Glossary（用語集・略語定義）](#6-glossary用語集略語定義)
7. [Document Owners and Reviewers（文書管理者・レビュアー一覧）](#7-document-owners-and-reviewers文書管理者レビュアー一覧)
8. [Change History（変更履歴）](#8-change-history変更履歴)

---

## 1. Project Overview（プロジェクト・機能の概要）

本設計書群は、完成版 MusicXML 作成支援システムへ到達するための検証結果・設計判断・未確定事項を整理したプロトタイプ段階の設計ガイドラインである。

score-reader は、OMR（Optical Music Recognition）が出力した MusicXML の**内部整合性を検査するプロトタイプ検証段階の検証支援 CLI ツール**である。機械的に検出できる構造的異常・要確認箇所を列挙し、人間の原本 PDF 照合作業の対象を絞り込む。

開発段階の整理は下表「Development Stage Classification（開発段階の分類）」を参照する。

### Development Stage Classification（開発段階の分類）

| Development Stage（開発段階） | Main Scope（主な対象） | Representative Implementation（代表実装） | Not Included / Future Consideration（含めないもの / 将来検討事項） |
|---|---|---|---|
| プロトタイプ検証段階 | 単一 MusicXML の構造検査。検証結果・設計判断・未確定事項の記録 | `prototype/src/verify_score.py`（単一 MusicXML 構造検査の検証実装）。検査結果の標準出力（テキスト / JSON） | 自動修正、自動統合、Web UI、原本 PDF 横並び画面は、現時点で定義する本実装段階には含めず、将来検討事項として扱う |
| 完成版MusicXML作成支援システムの本実装段階 | 複数 MusicXML 比較、差分可視化、比較レポート生成 | 未実装（本設計書群では方針・引き継ぎ事項として整理） | 自動修正、自動統合、Web UI、原本 PDF 横並び画面は、現時点で定義する本実装段階には含めず、将来検討事項として扱う。詳細は各 Doc の Open Issues を参照 |

---

## 2. Problem / Solution / Benefit Summary（問題・解決・効果の概要）

<!-- 各項目は1〜2文の概要のみ。詳細は下記 Doc へ誘導する -->

| Item（項目） | Summary（概要） | Detail Document（詳細文書） |
|---|---|---|
| Current Problems（現在の問題点） | OMR 出力 MusicXML は精度に限界があり、そのまま完成版として扱えない。難しい楽譜では MuseScore 上での手作業確認に大量の時間を要する。 | [01_REQUEST_DEFINITION.md](./01_REQUEST_DEFINITION.md) |
| Development Purpose（開発目的） | 人間確認をゼロにするのではなく、確認対象を絞り込み作業を省力化する。自動化できることと人間確認が必要なことを明確に分離する。 | [01_REQUEST_DEFINITION.md](./01_REQUEST_DEFINITION.md) |
| Solution Approach（解決方針） | ローカル CLI で単一 MusicXML の構造検査 [1]〜[8] を実行し、推測・断定せず `[FATAL]` / `[ANOMALY]` / `[WARN]` / `[INFO]` で列挙する。入力ファイルは非破壊。 | [01_REQUEST_DEFINITION.md](./01_REQUEST_DEFINITION.md) |
| System Functions（システム機能） | MusicXML パース、移調・小節長・調号・拍子/テンポ・未確定要素・リハーサルマーク・和音音数・パート間小節数の検査、テキスト/JSON 出力、終了コード管理。 | [02_REQUIREMENTS_DEFINITION.md](./02_REQUIREMENTS_DEFINITION.md) |
| Expected Benefits（期待効果） | 構造的異常の早期発見、確認箇所の優先順位付け、設計意図の記録による将来の引き継ぎ。削減効果の定量値はプロトタイプ検証段階では未実測。 | [01_REQUEST_DEFINITION.md](./01_REQUEST_DEFINITION.md) |
| Completion Criteria（完成判定基準） | SC-001〜SC-008（パース判定・各検査項目の出力・テキスト/JSON 出力）を満たすこと。`[WARN]`/`[ANOMALY]` 0 件でも完全無欠を保証しない（HC-005）。 | [01_REQUEST_DEFINITION.md](./01_REQUEST_DEFINITION.md) |

---

## 3. Screen Overview（画面概要）

<!-- 代表画面のみ thumbnail で掲載。full の詳細画像・画面項目・操作フローは 04 へ分離 -->

プロトタイプ検証段階は GUI / Web UI を持たない CLI ツールのため、代表インターフェースはターミナル上の実行例とする。

```bash
python3 verify_score.py ../tests/<file>.musicxml
python3 verify_score.py ../tests/<file>.musicxml --json
```

詳細（CLI 仕様・業務フロー・出力確認・人間レビューチェックリスト）: [04_UI_AND_FLOW_DESIGN.md](./04_UI_AND_FLOW_DESIGN.md)

---

## 4. Design Documents Index（設計書一覧）

| File（ファイル名） | Document Name（文書名） | Status（ステータス） | Version（バージョン） | Owner（担当者） |
|---|---|---|---|---|
| [01_REQUEST_DEFINITION.md](./01_REQUEST_DEFINITION.md) | Request Definition（要求定義） | Draft | 0.2 | Takashi Oikawa |
| [02_REQUIREMENTS_DEFINITION.md](./02_REQUIREMENTS_DEFINITION.md) | Requirements Definition（要件定義） | Draft | 0.2 | Takashi Oikawa |
| [03_DATA_AND_SECURITY_DESIGN.md](./03_DATA_AND_SECURITY_DESIGN.md) | Data and Security Design（データ・セキュリティ設計） | Draft | 0.2 | Takashi Oikawa |
| [04_UI_AND_FLOW_DESIGN.md](./04_UI_AND_FLOW_DESIGN.md) | UI and Flow Design（UI・フロー設計） | Draft | 0.2 | Takashi Oikawa |
| [05_ARCHITECTURE_DESIGN.md](./05_ARCHITECTURE_DESIGN.md) | Architecture Design（アーキテクチャ設計） | Draft | 0.2 | Takashi Oikawa |
| [06_OPERATION_AND_HANDOFF.md](./06_OPERATION_AND_HANDOFF.md) | Operation and Handoff Design（運用・詳細設計引き継ぎ） | Draft | 0.2 | Takashi Oikawa |

各文書は Draft ステータスであり、**プロトタイプ検証段階**の設計記録として位置づける。開発段階の分類は §1 Development Stage Classification を参照。内容抽出元の旧 Doc は [legacy/](./legacy/) に保持する。

---

## 5. Overall Design Policy（設計上の全体方針・前提）

| 前提 | 内容 |
|---|---|
| 設計ガイドラインの位置づけ | 本設計書群は、完成版 MusicXML 作成支援システムへ到達するための検証結果・設計判断・未確定事項を整理したプロトタイプ段階の設計ガイドラインである |
| 開発段階の分類 | §1 Development Stage Classification を参照。プロトタイプ検証段階と完成版MusicXML作成支援システムの本実装段階の2分類で整理する |
| プロトタイプ検証段階のスコープ | 単一 MusicXML の内部整合性検査 CLI（`verify_score.py`）のみ |
| 本実装段階の主対象 | 複数 MusicXML 比較、差分可視化、比較レポート生成 |
| 将来検討事項 | 自動修正、自動統合、Web UI、原本 PDF 横並び画面は、現時点で定義する本実装段階には含めず、将来検討事項として扱う |
| 完全自動化しない | 音高・音価・声部・タイ/スラー等の正誤を機械的に確定できない |
| 人間確認を省略しない | 確認対象を絞り込むことが目的であり、原本 PDF との目視照合は必須 |
| 推測しない・断定しない | 確定できない結果は `[WARN]` / `[INFO]` で列挙し、黙殺・自動補完を行わない |
| 警告なし≠正確 | `[WARN]` / `[ANOMALY]` が 0 件でも MusicXML の完全無欠を保証しない |
| OMR 出力は確認対象データ | OMR が生成した MusicXML は「正解データ」ではなく「確認対象データ」である |
| 独立したシステム | 他システムと連携しないローカル実行ツール |

**ライセンス・著作権（概要）**

- score-reader のライセンスは **CC BY-NC-SA 4.0**（`LICENSE` 参照）
- 著作権保護楽譜を公開リポジトリへ登録しない。テスト素材（`prototype/tests/`）はパブリックドメインに限定
- 詳細は [03_DATA_AND_SECURITY_DESIGN.md](./03_DATA_AND_SECURITY_DESIGN.md)

**推奨参照順**

```
README.md → 01 → 02 → 03 → 04 → 05 → 06
```

---

## 6. Glossary（用語集・略語定義）

<!-- この設計書群で使用するプロジェクト固有の用語・略語を定義する -->
<!-- 汎用的な IT 用語は記載不要 -->

| Term / Abbreviation（用語・略語） | Definition（定義） |
|---|---|
| OMR | Optical Music Recognition。楽譜 PDF・画像から MusicXML 等の機械可読形式へ変換する処理 |
| MusicXML | 楽譜を XML 形式で表現した標準フォーマット。OMR の出力形式として利用する |
| score-reader | 本プロジェクト。OMR 出力 MusicXML の内部整合性検査を行うプロトタイプ検証段階の検証支援 CLI ツール |
| verify_score.py | プロトタイプ検証段階の検証実装（`prototype/src/verify_score.py`）。単一 MusicXML 構造検査 |
| プロトタイプ検証段階 | 単一 MusicXML 構造検査と検証結果記録の段階。`verify_score.py` が代表実装 |
| 完成版MusicXML作成支援システムの本実装段階 | 複数 MusicXML 比較・差分可視化・比較レポート生成を主対象とする段階（未実装） |
| Prototype | 技術検証用の実装。正式完成版ではない |
| Legacy Source | 標準7文書化前の旧設計書（`legacy/` 配下）。参照元として保持する |
| `[FATAL]` | MusicXML パース失敗を示す出力レベル。終了コード 1 で終了する |
| `[ANOMALY]` | 小節長と拍子の不一致など、構造上の異常を示す出力レベル |
| `[WARN]` | 要確認の疑いがある箇所を示す出力レベル |
| `[INFO]` | 参考情報を示す出力レベル |
| 確認対象データ | OMR 出力 MusicXML の位置づけ。「正解データ」ではなく人間が確認すべきデータ |
| パブリックドメイン | 著作権保護期間が満了または権利放棄された楽譜。テスト素材として使用可能 |
| CC BY-NC-SA 4.0 | score-reader 本体のライセンス。非商用・継承・帰属の3条件が適用される |

---

## 7. Document Owners and Reviewers（文書管理者・レビュアー一覧）

| Role（役割） | Name（氏名） | Assigned Documents（担当文書） |
|---|---|---|
| Document Owner（文書管理者） | Takashi Oikawa | All Documents（README / 01〜06） |
| Reviewer（レビュアー） | 未定 | 未定 |

---

## 8. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-09 | 初版作成 | Takashi Oikawa |
| 0.2 | 2026-06-28 | legacy/ を内容抽出元として設計書群正本記入・Development Stage Classification 追加・開発段階分類表記統一・将来検討事項表記統一・Document Info 日付統一 | Takashi Oikawa |
