# score-reader

<details>
<summary>Document Info（文書情報）</summary>

Document Information（文書情報）

| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | README-001 |
| Version（バージョン） | 0.4.10 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-11-01 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | AGENTS.md / docs/design/01_REQUEST_DEFINITION.md 〜 06_OPERATION_AND_HANDOFF.md |

</details>

## 1. Project Overview（プロジェクト概要）

score-reader は、OMR（Optical Music Recognition）が生成した MusicXML の構造的異常や要確認箇所を検出し、人間による原本 PDF との確認範囲を絞り込むための CLI ツールです。

OMR で楽譜 PDF を MusicXML 化し、MuseScore 等で確認・修正する人が、原本との照合に入る前に、機械的に検出できる箇所を先に把握するために使います。

### 1.1 Current Status（現状）

> **Current Status（現状）**: 現行プロトタイプ（`prototype/src/verify_score.py`）はコード凍結中です。別配置の初回2入力比較を実装しました。共通の自作15ケースで動作検証します。実 OMR の精度・確認時間の効果検証は未実施です。

## 2. Background and Issues（背景・課題）

### 2.1 Target Users（対象利用者）

OMR を利用して楽譜 PDF を MusicXML 化し、MuseScore 等で確認・修正する利用者です。

### 2.2 Current Issues（現在の課題）

- OMR 出力は、そのまま完成版 MusicXML として扱えるとは限りません。
- 音高・音価・声部・記号等が原本譜と一致しているかは、MusicXML だけでは完全には判定できません。
- 人間が原本 PDF と照合する作業が必要になります。

### 2.3 Improvement by score-reader（score-readerによる改善）

機械的に検出できる構造的異常や要確認候補を先に抽出し、人間が確認する範囲を絞り込みます。

背景・課題・目的・対象範囲の詳細は [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) を参照してください。

## 3. Main Features（主な機能）

### 3.1 Current Prototype（現行プロトタイプ）

現在の `prototype/src/verify_score.py` は、単一の MusicXML に対して次を行います。

- MusicXML のパース
- 移調・小節長・調号・拍子/テンポの検査
- Unpitched（無音高）要素の検出
- 和音音数・パート間小節数の検査
- テキスト / JSON 出力

### 3.2 Production Implementation（初回本実装）

`src/score_reader/` が2つのMusicXMLの音高・音価・音符/休符・和音を比較し、差分と比較不能箇所を確認順位付きで報告します。移調情報がない場合は実音だけを保留し、記音等の比較結果を残します。

機能要件・非機能要件、および本実装の範囲は [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) を参照してください。

## 4. Design and Development Principles（設計・開発上の考え方）

score-reader は、検出できることと人間が判断することを分けて設計しています。

- MusicXML だけから正解を推測して、自動補完しません。
- 原本 PDF との最終確認は、人間が行います。
- 入力 MusicXML を、破壊的に上書きしません。
- 構造検査で異常が 0 件でも、完全無欠とは判断しません。
- 単一の OMR 結果だけに依存せず、2つのMusicXMLを比較します。
- 機械が検出できる範囲と、人間の判断が必要な範囲を分離します。

判断の根拠は次を参照してください。

- [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md)
- [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md)
- [05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md)

## 5. Technical Information and Usage（技術情報・使い方）

### 5.1 Technology Stack（技術構成）

リポジトリ上で確認できる構成は次のとおりです。

- Python（初回本実装は標準ライブラリのみ。macOS/Python 3.14.3で検証）
- プロトタイプのみ music21 `10.3.0`（`prototype/requirements.txt` で固定）

### 5.2 Frozen Prototype（凍結プロトタイプの実行方法）

リポジトリルートで実行します。

```bash
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml --json
```

操作フローの詳細は [04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md) を参照してください。

### 5.3 Two-input Comparison（初回比較の実行方法）

リポジトリルートで実行します。追加ライブラリのインストールは不要です。

```bash
PYTHONPATH=src python3 -m score_reader tests/fixtures/comparison/bases/BASIC-4M/v001/base.musicxml tests/fixtures/comparison/cases/SYN-002/v001/variant.musicxml
PYTHONPATH=src python3 -m score_reader tests/fixtures/comparison/bases/BASIC-4M/v001/base.musicxml tests/fixtures/comparison/cases/SYN-002/v001/variant.musicxml --json
```

対象は非圧縮score-partwiseで、対応可能な各パート1譜表・1声部です。開始位置を分数で比較し、音価の単位差と和音内の順序を正規化します。小節対応が崩れたパートはその位置以降を保留し、他パートは続けます。場所・差分・理由・確認順位・原本で確認する事項と検査限界を出力します。低優先の対象も消しません。

タイ結合・連符・装飾音・多声部等の意味的な同一視は初回対象外です。移調量を楽器名から推測せず、PDFページ位置も補完しません。3入力以上、圧縮MusicXML、score-timewise、DTD/entity宣言は対応しません。結果一致や終了コード0は原本に対する正確性の保証ではありません。

