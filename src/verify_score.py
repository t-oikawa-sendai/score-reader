#!/usr/bin/env python3
"""
score-reader: MusicXML 正確性検証ツール
-------------------------------------------------
OMR(画像→MusicXML変換)後のデータを「推測せず、書いてある通りに」読み、
誤りが混入しやすい箇所を機械的に検査する。

設計原則:
  - 推測しない。読めない箇所は黙殺せず WARNING として列挙する。
  - 移調楽器は記音(written)と実音(sounding)を区別して報告する。
  - 拍子と各小節の音価合計を検算し、不一致を異常として検出する。

使い方:
  python3 verify_score.py <input.musicxml>          # 人間可読(デフォルト)
  python3 verify_score.py <input.musicxml> --json   # 構造化JSON出力
"""
import sys
import json
import argparse
from collections import Counter
from fractions import Fraction
from music21 import converter, meter, key, tempo, instrument, expressions, chord


def load(path):
    """MusicXMLを読み込む。失敗は黙殺せず即座に報告して停止。"""
    try:
        return converter.parse(path)
    except Exception as e:
        print(f"[FATAL] パース失敗: {e}")
        sys.exit(1)


def report_transposing_instruments(score):
    """[1] 移調楽器テーブル: 各パートの管調と記音/実音の差を報告。"""
    print("=== [1] 移調楽器チェック ===")
    found = False
    for i, part in enumerate(score.parts):
        instr = part.getInstrument(returnDefault=True)
        interval = getattr(instr, "transposition", None)
        name = instr.partName or instr.instrumentName or f"Part{i+1}"
        if interval is not None and interval.semitones != 0:
            found = True
            print(f"  - {name}: 移調楽器 (記音→実音 {interval.directedName}, "
                  f"{interval.semitones:+d}半音) → 実音変換時は要注意")
        else:
            print(f"  - {name}: 実音楽器(C管)または移調情報なし")
    if not found:
        print("  ※ 移調楽器は検出されず。OMR元が移調情報を欠落させている可能性に留意。")


def verify_measure_durations(score):
    """[2] 拍子・小節長の検算: 各小節の音価合計が拍子と一致するか。"""
    print("=== [2] 小節長の検算 ===")
    anomalies = 0
    for pi, part in enumerate(score.parts):
        cur_ts = None
        for m in part.getElementsByClass("Measure"):
            ts = m.timeSignature or cur_ts
            if m.timeSignature:
                cur_ts = m.timeSignature
            if ts is None:
                print(f"  [WARN] Part{pi+1} m.{m.number}: 拍子記号が未確定")
                anomalies += 1
                continue
            expected = Fraction(ts.numerator, ts.denominator) * 4  # 四分音符単位
            actual = Fraction(m.duration.quarterLength).limit_denominator(1000)
            # アウフタクト(小節先頭の不完全小節)は許容
            if actual != expected and not (m.number in (0, 1) and actual < expected):
                print(f"  [ANOMALY] Part{pi+1} m.{m.number}: "
                      f"拍子{ts.ratioString} 期待{expected} ≠ 実測{actual}")
                anomalies += 1
    print(f"  → 異常 {anomalies} 件" if anomalies else "  → 全小節OK")


def list_key_signatures(score):
    """[3] 調号の検出と変化点の列挙。"""
    print("=== [3] 調号 ===")
    part = score.parts[0]
    for ks in part.recurse().getElementsByClass(key.KeySignature):
        m = ks.measureNumber
        print(f"  - m.{m}: 調号 {ks.sharps:+d} (シャープ/フラット数)")


def list_tempo_meter_events(score):
    """[4] テンポ・拍子変化のイベントリスト化。"""
    print("=== [4] テンポ/拍子 変化イベント ===")
    part = score.parts[0]
    events = []
    for ts in part.recurse().getElementsByClass(meter.TimeSignature):
        events.append((ts.measureNumber, f"拍子 {ts.ratioString}"))
    for mm in part.recurse().getElementsByClass(tempo.MetronomeMark):
        label = mm.text or ""
        bpm = f"{mm.number}" if mm.number else "?"
        events.append((mm.measureNumber, f"テンポ {label} ♩={bpm}"))
    for m, desc in sorted(events, key=lambda x: (x[0] or 0)):
        print(f"  - m.{m}: {desc}")


