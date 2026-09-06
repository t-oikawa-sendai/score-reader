# score-reader

> **現行プロトタイプ（`prototype/src/verify_score.py`）はコード凍結中です。**<br>
> 本リポジトリでは設計文書の検証・更新を継続しています。

score-readerは、OMR（楽譜認識）が出力したMusicXMLの構造検査を行うCLIツールです。

本リポジトリの本質は、**現行技術では自動化できない楽譜データ化の問題について、「機械にできること・できないこと・人間に委ねるべきこと」の境界を検証し、将来の開発者・保守者へ引き継ぐ設計記録として残す**ことにあります。

楽譜PDFのデータ化において、現状の技術では、本プロジェクトが対象とするMusicXMLの構造検査だけで、音高・音価・声部が原本譜と一致しているかを機械的に確定することはできません。<br>
score-readerは「機械にできる構造検査の範囲」を最大化しつつ、「人間が原本PDFと照合すべき領域」を明確に絞り込むことで、確認作業の省力化を目指します。ここでいう「最大化」は設計上の目標であり、現段階の定量的な要件でも、合否基準でもありません。

> 「人間確認をゼロにする」のではなく、<br>
> 「人間が確認すべき箇所を絞り込む」ことで作業効率を最大化する。

## 現行の位置づけ

- **プロトタイプ検証段階**：単一MusicXMLの構造検査CLI（`prototype/src/verify_score.py`）
- **本実装の確定スコープ**：複数MusicXML比較・差分可視化・比較レポート生成
- **将来検討事項**：自動修正、自動統合、Web UI
- **本リポジトリの対象外**：原本PDF横並び画面。本リポジトリでは設計・実装方針を定義しません

原本PDF横並び画面の本リポジトリへの実装は対象外ですが、人間がMuseScore等を使用して原本PDFと目視照合する既存運用は維持します。

## 使い方

リポジトリルートから実行します。

```bash
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml --json
```

<!--
README Writing Policy（README作成方針）
- README は設計書群の表紙・入口とする
- 文章は最短にする。詳細は個別 Doc へ誘導する
- 個人情報・機密情報・APIキー・トークンが写る画像は使用禁止
- Change History は作業メモにしない
-->

---

## Table of Contents（目次）

