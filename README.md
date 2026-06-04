# score-reader — MusicXML 正確性検証ツール

> リポジトリ名 `score-reader` は仮称です。

## 概要

OMR（光学楽譜認識）で画像/PDF の楽譜を MusicXML に変換したあと、その構造化データを
**「推測せず、書いてある通りに」** 読み、誤りが混入しやすい箇所を機械的に洗い出すツールです。

- 拍子と各小節の音価合計の不一致、移調楽器の記音/実音差、和音の音数など、
  目視では見落としやすい箇所を自動でチェックします。
- 曖昧・未確定な要素は黙殺せず、警告として必ず列挙します。

### 役割分担（重要）

- **画像 → MusicXML への変換は本ツールの対象外です。** 変換は外部の OMR ソフト
  （例: [Audiveris](https://github.com/Audiveris/audiveris)）で行ってください。
- 本ツールは **変換後の MusicXML の正確性検証** に専念します。
- 「正確さ」の最終責任は OMR の出力品質に依存します。本ツールはその誤りを下流で炙り出す役割です。

## 必要環境

- Python 3.12 以上
- [music21](https://web.mit.edu/music21/)（`requirements.txt` に固定: `music21==10.3.0`）

依存は仮想環境（venv）に隔離してインストールすることを強く推奨します。

> **macOS（Homebrew の Python）をお使いの方へ**
> Homebrew で導入した Python では、システム全体への `pip install` が PEP 668 により
> `externally-managed-environment` エラーで拒否されます。これは正常な挙動です。
> 下記のとおり **venv を作成し、その中でインストール** してください
> （`--break-system-packages` の使用は避けてください）。

## セットアップ

プロジェクトルートで以下を実行します。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- 作業を終えたら `deactivate` で仮想環境を抜けられます。
- 次回以降は `source .venv/bin/activate` で再び有効化するだけで使えます。

## 使い方

```bash
# 人間可読の検証レポートを出力（デフォルト）
python3 src/verify_score.py <input.musicxml>

# 検証結果を構造化 JSON で標準出力（教材システム連携などの機械処理向け）
python3 src/verify_score.py <input.musicxml> --json
```

JSON は標準出力に流れるため、ファイルへ保存する場合は次のようにします。

```bash
python3 src/verify_score.py <input.musicxml> --json > report.json
```

## 検証項目

実行すると、以下の項目が順に検査されます。

| # | 項目 | 何を検出するか |
|---|------|----------------|
| 1 | 移調楽器チェック | 各パートの管調と記音/実音の半音差を報告。移調情報の欠落も注記 |
| 2 | 小節長の検算 | 拍子から算出した期待音価と各小節の実測音価を比較。不一致を検出（アウフタクトは許容） |
| 3 | 調号の列挙 | 調号とその変化点（小節番号）を出力 |
| 4 | テンポ/拍子イベント | テンポ・拍子の変化点を小節番号順にリスト化 |
| 5 | 未確定・要確認要素 | 無音高（打楽器等）要素などを列挙。「完全無欠ではない」注記を必ず付す |
| 6 | リハーサルマーク対応表 | リハーサルマーク（練習記号）と小節番号の対応を一覧化。空内容・重複も警告 |
| 7 | 和音の音数チェック | 各和音の構成音数を報告。OMR の音抜けが疑われる箇所を炙り出す |
| 8 | パート間の小節数整合 | 各パートの小節数を比較し、不一致（小節の欠落/過剰認識の疑い）を検出。単一パートは対象外 |

> JSON 出力時のトップレベルキー: `parts`, `transposing_instruments`,
> `measure_anomalies`, `key_signatures`, `tempo_meter_events`,
> `rehearsal_marks`, `chord_voicing`, `part_measure_counts`, `unreadable`,
> `warnings`, `note`。
> WARN / ANOMALY は `warnings` 配列にも横断的に集約され、機械処理で拾えます。

### パート間の小節数整合について（項目 8）

- 複数パートのうち一部だけ小節が欠落・過剰認識されると、パート間で小節数がずれます。
  本ツールは **パート間の小節数の不一致を検出** できます。
- 不一致が出た場合は、**元譜（PDF/画像）との目視照合が必要** です。
- 本ツール単独では、**どのパートが正しいか・どの小節が欠落したか（正しい位置）は断定しません。**

## 出力の読み方

出力には 3 段階のラベルが付きます。優先度の高い順に確認してください。

| ラベル | 意味 | 優先度 |
|--------|------|--------|
| `ANOMALY` | 整合性の崩れ（例: 拍子と小節の音価合計が一致しない）。**最優先で要確認** | 高 |
| `WARN` | 曖昧・未確定・疑わしい箇所（例: 拍子記号が未確定、和音の音数がパート内で揺れる）。要目視確認 | 中 |
| `INFO` | 異常ではないが念のため共有する情報（例: 単音が和音として記譜されている） | 低 |

- まず `ANOMALY`、次に `WARN` を確認するのが基本の流れです。
- `INFO` は誤りとは限りませんが、記譜意図か OMR の取りこぼしかを判断する材料になります。

## 既知の限界

- **音高そのものの正誤は判定できません。** 本ツールは音価・拍子・移調・和音数などの
  整合性は検査できますが、OMR が誤読した音高は「正しい入力」として処理されます。
- 「異常 0 件」でも完全無欠を意味しません。
- **最終的な正確性は、元譜（PDF/画像）との目視照合で担保してください。**

## テスト

`tests/` 配下のサンプル譜はすべて **パブリックドメインの J.S. バッハ系** です。

| ファイル | 内容 |
|----------|------|
| `tests/bwv66_6.musicxml` | J.S. バッハ コラール（4声体・10小節） |
| `tests/bwv66_with_clarinet.musicxml` | 上記に Bb クラリネットを付与し、移調検出を発火させた版 |
| `tests/bwv66_with_rehearsal.musicxml` | 上記にリハーサルマーク A(m.1)・B(m.4) を付与し、項目[6]の正常系を発火させた版 |

```bash
python3 src/verify_score.py tests/bwv66_6.musicxml
python3 src/verify_score.py tests/bwv66_with_clarinet.musicxml
python3 src/verify_score.py tests/bwv66_with_rehearsal.musicxml --json
```

> **方針:** テストには著作権フリーの譜のみを使用します。市販譜（Disney 等）は
> テストに使用しません。