def list_unreadable(score):
    """[5] 読めなかった/曖昧な要素を黙殺せず列挙。"""
    print("=== [5] 未確定・要確認 要素 ===")
    flagged = 0
    for el in score.recurse().getElementsByClass("Unpitched"):
        flagged += 1
    if flagged:
        print(f"  [INFO] 無音高(打楽器等)要素 {flagged} 個 → 音高判定は対象外")
    # music21がパース時に無視した要素はeditorial情報に残ることがある
    print("  ※ ここに列挙が無くても完全無欠の保証ではない。元PDFとの目視照合を推奨。")


def list_rehearsal_marks(score):
    """[6] リハーサルマーク↔小節番号の対応表(吹奏楽スコアで頻出)。

    各リハーサルマーク(練習番号/記号)を出現する小節番号に紐づけて列挙する。
    推測しない方針に従い、検出ゼロや重複・小節番号欠落も黙殺せず注記する。
    """
    print("=== [6] リハーサルマーク対応表 ===")
    marks = []
    seen_ids = set()
    # パートをまたいで同一マークが重複し得るため、(小節, 内容) で正規化して集約する。
    for part in score.parts:
        for rm in part.recurse().getElementsByClass(expressions.RehearsalMark):
            measure = rm.measureNumber
            content = (rm.content or "").strip()
            key_id = (measure, content)
            if key_id in seen_ids:
                continue
            seen_ids.add(key_id)
            marks.append((measure, content))

    if not marks:
        print("  ※ リハーサルマークは検出されず。曲が短い/元譜に無い、もしくは")
        print("    OMRが記号を取りこぼした可能性に留意（黙殺せず元譜と照合）。")
        return

    # 小節番号順(未確定は末尾)に並べて対応表を出力。
    marks.sort(key=lambda x: (x[0] is None, x[0] or 0))
    for measure, content in marks:
        label = content if content else "(内容不明)"
        if measure is None:
            print(f"  [WARN] マーク「{label}」: 小節番号が未確定 → 配置位置を要確認")
        elif not content:
            print(f"  [WARN] m.{measure}: リハーサルマークの内容が空 → OMR取りこぼしの疑い")
        else:
            print(f"  - m.{measure}: リハーサルマーク「{label}」")

    # 同一小節に複数マークが付く異常を検出（通常は1小節1マーク）。
    measure_counts = {}
    for measure, _ in marks:
        if measure is not None:
            measure_counts[measure] = measure_counts.get(measure, 0) + 1
    dups = sorted(m for m, c in measure_counts.items() if c > 1)
    for m in dups:
        print(f"  [WARN] m.{m}: リハーサルマークが複数検出 → 重複/誤読の疑い")
    print(f"  → 計 {len(marks)} 個のリハーサルマークを検出")


def list_chord_voicing(score):
    """[7] 和音の音数チェック(OMRの音抜け検出)。

    OMRが和音の構成音を取りこぼしても音価・拍子は保たれるためすり抜ける。
    各和音の構成音数を報告し、すり抜けやすい箇所を炙り出す。

    重要: 「何音であるべきか」は楽譜に書かれていない以上、推測しない。
    異常と断定せず INFO/WARN として列挙し、元譜照合を促すに留める。
    """
    print("=== [7] 和音の音数チェック ===")
    total = 0
    for pi, part in enumerate(score.parts):
        instr = part.getInstrument(returnDefault=True)
        name = instr.partName or instr.instrumentName or f"Part{pi+1}"
        chords = list(part.recurse().getElementsByClass(chord.Chord))
        if not chords:
            continue
        total += len(chords)

        counts = [len(c.pitches) for c in chords]
        dist = Counter(counts)
        # パート内で最も多い音数(主流)。「べき音数」の断定ではなく目安として用いる。
        dominant = dist.most_common(1)[0][0]
        dist_str = ", ".join(f"{n}音×{cnt}" for n, cnt in sorted(dist.items()))
        print(f"  [{name}] 和音 {len(chords)} 個 (内訳: {dist_str}, 主流 {dominant}音)")

        for c in chords:
            cnt = len(c.pitches)
            m = c.measureNumber
            if cnt == 1:
                print(f"    [INFO] m.{m}: 単音が和音として記譜 (1音) "
                      f"→ 記譜上の意図か音抜けか元譜で要確認")
            elif cnt != dominant:
                print(f"    [WARN] m.{m}: 音数 {cnt} がパート主流 {dominant}音 と相違 "
                      f"→ 音抜け/重複の疑い、要目視確認")

    if total == 0:
        print("  ※ 和音要素は検出されず(単声パートのみ等)。")
        print("    OMRが和音を単音化して取りこぼした可能性も否定できないため元譜と照合。")
        return
    print(f"  → 計 {total} 個の和音を検査。音数の正誤は断定不可、必ず元譜と目視照合すること。")


