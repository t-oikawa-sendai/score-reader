# UI and Flow Design（UI・フロー設計）

<!-- Document Info（文書情報） -->
| Item（項目） | Value（値） |
|---|---|
| Document ID（文書ID） | UI-001 |
| Version（バージョン） | 0.2 |
| Status（ステータス） | Draft |
| Created Date（作成日） | 2026-06-09 |
| Last Updated（最終更新日） | 2026-06-28 |
| Owner（管理者） | Takashi Oikawa |
| Related Documents（関連文書） | README.md / 02_REQUIREMENTS_DEFINITION.md / 03_DATA_AND_SECURITY_DESIGN.md / 05_ARCHITECTURE_DESIGN.md / legacy/SCORE_READER_BASIC_DESIGN.md / legacy/MULTI_OMR_BASIC_DESIGN.md |

---

## Table of Contents（目次）

1. [Purpose（目的）](#1-purpose目的)
2. [Scope（対象範囲）](#2-scope対象範囲)
3. [Out of Scope（対象外範囲）](#3-out-of-scope対象外範囲)
4. [Assumptions（前提条件）](#4-assumptions前提条件)
5. [Definition Details（定義内容）](#5-definition-details定義内容)
6. [Open Issues（未決事項）](#6-open-issues未決事項)
7. [Handoff to Detail Design（詳細設計への引き継ぎ）](#7-handoff-to-detail-design詳細設計への引き継ぎ)
8. [Change History（変更履歴）](#8-change-history変更履歴)

---

## 1. Purpose（目的）

本設計書群は、完成版 MusicXML 作成支援システムへ到達するための検証結果・設計判断・未確定事項を整理したプロトタイプ段階の設計ガイドラインである。本文書は**プロトタイプ検証段階**における `verify_score.py`（単一 MusicXML 構造検査の検証実装）の CLI 操作フロー・出力確認フロー・人間レビューフローを定義し、実装・運用フェーズの基準とすることを目的とする。

将来本実装候補（複数 MusicXML 比較、差分可視化、比較レポート生成）の操作フローは、本文書の Open Issues で管理する。最終的な正確性の担保は人間による原本 PDF 照合で行う。本文書の対象読者は、設計者・実装者・利用者・プロジェクトオーナーである。

---

## 2. Scope（対象範囲）

| 対象 | 内容 |
|---|---|
| CLI インターフェース | コマンドライン引数・実行コマンド・出力形式の選択 |
| ユーザー操作フロー | 著作権確認 → 外部 OMR 実行 → score-reader 実行 → 出力確認 → 人間レビュー |
| 出力確認フロー | テキスト出力・JSON 出力の読み取り方・警告・異常の判断方針 |
| 人間レビューフロー | score-reader 出力を受けた後、MuseScore 等で原本 PDF と照合する作業フロー |
| エラー・警告処理フロー | `[FATAL]` / `[ANOMALY]` / `[WARN]` の対処フロー |
| 著作権・ライセンス確認フロー | 外部 OMR サービス利用前・テスト素材追加前の確認手順 |

---

## 3. Out of Scope（対象外範囲）

| 対象外項目 | 理由 |
|---|---|
| GUI 画面設計・ワイヤーフレーム | score-reader は CLI ツールであり、画面を持たない |
| Web UI・モバイル UI | プロトタイプ検証段階は CLI のみ対象とする |
| 原本 PDF 横並び画面 | 自動修正、自動統合、Web UI、原本 PDF 横並び画面は、現時点で定義する本実装段階には含めず、将来検討事項として扱う |
| MusicXML 自動修正 UI | 同上。score-reader は検査結果の出力のみ |
| 外部 OMR サービスの操作 UI | score-reader のスコープ外 |
| 完全自動化フロー（人間確認を省略するフロー） | 設計原則に反する |

---

## 4. Assumptions（前提条件）

本文書の内容が成立するために必要な前提は `01_REQUEST_DEFINITION.md` §4 を継承する。以下は UI・フロー設計フェーズで追加する前提を示す。

- 利用者は Python 実行環境・仮想環境のセットアップが完了していること（環境構築手順は `06_OPERATION_AND_HANDOFF.md` に記載）
- 利用者は MuseScore 等の楽譜編集ソフトを別途用意し、原本 PDF との照合を行う意図があること
- score-reader の CLI 出力は「確認対象情報」であり、正解として採用しないこと
- 本プロジェクトのライセンスは **CC BY-NC-SA 4.0**（LICENSE ファイル参照）
- 本文書の v0.1 日付は、移行元 Legacy Source（`legacy/SCORE_READER_BASIC_DESIGN.md`）の初版コミット日（2026-06-07）を引き継ぐ

---

## 5. Definition Details（定義内容）

### 5.1 Screen List — Detail Definition（画面一覧・詳細定義）

プロトタイプ検証段階は GUI を持たないため、画面一覧は対象外とする。代わりに CLI インターフェース仕様を定義する。

| Screen ID（画面ID） | Screen Name（画面名） | Input Items（入力項目） | Output Items（出力項目） | Main Operations（主要操作） | Notes（備考） |
|---|---|---|---|---|---|
| CLI-001 | verify_score.py 実行 | 第 1 引数: MusicXML ファイルパス。任意: `--json` | 標準出力: 検査結果（テキスト or JSON）。終了コード 0/1 | 検査実行・出力確認 | 実行ファイル: `prototype/src/verify_score.py` |

#### 引数・フラグ

| 引数 / フラグ | 必須 | 内容 |
|---|---|---|
| `input`（第 1 引数） | 必須 | 検査対象 MusicXML ファイルパス |
| `--json` | 任意 | JSON 形式で標準出力 |

#### 実行コマンド例

```bash
python3 verify_score.py ../tests/<file>.musicxml
python3 verify_score.py ../tests/<file>.musicxml --json
python3 verify_score.py ../tests/<file>.musicxml --json > result.json
```

### 5.2 Screen Transition and Business Flow（画面遷移図・業務フロー）

画面遷移は対象外（CLI ツールのため）。業務フロー全体を以下に示す。

```mermaid
flowchart TD
    A[["① 著作権・ライセンス確認"]]
    B[["② 外部 OMR で PDF → MusicXML"]]
    C[["③ score-reader 実行"]]
    D{{"パース成功？"}}
    E[["[FATAL] 終了コード 1"]]
    F{{"[ANOMALY] / [WARN] あり？"}}
    G[["④-A 警告・異常箇所を特定"]]
    H[["④-B 警告なし（完全無欠を保証しない）"]]
    I[["⑤ MuseScore 等で原本 PDF と照合"]]
    J[["⑥ 修正完了（必要に応じ再検査）"]]

    A --> B --> C --> D
    D -- No --> E
    D -- Yes --> F
    F -- Yes --> G --> I
    F -- No --> H --> I
    I --> J
```

| 事項 | 内容 |
|---|---|
| 完全自動化禁止 | 人間確認を省略して完了する分岐を設けない |
| 警告なし≠正確 | `[WARN]` / `[ANOMALY]` 0 件でも原本 PDF 照合（⑤）を省略しない |
| OMR 出力は確認対象 | ② の MusicXML を正解として扱わない |

### 5.3 Wireframes and Layout Policy（主要画面のワイヤーフレーム・レイアウト方針）

本文書では対象外。理由: プロトタイプ検証段階は CLI ツールであり、画面・レイアウト・原本 PDF 横並び UI を持たない。

### 5.4 Operation Flow and User Scenarios（操作フロー・ユーザーシナリオ）

| Scenario ID（シナリオID） | Operation Name（操作名） | Steps（操作手順） |
|---|---|---|
| SC-001 | 基本検査フロー（テキスト出力） | 1. リポジトリルートで仮想環境を有効化 → 2. `cd prototype/src` → 3. `python3 verify_score.py ../tests/<file>.musicxml` → 4. 出力の `[ANOMALY]` / `[WARN]` を記録 → 5. MuseScore 等で原本 PDF と照合 |
| SC-002 | JSON 出力フロー | 1. SC-001 と同様の前提 → 2. `--json` 指定で実行 → 3. 必要に応じリダイレクトで保存 → 4. 後工程または照合作業で参照 |
| SC-003 | 入力ファイル選択フロー | 1. 著作権状況を確認 → 2. 外部 OMR 出力 MusicXML を用意 → 3. ファイルパスを第 1 引数に指定 |
| SC-004 | 出力確認フロー | 1. `[FATAL]`: OMR 再実行または形式確認 → 2. `[ANOMALY]`: 該当小節を最優先照合 → 3. `[WARN]`: リストアップして原本 PDF 照合 → 4. 警告 0 件: 完全無欠を保証しない旨を確認し照合を省略しない |
| SC-005 | 人間レビューフロー | 1. 警告・異常箇所を整理 → 2. MuseScore で MusicXML を開く → 3. 原本 PDF と目視照合・修正 → 4. 必要に応じ score-reader を再実行 |

#### 著作権確認チェック（SC-003 補足）

```
□ 対象楽譜の著作権状況を確認した
□ 外部 OMR サービスの利用規約を確認した
□ テスト素材追加時はパブリックドメインのみとした
```

### 5.5 Validation and Error Handling Policy（バリデーション・エラーハンドリング方針 / UI層）

| Target（対象） | Validation Rules（バリデーションルール） | Error Message / Display Policy（エラーメッセージ・表示方針） |
|---|---|---|
| 入力ファイルパス | ファイルが存在し、`music21.converter.parse` が読み込める形式であること | パース失敗: `[FATAL]` を出力し終了コード 1 |
| `--json` フラグ | 指定・未指定いずれも有効 | 無効なフラグ: `argparse` 標準エラー |

| 出力レベル | 利用者の対処フロー |
|---|---|
| `[FATAL]` | OMR 再実行・MusicXML 形式確認・手動対応を検討 |
| `[ANOMALY]` | 該当小節を最優先で原本 PDF 照合 |
| `[WARN]` | 警告箇所をリストアップし原本 PDF 照合 |
| `[INFO]` | 必要に応じて確認 |
| 警告・異常なし | 原本 PDF 照合を省略しない |

### 5.6 Accessibility and Responsive Design Policy（アクセシビリティ・レスポンシブ対応方針）

本文書では対象外。理由: プロトタイプ検証段階は CLI ツールであり、GUI・画面を持たない。

---

## 6. Open Issues（未決事項）

| ID | Open Issue（未決事項） | Owner（担当者） | Due Date（期限） | Status（ステータス） |
|---|---|---|---|---|
| TBD-001 | 将来検討事項で複数 MusicXML 比較機能を実装する場合の CLI フロー（引数設計・出力形式）を定義するか。 | Takashi Oikawa | 未定 | Open |
| TBD-002 | `[WARN]` / `[ANOMALY]` の優先度付けフローを設計書として定義するか。 | Takashi Oikawa | 未定 | Open |
| TBD-003 | 著作権確認チェックリストを正式化・運用化するか。 | Takashi Oikawa | 未定 | Open |

---

## 7. Handoff to Detail Design（詳細設計への引き継ぎ）

1. **「警告なし＝正確」の誤解防止**: `[WARN]` / `[ANOMALY]` 0 件でも「完全無欠を保証しない」注記を必ず出力に含めること。
2. **終了コードの徹底**: パース成功 0、パース失敗 1。
3. **CLI 引数変更時は本文書を更新**: 引数・フラグ追加時は §5.1 と SC シナリオを更新すること。
4. **著作権確認フローの周知**: 利用者向けドキュメントに実行前の著作権確認を明示すること。

---

## 8. Change History（変更履歴）

| Version（バージョン） | Date（日付） | Changes（変更内容） | Author（変更者） |
|---|---|---|---|
| 0.1 | 2026-06-09 | 初版作成 | Takashi Oikawa |
| 0.2 | 2026-06-28 | legacy/04 を内容抽出元として正本記入・開発段階分類表記統一 | Takashi Oikawa |
