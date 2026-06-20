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
| [docs/design/MULTI_OMR_BASIC_DESIGN.md](docs/design/MULTI_OMR_BASIC_DESIGN.md) | OMR サービスの概要、精度・誤認識傾向、複数 OMR 比較が必要な理由 |
| [docs/design/SCORE_READER_BASIC_DESIGN.md](docs/design/SCORE_READER_BASIC_DESIGN.md) | `verify_score.py` プロトタイプのプログラム仕様書 |
| [SKILL.md](SKILL.md) | Cursor 等へ作業を依頼する際の作業ルール（変更時は別途指示） |

Cursor 等へ作業を依頼する際は、最初に [SKILL.md](SKILL.md) を読み込ませ、上記設計文書も確認させてください。

## リポジトリ構成

```text
score-reader/
├── README.md
├── SKILL.md
├── LICENSE
├── .gitignore
├── docs/
│   └── design/
│       ├── MULTI_OMR_BASIC_DESIGN.md
│       └── SCORE_READER_BASIC_DESIGN.md
└── prototype/
    ├── src/
    │   └── verify_score.py
    ├── tests/
    │   └── *.musicxml
    └── requirements.txt
```

## 著作権・セキュリティ

- 著作権保護された譜面を GitHub へ登録しない
- GitHub 上のテスト素材はパブリックドメインに限定する
- API キー、トークン、秘密鍵、個人情報をソース、ログ、Git 管理対象へ含めない
- 外部 OMR サービスへ譜面を送信する場合は、利用規約と著作権条件を確認する