def _part_label(part, index):
    """パートの識別名を決定(共通)。命名規則は他セクションと揃える。"""
    instr = part.getInstrument(returnDefault=True)
    name = instr.partName or instr.instrumentName or f"Part{index+1}"
    return name


def list_part_measure_consistency(score):
    """[8] 複数パート間の小節数整合チェック(OMRの小節欠落/過剰認識検出)。

    各パートの小節数を比較し、不一致を WARN として報告する。
    推測しない方針に従い、どのパートが正しいか・どの小節が欠落したかは断定しない。
    単一パートは比較対象が無いため異常扱いせず INFO とする。
    """
    print("=== [8] 複数パート間の小節数整合チェック ===")
    counts = []
    for i, part in enumerate(score.parts):
        name = _part_label(part, i)
        n = len(part.getElementsByClass("Measure"))
        counts.append((i + 1, name, n))
        print(f"  - Part{i+1} {name}: {n} 小節")

    if len(counts) <= 1:
        print("  [INFO] パートが1つのみ。比較対象が無いため整合チェックは対象外。")
        return

    distinct = sorted({n for _, _, n in counts})
    if len(distinct) == 1:
        print(f"  → 全パートの小節数が一致 ({distinct[0]} 小節)")
    else:
        print(f"  [WARN] パート間で小節数が一致しません(検出値: {distinct})")
        print("    → OMRの小節欠落/過剰認識の疑い。元譜との目視照合が必要。")
        print("    ※ どのパートが正しいか・どの小節が欠落したかは本ツールでは断定しない。")


# =====================================================================
# JSON出力用コレクタ群
# 人間可読の print 関数とはロジックを共有せず分離し、既存出力を温存する。
# WARN/ANOMALY は各セクションのデータに加え warnings 配列にも集約する。
# =====================================================================

def collect_transposing_instruments(score, warnings):
    """[1] 移調楽器情報を構造化。"""
    rows = []
    for i, part in enumerate(score.parts):
        instr = part.getInstrument(returnDefault=True)
        interval = getattr(instr, "transposition", None)
        name = instr.partName or instr.instrumentName or f"Part{i+1}"
        if interval is not None and interval.semitones != 0:
            rows.append({
                "part": i + 1,
                "name": name,
                "transposing": True,
                "semitones": interval.semitones,
                "directed_name": interval.directedName,
            })
        else:
            rows.append({
                "part": i + 1,
                "name": name,
                "transposing": False,
                "semitones": 0,
                "directed_name": None,
            })
    return rows


