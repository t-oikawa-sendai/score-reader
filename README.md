# score-reader

## 目的

`score-reader` は、楽譜 PDF を MusicXML へ変換する OMR（Optical Music Recognition）の出力を検証・活用し、人間が確認すべき箇所を絞り込むことを目指すプロジェクトです。

- 単一 OMR の認識結果をそのまま完成版として扱わない
- OMR 出力の内部整合性を機械的に検査する
- 複数 OMR 結果の比較により、確認対象を不一致箇所・高リスク箇所に集中させる
- 推測による自動補完を避け、原本 PDF を正本として保持する

現時点で、楽譜 PDF から完成版 MusicXML を完全自動生成することは目的としません。生成された MusicXML の完成度を高め、人間による確認・修正の負荷を削減することを目指します。

## システム概要

```text
原本 PDF
  ↓
OMR サービス（1 種類以上）→ MusicXML
  ↓
score-reader（検査・比較の支援）
  ↓
人間が原本 PDF と照合し、MuseScore 等で修正
```

| 要素 | 現状 |
|------|------|
| OMR 変換 | 外部サービスまたは外部ツールが担当（例: Newzik） |
| 検査 | `prototype/src/verify_score.py` による単一 MusicXML の構造検査（技術検証用プロトタイプ） |
| 最終判断 | 人間が原本 PDF と照合して行う |

MusicXML の内部整合性が正常でも、原本 PDF と異なる場合があります。最終的な正確性は、原本 PDF との目視照合で担保してください。

## 文書案内

| 文書 | 内容 |
|------|------|
| [docs/design/README.md](docs/design/README.md) | 設計文書インデックス・プロジェクト全体方針 |
| [docs/design/01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md) | 要求定義 |
| [docs/design/02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md) | 要件定義 |
| [docs/design/03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md) | データ・セキュリティ設計 |
| [docs/design/04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md) | UI・フロー設計（CLI 操作・業務フロー） |
| [docs/design/05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md) | アーキテクチャ設計 |
| [docs/design/06_OPERATION_AND_HANDOFF.md](docs/design/06_OPERATION_AND_HANDOFF.md) | 運用・引き継ぎ設計 |
| [SKILL.md](SKILL.md) | Cursor 等へ作業を依頼する際の作業ルール |

旧設計書（`docs/design/legacy/`）は Legacy Source として保持しています。標準設計文書への移行済みのため、正本として参照しないでください。

Cursor 等へ作業を依頼する際は、最初に [SKILL.md](SKILL.md) を読み込ませ、上記設計文書も確認させてください。

## リポジトリ構成

```text
score-reader/
├── README.md
├── SKILL.md
├── LICENSE           ← 旧一律ライセンス（CC BY-NC-SA 4.0）。移行経緯として保持
├── LICENSE-CODE      ← ソースコード用ライセンス（MIT License）
├── LICENSE-DOCS      ← 設計文書用ライセンス（CC BY-NC-SA 4.0）
├── NOTICE            ← サードパーティライセンス表示（music21 BSD-3-Clause 等）
├── .gitignore
├── docs/
│   └── design/
│       ├── README.md
│       ├── 01_REQUEST_DEFINITION.md
│       ├── 02_REQUIREMENTS_DEFINITION.md
│       ├── 03_DATA_AND_SECURITY_DESIGN.md
│       ├── 04_UI_AND_FLOW_DESIGN.md
│       ├── 05_ARCHITECTURE_DESIGN.md
│       ├── 06_OPERATION_AND_HANDOFF.md
│       └── legacy/
│           ├── MULTI_OMR_BASIC_DESIGN.md   ← Legacy Source
│           └── SCORE_READER_BASIC_DESIGN.md ← Legacy Source
└── prototype/
    ├── src/
    │   └── verify_score.py   ← MIT License (SPDX: MIT)
    ├── tests/
    │   └── *.musicxml         ← パブリックドメイン素材（BWV 66）。詳細は NOTICE 参照
    └── requirements.txt
```

## ライセンス（License）

本リポジトリの成果物はファイルの種別ごとに異なるライセンスを適用します。

| 対象 | ライセンス | ファイル |
|------|-----------|---------|
| ソースコード（`prototype/src/verify_score.py`） | MIT License | [LICENSE-CODE](LICENSE-CODE) |
| 設計文書・作業ルール文書（`docs/design/`・`SKILL.md`・`README.md`） | CC BY-NC-SA 4.0 | [LICENSE-DOCS](LICENSE-DOCS) |
| テスト素材（`prototype/tests/*.musicxml`） | パブリックドメイン由来（BWV 66、Bach 1685–1750）。music21 由来の部分は帰属表示要確認 | [NOTICE](NOTICE) |
| 依存ライブラリ（music21 10.3.0） | BSD 3-Clause License | [NOTICE](NOTICE) |

> **移行経緯**: リポジトリルートの `LICENSE` ファイル（CC BY-NC-SA 4.0）は、単一ライセンス構成からこの分離構成へ移行する過程の記録として保持しています。

## 著作権・セキュリティ

- 著作権保護された譜面を GitHub へ登録しない
- GitHub 上のテスト素材はパブリックドメインに限定する
- API キー、トークン、秘密鍵、個人情報をソース、ログ、Git 管理対象へ含めない
- 外部 OMR サービスへ譜面を送信する場合は、利用規約と著作権条件を確認する