- [現行の位置づけ](#現行の位置づけ)
- [使い方](#使い方)
1. [Project Overview Detail（開発段階の詳細分類）](#1-project-overview-detail開発段階の詳細分類)
2. [Problem / Solution / Benefit Summary（問題・解決・効果の概要）](#2-problem-solution-benefit-summary問題解決効果の概要)
3. [Screen Overview Detail（CLIインターフェース詳細）](#3-screen-overview-detailcliインターフェース詳細)
4. [Design Documents Index（設計書一覧）](#4-design-documents-index設計書一覧)
5. [Overall Design Policy（設計上の全体方針・前提）](#5-overall-design-policy設計上の全体方針前提)
6. [Glossary（用語集・略語定義）](#6-glossary用語集略語定義)
7. [Document Owners and Reviewers（文書管理者・レビュアー一覧）](#7-document-owners-and-reviewers文書管理者レビュアー一覧)
8. [Change History（変更履歴）](#8-change-history変更履歴)

---

## 1. Project Overview Detail（開発段階の詳細分類）

開発段階ごとの詳細分類を下表に示す。読者が最初に理解すべき概要、設計思想、現在位置、基本実行例は冒頭（現行の位置づけ・使い方）を参照する。全体方針は §5、要求上の境界分類は [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) を参照する。正本設計文書は [docs/design/01](docs/design/01_REQUEST_DEFINITION.md)〜[06](docs/design/06_OPERATION_AND_HANDOFF.md) である。`prototype/` は正式実装ではなく技術検証用である。score-reader は、OMR（Optical Music Recognition）が出力した MusicXML の内部整合性を検査する検証支援 CLI ツールである。機械的に検出できる構造的異常・要確認箇所を列挙し、人間の原本 PDF 照合作業の対象を絞り込む。

### Development Stage Classification（開発段階の分類）

| Development Stage（開発段階） | Main Scope（主な対象） | Representative Implementation（代表実装） | Not Included / Future Consideration（含めないもの / 将来検討事項） |
|---|---|---|---|
| 現行プロトタイプ（プロトタイプ検証段階） | 単一 MusicXML の構造検査。検証結果・設計判断・未確定事項の記録 | `prototype/src/verify_score.py`（単一 MusicXML 構造検査の検証実装）。検査結果の標準出力（テキスト / JSON）。コード凍結中 | 本実装確定スコープ（複数 MusicXML 比較一式）は現行プロトタイプに含めない。自動修正、自動統合、Web UI は将来検討事項。原本 PDF 横並び画面は本リポジトリの対象外であり、本リポジトリでは設計・実装方針を定義しない |
| 完成版MusicXML作成支援システムの本実装（確定スコープ） | 複数 MusicXML 入力、正規化、比較可能性判定、差分比較、差分可視化、比較レポート生成 | 未実装（確定スコープ。詳細は本実装時に定義する） | 自動修正、自動統合、Web UI は、現時点で定義する本実装段階には含めず、将来検討事項として扱う。原本 PDF 横並び画面は本リポジトリの対象外であり、本リポジトリでは設計・実装方針を定義しない |
| 将来検討事項 | 対象外。本実装確定スコープにも現行プロトタイプにも含めない | 未実装 | 自動修正、自動統合、Web UI |
| 本リポジトリの対象外 | 原本 PDF 横並び画面。本リポジトリでは設計・実装方針を定義しない | 定義しない | 原本 PDF 横並び画面の本リポジトリへの実装は対象外である。人間が MuseScore 等を使用して原本 PDF と目視照合する既存運用は維持する |

---

## 2. Problem / Solution / Benefit Summary（問題・解決・効果の概要）

<!-- 各項目は1〜2文の概要のみ。詳細は下記 Doc へ誘導する -->

| Item（項目） | Summary（概要） | Detail Document（詳細文書） |
|---|---|---|
| Current Problems（現在の問題点） | OMR 出力 MusicXML は精度に限界があり、そのまま完成版として扱えない。難しい楽譜では MuseScore 上での手作業確認に大量の時間を要する。 | [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) |
| Development Purpose（開発目的） | 機械的に検出可能な領域、人間確認が必要な領域、現技術では自動化困難な領域を分離し、確認対象を絞り込む。人間確認をゼロにすることは目的ではない。 | [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) |
| Solution Approach（解決方針） | 完成版MusicXML作成支援システムに向け、複数 OMR 結果の比較、MusicXML 内部構造検査、比較不能箇所の明示を組み合わせ、人間が原本 PDF と照合すべき箇所を絞り込む。推測による自動補完や入力ファイルの上書きは行わない。 | [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) |
| System Functions（システム機能） | 現行プロトタイプ: MusicXML パース、移調・小節長・調号・拍子/テンポ・Unpitched（無音高）・リハーサルマーク・和音音数・パート間小節数の検査、テキスト/JSON 出力、終了コード管理。本実装確定スコープ: 複数 MusicXML 入力、正規化、比較可能性判定、差分比較、差分可視化、比較レポート生成（未実装。詳細は本実装時に定義）。 | [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) |
| Expected Benefits（期待効果） | 構造的異常の早期発見、確認箇所の優先順位付け、設計判断の記録による将来の引き継ぎ。削減効果の定量値はプロトタイプ検証段階では未実測。 | [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) |
| Completion Criteria（完成判定基準） | SC-001〜SC-009（パース判定・各検査項目の出力・Unpitched 件数の報告・テキスト/JSON 出力）を満たすこと。`[WARN]`/`[ANOMALY]` 0 件でも完全無欠を保証しない（HC-005）。 | [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) |

---

## 3. Screen Overview Detail（CLIインターフェース詳細）

プロトタイプ検証段階は GUI / Web UI を持たない CLI ツールのため、代表インターフェースはターミナル上の実行である。基本実行例（リポジトリルート起点）は冒頭「使い方」を参照する。

詳細（CLI 仕様・業務フロー・出力確認・人間レビューチェックリスト）: [04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md)

---

## 4. Design Documents Index（設計書一覧）

| File（ファイル名） | Document Name（文書名） | Status（ステータス） | Version（バージョン） | Owner（担当者） |
|---|---|---|---|---|
| [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) | Request Definition（要求定義） | Draft | 0.3.5 | Takashi Oikawa |
| [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) | Requirements Definition（要件定義） | Draft | 0.3.5 | Takashi Oikawa |
| [03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md) | Data and Security Design（データ・セキュリティ設計） | Draft | 0.3.4 | Takashi Oikawa |
| [04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md) | UI and Flow Design（UI・フロー設計） | Draft | 0.3.4 | Takashi Oikawa |
| [05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md) | Architecture Design（アーキテクチャ設計） | Draft | 0.3.5 | Takashi Oikawa |
| [06_OPERATION_AND_HANDOFF.md](docs/design/06_OPERATION_AND_HANDOFF.md) | Operation and Handoff Design（運用・詳細設計引き継ぎ） | Draft | 0.3.5 | Takashi Oikawa |

各文書は Draft ステータスであり、**プロトタイプ検証段階**の設計記録として位置づける。開発段階の分類は §1 Development Stage Classification を参照する。作業ルールは [SKILL.md](SKILL.md) を参照する。設計レビュー記録は [docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md](docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md) および [docs/reviews/2026-09-06_SCORE_READER_CROSS_DOCUMENT_REVIEW.md](docs/reviews/2026-09-06_SCORE_READER_CROSS_DOCUMENT_REVIEW.md) を参照する。

---

## 5. Overall Design Policy（設計上の全体方針・前提）

| 前提 | 内容 |
|---|---|
| 設計ガイドラインの位置づけ | 完成版 MusicXML 作成支援システムへ到達するための検証結果・設計判断・未確定事項を整理したプロトタイプ段階の設計ガイドライン。詳細は [01](docs/design/01_REQUEST_DEFINITION.md)〜[06](docs/design/06_OPERATION_AND_HANDOFF.md) |
| 開発段階の分類 | §1 Development Stage Classification を参照。現行プロトタイプ、本実装確定スコープ、将来検討事項、本リポジトリの対象外 |
| 現行プロトタイプのスコープ | 単一 MusicXML の内部整合性検査 CLI（`verify_score.py`）のみ。コード凍結中。機能要件は [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) |
| 本実装確定スコープ | 複数 MusicXML 入力、正規化、比較可能性判定、差分比較、差分可視化、比較レポート生成。未実装であり、未確定ではない。[02](docs/design/02_REQUIREMENTS_DEFINITION.md) §5.8 / [05](docs/design/05_ARCHITECTURE_DESIGN.md) |
| 将来検討事項 | 自動修正、自動統合、Web UI。本実装確定スコープには含めない。§1 を参照 |
| 本リポジトリの対象外 | 原本 PDF 横並び画面。本リポジトリでは設計・実装方針を定義しない。人間が MuseScore 等を使用して原本 PDF と目視照合する既存運用は維持する。§1 を参照 |
| 完全自動化しない | 音高・音価・声部・タイ/スラー等の正誤を機械的に確定できない。[01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) §5.5 |
| 人間確認を省略しない | 確認対象を絞り込むことが目的であり、原本 PDF との目視照合は必須 |
| 推測しない・断定しない | 確定できない結果は `[WARN]` / `[INFO]` で列挙し、黙殺・自動補完を行わない。引き継ぎは [06_OPERATION_AND_HANDOFF.md](docs/design/06_OPERATION_AND_HANDOFF.md) |
| 警告なし≠正確 | `[WARN]` / `[ANOMALY]` が 0 件でも MusicXML の完全無欠を保証しない |
| OMR 出力は確認対象データ | OMR が生成した MusicXML は「正解データ」ではなく「確認対象データ」である |
| 独立したシステム | 他システムと連携しないローカル実行ツール |

**ライセンス・著作権（概要）**

現在の分離構成を正式な構成として扱う。

| 対象 | ライセンス | 参照 |
|---|---|---|
| ソースコード | MIT License | [LICENSE-CODE](LICENSE-CODE) |
| 設計文書・README・作業ルール | CC BY-NC-SA 4.0 | [LICENSE-DOCS](LICENSE-DOCS) |
| 旧ライセンス記録 | 移行前の単一ライセンス記録として残置 | [LICENSE](LICENSE) |
| テスト素材（`prototype/tests/`） | 上記2区分のいずれにも自動的に含めない。権利・法務未解決事項は 03 TBD-005、技術的な由来は 05 TBD-005 で追跡する | [NOTICE](NOTICE) / [03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md) / [05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md) |

- テスト素材は、楽曲の権利、MusicXML エンコーディングの権利、加工・再配布条件を分けて確認する
- 現在公開中のテスト素材は権利確認中であり、暫定的に公開継続する。公開可否の法的確定は未完了である
- 詳細は [NOTICE](NOTICE) および [03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md)

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
| score-reader | 本プロジェクト。OMR 出力 MusicXML の確認対象を絞り込む検証プロジェクト |
| verify_score.py | 現行プロトタイプの検証実装（`prototype/src/verify_score.py`）。単一 MusicXML 構造検査。コード凍結中 |
| コード凍結 | 現行 `verify_score.py` の実装を変更しない状態。設計文書の更新・検証は継続する |
| プロトタイプ検証段階 | §1 Development Stage Classification の現行プロトタイプ段階 |
| 完成版MusicXML作成支援システムの本実装段階 | §1 の本実装確定スコープ。未実装。未確定ではない |
| Prototype | 技術検証用の実装。正式完成版ではない |
| `[FATAL]` | MusicXML パース失敗を示す出力レベル。終了コード 1 で終了する。[02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) §5.1 |
| `[ANOMALY]` | 小節長と拍子の不一致など、構造上の異常を示す出力レベル。同上 |
| `[WARN]` | 要確認の疑いがある箇所を示す出力レベル。同上 |
| `[INFO]` | 参考情報を示す出力レベル。同上 |
| Unpitched（無音高） | 音高を持たない要素。検査 [5]（FR-006）の報告対象。[02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) |
| 確認対象データ | OMR 出力 MusicXML の位置づけ。「正解データ」ではなく人間が確認すべきデータ |
| パブリックドメイン | 本書では、著作権保護期間の満了等により、楽曲・作曲物について著作権による利用制限を受けない状態を指す。MusicXMLエンコーディングの権利・再配布条件とは別であり、テスト素材へ自動的に適用しない。 |
| MIT License | ソースコード（`LICENSE-CODE`）に適用するライセンス |
| CC BY-NC-SA 4.0 | 設計文書・README・作業ルール（`LICENSE-DOCS`）に適用するライセンス。非商用・継承・帰属の3条件が適用される |
| LICENSE | 旧ライセンス記録。現行の適用ライセンスそのものではない |

---

## 7. Document Owners and Reviewers（文書管理者・レビュアー一覧）

| Role（役割） | Name（氏名） | Assigned Documents（担当文書） |
|---|---|---|
| Document Owner（文書管理者） | Takashi Oikawa | All Documents（README / 01〜06） |
| Reviewer（レビュアー） | GEM_REVIEWER_PERSONA | All Documents（README / 01〜06） |

---

## 8. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-09 | 初版作成 | Takashi Oikawa |
| 0.2 | 2026-06-28 | 設計書群正本記入・Development Stage Classification 追加・開発段階分類表記統一・将来検討事項表記統一・Document Info 日付統一 | Takashi Oikawa |
| 0.3.3 | 2026-06-28 | Document Info の Version を 0.3.3 とした。正本構造の修正と legacy 文書参照の削除（git: 279459c）。solution approach の整合およびトップレベル見出し修正（git: c2d1f52, d936730） | Takashi Oikawa |
| 0.4.0 | 2026-09-06 | 設計レビュー反映。分離ライセンス構成への修正、成功基準を SC-001〜SC-009 に更新、存在しない標準文書リンクとスクリーンショット運用記述の削除 | Takashi Oikawa |
| 0.4.1 | 2026-09-06 | 設計レビュー差し戻し反映。本実装確定スコープ（複数 MusicXML 比較一式）と現行プロトタイプ・将来検討事項の3区分を統一。Reviewer を GEM_REVIEWER_PERSONA に統一。テスト素材は権利確認中の暫定公開継続として関連文書へ誘導 | Takashi Oikawa |
| 0.4.2 | 2026-09-06 | 文書表現の整理。設計思想（機械と人間の役割境界）の明示、コード凍結の明記、Glossary の短縮。仕様の追加・変更は行っていない | Takashi Oikawa |
| 0.4.3 | 2026-09-06 | 横断レビュー反映。実行例をリポジトリルート起点へ統一。権利追跡先と設計文書 Version を整合 | Takashi Oikawa |
| 0.4.4 | 2026-09-06 | 冒頭へ設計思想・現行位置・基本実行例を全文掲載。原本 PDF 横並び画面を将来検討事項から外し、本リポジトリでは設計・実装方針を定義しない対象へ変更。人間が MuseScore 等で原本 PDF と目視照合する既存運用は維持する | Takashi Oikawa |
| 0.4.5 | 2026-09-06 | 日本語表現の修正。設計記録の表現、最大化の位置づけ、原本 PDF 横並び画面の実装対象外の言い回し、読者表記、分離構成の表現を自然な日本語へ統一。Document Info を末尾の折りたたみ領域へ移動。仕様の追加・変更は行っていない | Takashi Oikawa |

<details>
<summary>Document Information（文書情報）</summary>

| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | README-001 |
| Version（バージョン） | 0.4.5 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-09-06 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | SKILL.md / docs/design/01_REQUEST_DEFINITION.md 〜 06_OPERATION_AND_HANDOFF.md / docs/reviews/2026-09-06_SCORE_READER_DESIGN_REVIEW.md / docs/reviews/2026-09-06_SCORE_READER_CROSS_DOCUMENT_REVIEW.md |

</details>