def collect_measure_anomalies(score, warnings):
    """[2] 小節長の検算結果(WARN/ANOMALYのみ)を構造化。"""
    rows = []
    for pi, part in enumerate(score.parts):
        cur_ts = None
        for m in part.getElementsByClass("Measure"):
            ts = m.timeSignature or cur_ts
            if m.timeSignature:
                cur_ts = m.timeSignature
            if ts is None:
                entry = {
                    "part": pi + 1, "measure": m.number, "level": "WARN",
                    "message": "拍子記号が未確定",
                }
                rows.append(entry)
                warnings.append({
                    "section": 2, "level": "WARN", "part": pi + 1,
                    "measure": m.number, "message": "拍子記号が未確定",
                })
                continue
            expected = Fraction(ts.numerator, ts.denominator) * 4
            actual = Fraction(m.duration.quarterLength).limit_denominator(1000)
            if actual != expected and not (m.number in (0, 1) and actual < expected):
                msg = f"拍子{ts.ratioString} 期待{expected} ≠ 実測{actual}"
                entry = {
                    "part": pi + 1, "measure": m.number, "level": "ANOMALY",
                    "ratio": ts.ratioString, "expected": str(expected),
                    "actual": str(actual), "message": msg,
                }
                rows.append(entry)
                warnings.append({
                    "section": 2, "level": "ANOMALY", "part": pi + 1,
                    "measure": m.number, "message": msg,
                })
    return rows


def collect_key_signatures(score, warnings):
    """[3] 調号を構造化。"""
    part = score.parts[0]
    return [
        {"measure": ks.measureNumber, "sharps": ks.sharps}
        for ks in part.recurse().getElementsByClass(key.KeySignature)
    ]


def collect_tempo_meter_events(score, warnings):
    """[4] テンポ/拍子イベントを構造化(小節番号順)。"""
    part = score.parts[0]
    events = []
    for ts in part.recurse().getElementsByClass(meter.TimeSignature):
        events.append({
            "measure": ts.measureNumber, "type": "time_signature",
            "description": f"拍子 {ts.ratioString}", "value": ts.ratioString,
        })
    for mm in part.recurse().getElementsByClass(tempo.MetronomeMark):
        label = mm.text or ""
        events.append({
            "measure": mm.measureNumber, "type": "tempo",
            "description": f"テンポ {label} ♩={mm.number if mm.number else '?'}",
            "bpm": mm.number, "text": label or None,
        })
    return sorted(events, key=lambda e: (e["measure"] or 0))


def collect_rehearsal_marks(score, warnings):
    """[6] リハーサルマークを構造化。WARN(空内容/小節未確定/重複)も集約。"""
    marks = []
    seen_ids = set()
    for part in score.parts:
        for rm in part.recurse().getElementsByClass(expressions.RehearsalMark):
            measure = rm.measureNumber
            content = (rm.content or "").strip()
            key_id = (measure, content)
            if key_id in seen_ids:
                continue
            seen_ids.add(key_id)
            marks.append((measure, content))

    marks.sort(key=lambda x: (x[0] is None, x[0] or 0))
    rows = []
    for measure, content in marks:
        rows.append({"measure": measure, "content": content})
        if measure is None:
            warnings.append({
                "section": 6, "level": "WARN", "measure": None,
                "message": f"リハーサルマーク「{content or '(内容不明)'}」の小節番号が未確定",
            })
        elif not content:
            warnings.append({
                "section": 6, "level": "WARN", "measure": measure,
                "message": "リハーサルマークの内容が空(OMR取りこぼしの疑い)",
            })

    measure_counts = {}
    for measure, _ in marks:
        if measure is not None:
            measure_counts[measure] = measure_counts.get(measure, 0) + 1
    for m in sorted(mn for mn, c in measure_counts.items() if c > 1):
        warnings.append({
            "section": 6, "level": "WARN", "measure": m,
            "message": "リハーサルマークが複数検出(重複/誤読の疑い)",
        })
    return rows


def collect_chord_voicing(score, warnings):
    """[7] 和音の音数を構造化。WARN(主流と相違)を集約、単音はINFOフラグ。"""
    parts_data = []
    for pi, part in enumerate(score.parts):
        instr = part.getInstrument(returnDefault=True)
        name = instr.partName or instr.instrumentName or f"Part{pi+1}"
        chords = list(part.recurse().getElementsByClass(chord.Chord))
        if not chords:
            continue
        counts = [len(c.pitches) for c in chords]
        dist = Counter(counts)
        dominant = dist.most_common(1)[0][0]
        items = []
        for c in chords:
            cnt = len(c.pitches)
            m = c.measureNumber
            flag = None
            if cnt == 1:
                flag = "INFO"
            elif cnt != dominant:
                flag = "WARN"
                warnings.append({
                    "section": 7, "level": "WARN", "part": pi + 1, "measure": m,
                    "message": f"音数 {cnt} がパート主流 {dominant}音 と相違"
                               "(音抜け/重複の疑い)",
                })
            items.append({"measure": m, "count": cnt, "flag": flag})
        parts_data.append({
            "part": pi + 1,
            "name": name,
            "total": len(chords),
            "dominant": dominant,
            "distribution": {str(n): cnt for n, cnt in sorted(dist.items())},
            "items": items,
        })
    return parts_data


