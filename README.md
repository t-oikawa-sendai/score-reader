# score-reader

OMR（楽譜認識）が出力したMusicXMLの構造検査を行うCLIツールです。

> **現状**: `prototype/src/verify_score.py` はコード凍結中です。
>
> 本リポジトリでは設計文書の検証・更新を継続しています。

## 背景

OMR出力のMusicXMLは、音高・音価・声部が原本譜と一致しているかを
機械的に完全に判定できるものではありません。

score-readerは、機械的に検出できる構造的異常を列挙し、
人間が原本PDFと照合すべき箇所を絞り込むことで、確認作業を省力化します。

## 機能（現行プロトタイプ）

- MusicXMLのパース
- 移調・小節長・調号・拍子/テンポの検査
- Unpitched（無音高）要素の検出
- 和音音数・パート間小節数の検査
- テキスト / JSON 出力

## 使い方

```bash
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml
python3 prototype/src/verify_score.py prototype/tests/<file>.musicxml --json
```
