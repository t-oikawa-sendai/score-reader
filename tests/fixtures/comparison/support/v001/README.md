# 補助境界ケース v001

2026-11-01 Work自作。承認済み15ケースに追加した実装の境界確認用であり、15ケースの期待結果の置換ではない。

- multivoice: 第1小節先頭だけvoice2。第1小節不能、次小節継続。
- invalid-duration: 第1音durationをinvalid。第1小節不能、次小節継続。
- tuplet: 第1音3:2表示。存在を保持、音価不能、P1へ昇格しない。
- grace: 第1音装飾音。時間軸不能を明示。
- microtone: 第1音alter0.5。記音/実音不能、種類/音価は比較。
- other-part-continues: 同名パートのP1のみ小節2を除去。P2の4小節継続。
- invalid/doctype/timewise: 壊れたXML/未対応宣言/未対応ルート。入力不能。
- aggregation.json: 同一場所のP2+UとP2+P1。既知最上位とU有無保持。小節全体との混同禁止。

旧版不変。修正時はv002等へ追加し理由を記録する。