def collect_unreadable(score, warnings):
    """[5] 未確定要素を構造化。完全性は主張しない注記を付す。"""
    unpitched = len(list(score.recurse().getElementsByClass("Unpitched")))
    return {
        "unpitched_count": unpitched,
        "note": "列挙が無くても完全無欠の保証ではない。元PDFとの目視照合を推奨。",
    }


def collect_part_measure_counts(score, warnings):
    """[8] パート間の小節数整合を構造化。不一致は WARN を warnings にも集約。

    正しいパート・欠落位置は断定しない。単一パートは不一致扱いしない。
    """
    parts = []
    for i, part in enumerate(score.parts):
        parts.append({
            "part": i + 1,
            "name": _part_label(part, i),
            "measures": len(part.getElementsByClass("Measure")),
        })

    distinct = sorted({p["measures"] for p in parts})
    single_part = len(parts) <= 1
    consistent = single_part or len(distinct) == 1

    warning_msg = None
    if not consistent:
        warning_msg = (
            f"パート間で小節数が一致しない(検出値: {distinct})。"
            "OMRの小節欠落/過剰認識の疑い。正しいパート・欠落位置は断定不可、元譜と目視照合。"
        )
        warnings.append({
            "section": 8, "level": "WARN", "measure": None,
            "message": warning_msg,
        })

    return {
        "parts": parts,
        "consistent": consistent,
        "single_part": single_part,
        "distinct_counts": distinct,
        "warning": warning_msg,
    }


def build_report(score):
    """検証[1]〜[8]を構造化辞書に集約する。WARN/ANOMALYは warnings にも集約。"""
    warnings = []
    report = {
        "parts": len(score.parts),
        "transposing_instruments": collect_transposing_instruments(score, warnings),
        "measure_anomalies": collect_measure_anomalies(score, warnings),
        "key_signatures": collect_key_signatures(score, warnings),
        "tempo_meter_events": collect_tempo_meter_events(score, warnings),
        "rehearsal_marks": collect_rehearsal_marks(score, warnings),
        "chord_voicing": collect_chord_voicing(score, warnings),
        "unreadable": collect_unreadable(score, warnings),
        "part_measure_counts": collect_part_measure_counts(score, warnings),
        "warnings": warnings,
        "note": "音価・拍子・移調の整合性検査であり音高の正誤は判定不可。"
                "ANOMALY/WARN を最優先で確認し、最終的に元譜と目視照合すること。",
    }
    return report


def run_human_readable(score):
    """既存の人間可読出力(デフォルト)。"""
    print(f"読込成功: パート数 {len(score.parts)}\n")
    report_transposing_instruments(score)
    verify_measure_durations(score)
    list_key_signatures(score)
    list_tempo_meter_events(score)
    list_rehearsal_marks(score)
    list_chord_voicing(score)
    list_part_measure_consistency(score)
    list_unreadable(score)
    print("\n--- 検証完了。ANOMALY/WARN を最優先で確認すること。 ---")


def main():
    parser = argparse.ArgumentParser(
        description="MusicXML 正確性検証ツール (OMR出力の下流検査)")
    parser.add_argument("input", help="入力 MusicXML ファイル")
    parser.add_argument("--json", action="store_true",
                        help="検証[1]〜[8]の結果を構造化JSONで標準出力する")
    args = parser.parse_args()

    score = load(args.input)
    if args.json:
        report = build_report(score)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        run_human_readable(score)


if __name__ == "__main__":
    main()
