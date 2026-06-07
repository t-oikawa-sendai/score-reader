# score-reader

## プロジェクト概要

`score-reader` は、同一の原本 PDF から生成された複数の OMR 変換結果を比較し、人間が確認すべき箇所を絞り込むための **設計・検証プロジェクト** です。

- 単一 OMR の認識結果をそのまま採用しない
- 複数 OMR の比較と MusicXML 内部の整合性検査を併用する
- 推測による自動補完を避け、要確認箇所を明示する
- 原本 PDF を正本として保持する

## 現在の位置づけ

**本リポジトリは現在、基本設計段階です。**

Phase 1（複数 MusicXML 比較と比較レポート生成）の詳細設計・正式実装は未着手です。リポジトリの最優先事項は、設計方針と文書構造の明確化です。

## 文書

### 基本設計（正本）

- [docs/design/SCORE_READER_BASIC_DESIGN.md](docs/design/SCORE_READER_BASIC_DESIGN.md) — プロジェクトの基本設計に関する正本

### 補助文書

- [docs/project/PROJECT_SCOPE.md](docs/project/PROJECT_SCOPE.md) — 対象範囲、対象外、変更範囲
- [docs/project/DEVELOPMENT_PHASES.md](docs/project/DEVELOPMENT_PHASES.md) — Phase 1 と将来検討事項の境界
- [docs/project/OPEN_ISSUES.md](docs/project/OPEN_ISSUES.md) — 未確定事項

### 移行元資料

- [docs/design/MULTI_OMR_BASIC_DESIGN.md](docs/design/MULTI_OMR_BASIC_DESIGN.md) — 複数 OMR 比較に関する先行基本設計（参考資料）

## 現行 Python ソースについて

`prototype/src/verify_score.py` は、単一 MusicXML の構造検査が技術的に可能かを確認するための **技術検証用プロトタイプ** です。

- 正式完成版ではない
- 現段階では改修対象としない
- 詳細設計後に、再利用、置換、廃止のいずれとするか判断する

現行ソースは技術検証用プロトタイプである。詳細説明の整理は後工程で行う。

## 原本 PDF との照合について

MusicXML の内部整合性が正常でも、原本 PDF と異なる場合があります。**最終的な正確性は、原本 PDF との目視照合で担保してください。**

本プロジェクトは、確認すべき箇所を絞り込むことを目的とし、原本 PDF の内容を自動で確定することは Phase 1 の対象外です。

## 著作権・セキュリティ

- **著作権保護された譜面を GitHub へ登録しない**
- GitHub 上のテスト素材は、パブリックドメインに限定する
- API キー、トークン、秘密鍵、個人情報をソース、ログ、Git 管理対象へ含めない
- 外部 OMR サービスへ譜面を送信する場合は、利用規約と著作権条件を確認する

## リポジトリ構成

```text
score-reader/
├── README.md
├── SKILL.md
├── .gitignore
│
├── docs/
│   ├── design/
│   │   ├── SCORE_READER_BASIC_DESIGN.md
│   │   └── MULTI_OMR_BASIC_DESIGN.md   # 移行元の参考資料
│   │
│   └── project/
│       ├── PROJECT_SCOPE.md
│       ├── DEVELOPMENT_PHASES.md
│       └── OPEN_ISSUES.md
│
└── prototype/
    ├── src/
    │   └── verify_score.py             # 技術検証用プロトタイプ
    ├── tests/
    │   └── *.musicxml                  # テスト素材
    └── requirements.txt
```
