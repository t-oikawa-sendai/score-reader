# score-reader

<!-- Document Information（文書情報） -->

| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | README-001 |
| Version（バージョン） | 0.4.7 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-10-02 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | SKILL.md / docs/design/01_REQUEST_DEFINITION.md 〜 06_OPERATION_AND_HANDOFF.md |

score-reader は、OMR（Optical Music Recognition）が生成した MusicXML の構造的異常や要確認箇所を検出し、人間による原本 PDF との確認範囲を絞り込むための CLI ツールです。

OMR で楽譜 PDF を MusicXML 化し、MuseScore 等で確認・修正する人が、原本との照合に入る前に、機械的に検出できる箇所を先に把握するために使います。

> **Current Status（現状）**: 現行プロトタイプ（`prototype/src/verify_score.py`）はコード凍結中です。本リポジトリでは設計文書の検証・更新を継続しています。

## Background and Issues（背景・課題）

### Target Users（対象利用者）

OMR を利用して楽譜 PDF を MusicXML 化し、MuseScore 等で確認・修正する利用者です。

### Current Issues（現在の課題）

- OMR 出力は、そのまま完成版 MusicXML として扱えるとは限りません。
- 音高・音価・声部・記号等が原本譜と一致しているかは、MusicXML だけでは完全には判定できません。
- 人間が原本 PDF と照合する作業が必要になります。

### Improvement by score-reader（score-readerによる改善）

機械的に検出できる構造的異常や要確認候補を先に抽出し、人間が確認する範囲を絞り込みます。

背景・課題・目的・対象範囲の詳細は [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) を参照してください。

## Main Features（主な機能）

### Current Prototype（現行プロトタイプ）

現在の `prototype/src/verify_score.py` は、単一の MusicXML に対して次を行います。

- MusicXML のパース
- 移調・小節長・調号・拍子/テンポの検査
- Unpitched（無音高）要素の検出
- 和音音数・パート間小節数の検査
- テキスト / JSON 出力

### Production Implementation（今後の本実装）

複数 MusicXML を比較し、人間が確認すべき箇所を絞り込む機能を、本実装として設計しています。現行プロトタイプには未実装です。

機能要件・非機能要件、および本実装の範囲は [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) を参照してください。

## Design and Development Principles（設計・開発上の考え方）

score-reader は、検出できることと人間が判断することを分けて設計しています。

- MusicXML だけから正解を推測して、自動補完しません。
- 原本 PDF との最終確認は、人間が行います。
- 入力 MusicXML を、破壊的に上書きしません。
- 構造検査で異常が 0 件でも、完全無欠とは判断しません。
- 単一の OMR 結果だけに依存せず、将来は複数 OMR 結果を比較します。
- 機械が検出できる範囲と、人間の判断が必要な範囲を分離します。

判断の根拠は次を参照してください。

- [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md)
- [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md)
- [05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md)

## Technical Information and Usage（技術情報・使い方）

### Technology Stack（技術構成）

リポジトリ上で確認できる構成は次のとおりです。

- Python
- music21 `10.3.0`（`prototype/requirements.txt` で固定）

### Execution Method（実行方法）

リポジトリルートで実行します。

```bash
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml --json
```

操作フローの詳細は [04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md) を参照してください。

## Design Documents（設計文書）

詳細仕様の正本は `docs/design/` です。README は入口であり、仕様の再掲ではありません。

| Document（文書） | Description（内容） |
|---|---|
| [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) | 要求定義：背景・課題・目的・対象範囲 |
| [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) | 要件定義：機能要件・非機能要件 |
| [03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md) | データ・セキュリティ・著作権 |
| [04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md) | CLI・操作フロー |
| [05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md) | アーキテクチャ・構成 |
| [06_OPERATION_AND_HANDOFF.md](docs/design/06_OPERATION_AND_HANDOFF.md) | テスト・運用・詳細設計への引き継ぎ |
| [SKILL.md](SKILL.md) | AI/Cursor が作業するときのルール |

## Repository Structure（リポジトリ構成）

```text
score-reader/
├── README.md
├── SKILL.md
├── LICENSE
├── LICENSE-CODE
├── LICENSE-DOCS
├── NOTICE
├── docs/
│   ├── design/
│   │   ├── 01_REQUEST_DEFINITION.md
│   │   ├── 02_REQUIREMENTS_DEFINITION.md
│   │   ├── 03_DATA_AND_SECURITY_DESIGN.md
│   │   ├── 04_UI_AND_FLOW_DESIGN.md
│   │   ├── 05_ARCHITECTURE_DESIGN.md
│   │   └── 06_OPERATION_AND_HANDOFF.md
│   └── reviews/
│       └── 過去のレビュー記録
└── prototype/
    ├── src/
    │   └── verify_score.py
    ├── tests/
    └── requirements.txt
```

`docs/reviews/` には過去のレビュー記録があります。テスト用 MusicXML は `prototype/tests/` にあります。

## License（ライセンス）

ライセンス本文は各ファイルが正本です。

- ソースコード: MIT License / [LICENSE-CODE](LICENSE-CODE)
- ドキュメント: CC BY-NC-SA 4.0 / [LICENSE-DOCS](LICENSE-DOCS)
- 第三者表記とテスト素材に関する注記: [NOTICE](NOTICE)
- [LICENSE](LICENSE) は、ドキュメントライセンスの legacy record です。

権利判断とテスト素材の詳細は [03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md) を参照してください。

## AI Usage（AI利用）

要求整理、設計、文書更新、レビューの各工程で AI を利用しています。生成結果は Project Owner が確認し、採用する内容を決めています。

| Phase（工程） | AI Usage（AI利用） |
|---|---|
| 要求・要件整理 | Ownerの指示により、ChatGPTが整理・論点確認 |
| 設計 | 概要設計はOwner、ChatGPT による設計整理・実装指示作成 |
| 実装・文書更新 | Cursor による編集・検証作業 |
| レビュー | AI による独立レビューを利用、Ownerが実機確認検証 |
| 最終判断 | Project Owner が確認・承認 |
※ README作成に関しては全文Ownerからの指示

## Change History（変更履歴）

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
| 0.4.6 | 2026-10-02 | READMEをプロジェクト入口として再構成。主要情報、設計文書への導線、Repository構成、ライセンス、AI利用を整理し、人間向け表示を English（日本語）へ統一。仕様変更なし | Takashi Oikawa |
| 0.4.7 | 2026-10-02 | AI利用範囲とOwnerの責任範囲を明確化。仕様変更なし | Takashi Oikawa |
