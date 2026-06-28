# SKILL: score-reader 作業ルール

## 1. 本書の位置づけ

本書は、今後の設計、実装、検証作業で遵守する作業ルールを定義する。

本書は基本設計書ではない。

設計上の判断は、正本となる設計文書（§2 参照）を優先する。

本書と正本設計書（§2）が矛盾する場合は、作業を停止する。

## 2. 正本となる設計文書

正本:

- [README.md](README.md)（設計Doc群のインデックス・全体方針）
- [docs/design/01_REQUEST_DEFINITION.md](docs/design/01_REQUEST_DEFINITION.md)
- [docs/design/02_REQUIREMENTS_DEFINITION.md](docs/design/02_REQUIREMENTS_DEFINITION.md)
- [docs/design/03_DATA_AND_SECURITY_DESIGN.md](docs/design/03_DATA_AND_SECURITY_DESIGN.md)
- [docs/design/04_UI_AND_FLOW_DESIGN.md](docs/design/04_UI_AND_FLOW_DESIGN.md)
- [docs/design/05_ARCHITECTURE_DESIGN.md](docs/design/05_ARCHITECTURE_DESIGN.md)
- [docs/design/06_OPERATION_AND_HANDOFF.md](docs/design/06_OPERATION_AND_HANDOFF.md)

## 3. 利用方法

### 3.1 配置場所

本書は、リポジトリルートに配置する。

```text
score-reader/
└── SKILL.md
```

別のディレクトリへ移動しない。
ファイル名も変更しない。

### 3.2 目的

本書は、Cursor 等へ作業を依頼する際に読み込ませる作業ルールである。

本書には、今後の設計、実装、修正、検証で守るべきルール、変更禁止範囲、停止条件を記載する。

本書は、基本設計書の代替ではない。
本書だけを参照して、仕様を追加、変更、補完してはいけない。

### 3.3 Cursor での利用方法

Cursor へ作業を依頼する際は、作業開始前に本書を読み込ませる。

作業依頼では、以下の文書も併せて確認させる。

```text
SKILL.md
README.md
docs/design/01_REQUEST_DEFINITION.md
docs/design/02_REQUIREMENTS_DEFINITION.md
docs/design/03_DATA_AND_SECURITY_DESIGN.md
docs/design/04_UI_AND_FLOW_DESIGN.md
docs/design/05_ARCHITECTURE_DESIGN.md
docs/design/06_OPERATION_AND_HANDOFF.md
```

各文書の役割は以下のとおりとする。

| 文書 | 役割 |
|------|------|
| `SKILL.md` | 作業ルール、禁止事項、停止条件 |
| `README.md` | 設計Doc群のインデックス・全体方針（正本） |
| `docs/design/01_REQUEST_DEFINITION.md` | 要求定義（正本） |
| `docs/design/02_REQUIREMENTS_DEFINITION.md` | 要件定義（正本） |
| `docs/design/03_DATA_AND_SECURITY_DESIGN.md` | データ・セキュリティ設計（正本） |
| `docs/design/04_UI_AND_FLOW_DESIGN.md` | UI・フロー設計（正本） |
| `docs/design/05_ARCHITECTURE_DESIGN.md` | アーキテクチャ設計（正本） |
| `docs/design/06_OPERATION_AND_HANDOFF.md` | 運用・引き継ぎ設計（正本） |

### 3.4 参照する工程

以下の工程では、本書を必ず参照する。

- 設計確認
- 実装
- 修正
- 検証
- commit 前確認
- push 前確認

### 3.5 矛盾を検出した場合

本書と正本設計書が矛盾する場合は、正本設計書（§2 参照）を優先する。

ただし、Cursor が独自判断で修正してはいけない。
作業を停止し、矛盾点だけを報告する。

未確定事項を推測で補完してはいけない。

## 4. プロジェクトの目的

- OMR により生成された MusicXML の誤りが混入しやすい箇所を機械的に検査する。
- 疑わしい箇所、判定不能箇所を黙殺しない。
- 人間が確認すべき箇所へ優先順位を付ける。
- アラートがない箇所について、誤認識が存在しないことを保証しない。
- 最終的な品質保証には、原本 PDF との照合を必要とする。

## 5. 必須遵守事項

- 推測による自動補完を行わない。
- 読み取れない、判断できない箇所を正常扱いしない。
- 要確認箇所、保留として明示する。
- 多数決だけで正解を確定しない。
- 原本 PDF を正本として保持する。
- 入力 MusicXML を直接上書きしない。
- 異常 0 件でも完全無欠と主張しない。
- アラートなしを安全宣言として扱わない。
- 検査不能、解析不能、入力不足を黙殺しない。

## 6. 変更禁止範囲

以下は行わない。

- MusicXML の自動修正
- MusicXML の書換え
- 原本 PDF との自動照合
- MuseScore 書換え
- アラート付き派生 MusicXML の生成

## 7. 現行プロトタイプの扱い

現行プロトタイプの配置:

```text
prototype/src/verify_score.py
prototype/requirements.txt
prototype/tests/
```

現行プロトタイプについて:

- 単一 MusicXML の構造検査が技術的に可能か確認するためのテストプログラムである。
- 正式実装ではない。
- 現段階では改修しない。
- 再利用、置換、廃止の判断は詳細設計後に行う。
- 現行プロトタイプの検査項目 `[1]`〜`[8]` の一覧は、[docs/design/06_OPERATION_AND_HANDOFF.md](docs/design/06_OPERATION_AND_HANDOFF.md) §5.1「プロトタイプ検証項目（技術検証済み [1]〜[8]）」を参照する。これらは正式仕様ではなく、`prototype/src/verify_score.py` で確認済みの技術検証項目である。

## 8. 検証ルール

- 作業前にバックアップを作成する。
- 変更前後の Git 状態を確認する。
- 変更対象と変更禁止対象を明確にする。
- プロトタイプ関連ファイルを変更する場合は、変更前後の SHA-256 を確認する。
- 正本設計書（§2）との整合性を確認する。
- commit 前に差分を確認する。
- push 前に作業ツリーがクリーンであることを確認する。
- 仕様不一致、破壊的変更、秘匿情報、著作権上の問題を検出した場合は停止する。

## 9. セキュリティ・著作権

- API キー、パスワード、トークン、秘密鍵、個人情報を、ソース、ログ、Git 管理対象へ含めない。
- 著作権保護された譜面を GitHub へ登録しない。
- GitHub 上のテスト素材は、パブリックドメインに限定する。
- 外部 OMR サービスへ譜面を送信する場合は、利用規約と著作権条件を確認する。
- 市販譜由来の中間ファイルの保存場所と管理方法は、詳細設計前に確定する。

## 10. 環境

リポジトリ名は `score-reader` として確定している。

## 11. 停止条件

以下に該当した場合は、作業を停止する。

- 正本となる基本設計書と矛盾する。
- 未確定事項を確定事項として扱う必要がある。
- 承認済みの変更範囲を超えるソースコード変更が必要になる。
- 承認のないファイル削除、破壊的変更、上書きが必要になる。
- 秘匿情報を検出する。
- 著作権保護データを検出する。
- commit または push の判断が必要になる。

停止時は、問題点と判断が必要な事項だけを報告する。
