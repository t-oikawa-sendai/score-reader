# プロジェクト対象範囲

本書は、`score-reader` の対象範囲と対象外、およびリポジトリ再整備における変更範囲を整理する。

基本設計の正本は [SCORE_READER_BASIC_DESIGN.md](../design/SCORE_READER_BASIC_DESIGN.md) を参照すること。

## プロジェクトの対象範囲（Phase 1）

[基本設計書 第5章](../design/SCORE_READER_BASIC_DESIGN.md#5-対象範囲) に基づき、Phase 1 では以下を行う。

- 複数 MusicXML の入力
- 各 MusicXML の単体構造検査
- 比較前の正規化
- 比較可能性の判定
- 差分比較
- 一致箇所、要確認箇所、比較不能箇所の分類
- 記譜上の高リスク領域の抽出
- 比較レポートの生成

Phase 1 の終了点は **比較レポートの生成** である。

## プロジェクトの対象外（Phase 1）

[基本設計書 第6章](../design/SCORE_READER_BASIC_DESIGN.md#6-対象外) に基づき、Phase 1 では以下を行わない。

- 原本 PDF との照合
- 人間による採用元選択
- 人間による手修正
- 再比較ループ
- MusicXML の自動修正、書換え
- 自動統合、半自動統合
- 多数決による自動採用
- Web UI
- 原本 PDF との横並び画面
- MuseScore 書換え
- アラート付き派生 MusicXML の生成

## 今回のリポジトリ再整備で実施する範囲

文書構造と README の再整備、および現行プロトタイプ関連ファイルの再配置を行う。
プロトタイプ関連ファイルは内容を変更せず、prototype/ 配下へ移動する。

| 区分 | 内容 |
|---|---|
| 新規作成 | `docs/design/SCORE_READER_BASIC_DESIGN.md` |
| 新規作成 | `docs/project/PROJECT_SCOPE.md`（本書） |
| 新規作成 | `docs/project/DEVELOPMENT_PHASES.md` |
| 新規作成 | `docs/project/OPEN_ISSUES.md` |
| 修正 | `README.md`（プロジェクト入口として再構成） |
| 既存資料として残す | `docs/design/MULTI_OMR_BASIC_DESIGN.md` |
| 再配置 | `requirements.txt` → `prototype/requirements.txt` |
| 再配置 | `src/verify_score.py` → `prototype/src/verify_score.py` |
| 再配置 | `tests/` → `prototype/tests/` |

## 今回の変更禁止範囲

再配置完了後、以下は内容変更、追加移動、改名、削除を行わない。

| パス | 理由 |
|---|---|
| `SKILL.md` | 位置づけ整理は後工程 |
| `prototype/requirements.txt` | 依存関係定義の整理は後工程 |
| `prototype/src/verify_score.py` | 現行ソースは技術検証用プロトタイプ。改修しない |
| `prototype/tests/` | テスト素材・構成の整理は後工程 |
| `.gitignore` | 今回の対象外 |
| `docs/design/MULTI_OMR_BASIC_DESIGN.md` | 移行元資料として残す |

以下の作業も実施しない。

- ソースコード改修
- テスト追加
- 依存ライブラリ変更
- 詳細設計
- 機能追加
- ファイル削除