終了コードはレポート作成0（差分・部分的比較不能を含む）、読取不能1、引数不正2。JSONも不能理由を保持します。製品は入力を読んで標準出力へ報告するだけで、入力の変更やファイルの自動保存は行いません。具体的な出力形式は設計03 §5.9・04 §5.8を参照してください。

### 5.4 Repeatable Verification（共通データでの再実行）

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/verify_comparison.py --suite v003 --output tests/results/comparison/my-run --compare-run tests/results/comparison/initial-20261101/result.json
```

`my-run`は未作成の名前に変えてください。結果の上書きは拒否します。[共通データ](tests/fixtures/comparison/README.md)と[変更理由](tests/fixtures/comparison/CHANGELOG.md)を版ごとに保存し、旧版を保持します。SYN-012の記載不整合と参照パスを修正した現行スイートはv003で、全15ケースの期待結果はv001のままです。

検証結果にはデータの版・内容識別値、実装commit、未commit差分と未追跡ファイルの復元用アーカイブが付きます。共通ケースと追加・変更ケースを分離し、見逃し・不要な理由・誤対応を照合します。警告件数の減少だけで改善と判断しません。初回基準と同一実装の再実行は再現性確認であり、実OMR効果の実証ではありません。詳細は設計06 §5.9を参照してください。

## 6. Documentation and Repository（文書・リポジトリ構成）

### 6.1 Design Documents（設計文書）

詳細仕様の正本は `docs/design/` です。README は入口であり、仕様の再掲ではありません。

| Document（文書） | Description（内容） |
|---|---|
| [01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) | 要求定義：背景・課題・目的・対象範囲 |
| [02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) | 要件定義：機能要件・非機能要件 |
| [03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md) | データ・セキュリティ・著作権 |
| [04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md) | CLI・操作フロー |
| [05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md) | アーキテクチャ・構成 |
| [06_OPERATION_AND_HANDOFF.md](docs/design/06_OPERATION_AND_HANDOFF.md) | テスト・運用・詳細設計への引き継ぎ |
| [AGENTS.md](AGENTS.md) | Work 等の AI が作業するときのルール |

### 6.2 Repository Structure（リポジトリ構成）

```text
score-reader/
├── README.md
├── AGENTS.md
├── SKILL.md（AGENTS.md への移行案内）
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
├── src/score_reader/（初回本実装）
├── tests/fixtures/comparison/（版管理する共通自作データ）
├── tests/results/comparison/（検証結果・実装復元記録）
├── tools/verify_comparison.py
└── prototype/
    ├── src/
    │   └── verify_score.py
    ├── tests/
    └── requirements.txt
```

`docs/reviews/` には過去のレビュー記録があります。凍結プロトタイプの素材は `prototype/tests/`、本実装の共通自作データは `tests/fixtures/comparison/` です。

### 6.3 License（ライセンス）

ライセンス本文は各ファイルが正本です。

- ソースコード: MIT License / [LICENSE-CODE](LICENSE-CODE)
- ドキュメント: CC BY-NC-SA 4.0 / [LICENSE-DOCS](LICENSE-DOCS)
- 第三者表記とテスト素材に関する注記: [NOTICE](NOTICE)
- [LICENSE](LICENSE) は、ドキュメントライセンスの legacy record です。

権利判断とテスト素材の詳細は [03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md) を参照してください。

## 7. AI Usage（AI利用）

要求整理、設計、文書更新、レビューの各工程で AI を利用しています。生成結果は Project Owner が確認し、採用する内容を決めています。

| Phase（工程） | AI Usage（AI利用） |
|---|---|
| 要求・要件整理 | Ownerの指示により、ChatGPTが整理・論点確認 |
| 設計 | 概要設計はOwner、ChatGPT による設計整理・実装指示作成 |
| 実装・文書更新 | Work による編集・検証作業 |
| レビュー | AI による独立レビューを利用、Ownerが実機確認検証 |
| 最終判断 | Project Owner が確認・承認 |
※ README作成に関しては全文Ownerからの指示

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
| 0.4.6 | 2026-10-02 | READMEをプロジェクト入口として再構成。主要情報、設計文書への導線、Repository構成、ライセンス、AI利用を整理し、人間向け表示を English（日本語）へ統一。仕様変更なし | Takashi Oikawa |
| 0.4.7 | 2026-10-02 | AI利用範囲とOwnerの責任範囲を明確化。仕様変更なし | Takashi Oikawa |
| 0.4.8 | 2026-10-02 | READMEの見出し階層を整理し、大項目・中項目の構造を統一。仕様変更なし | Takashi Oikawa |
| 0.4.9 | 2026-11-01 | 作業ルールの現行参照を AGENTS.md へ移行し、実装・文書更新担当を Work に更新。旧 SKILL.md は移行案内として保持。仕様変更なし | Work |
| 0.4.10 | 2026-11-01 | 初回2入力比較の実行方法・対応範囲・制約、共通データと再現可能な動作検証手順を記載。 | Work |
