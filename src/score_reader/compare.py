"""MusicXML comparison. No fixture metadata, network, or file writes are used."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

RULE_VERSION = 'initial-2026-11-01-v1'
LIMITS = [
    '2入力・非圧縮score-partwise。対応可能な各パート1譜表・1声部が初回対象。',
    'タイ結合・連符・装飾音・多声部・複数小節休符の意味的な同一視は未対応。',
    '音高・音価・種類・和音・臨時記号表示以外（強弱・歌詞・奏法等）の内容比較は未対応。',
    '原本PDF位置は不明。原本との正誤判定・自動修正は行わない。',
    '差分0・比較一致でも完全無欠を保証しない。最終確認には人間による原本PDF照合が必要。',
    '人工データの動作検証は実OMRの精度・確認時間の効果を証明しない。',
]
STEPS = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
ACCIDENTALS = {'natural': 0, 'sharp': 1, 'flat': -1, 'double-sharp': 2,
               'sharp-sharp': 2, 'flat-flat': -2}
TYPE_LENGTH = {'whole': Fraction(4), 'half': Fraction(2), 'quarter': Fraction(1),
               'eighth': Fraction(1, 2), '16th': Fraction(1, 4), '32nd': Fraction(1, 8),
               '64th': Fraction(1, 16), '128th': Fraction(1, 32)}


def rational(text):
    if text is None:
        raise ValueError('required numeric value missing')
    return Fraction(text.strip())


def whole(text):
    value = rational(text)
    if value.denominator != 1:
        raise ValueError('integer required')
    return int(value)


@dataclass
class Member:
    pitch: tuple | None
    duration: Fraction | None
    display: str | None
    source: int
    pitch_error: str | None = None
    risks: list[str] = field(default_factory=list)
    original: dict = field(default_factory=dict)


@dataclass
class Event:
    start: Fraction
    kind: str
    members: list[Member]
    voice: str | None
    staff: str | None


@dataclass
class Measure:
    number: str | None
    index: int
    meter: Fraction | None
    transpose: int | None
    events: list[Event]
    length: Fraction | None
    error: str | None = None
    presence: list[dict] = field(default_factory=list)
    context: dict = field(default_factory=dict)


@dataclass
class Part:
    id: str | None
    name: str | None
    index: int
    measures: list[Measure]
    staff_count: int | None


@dataclass
class Score:
    parts: list[Part]
    sha256: str


def read_score(path: str | Path) -> Score:
    raw = Path(path).read_bytes()
    # Prevent entity expansion and external-resource declarations without a dependency.
    if b'<!DOCTYPE' in raw.replace(b'\x00', b'').upper() or b'<!ENTITY' in raw.replace(b'\x00', b'').upper():
        raise ValueError('DTD/entity declarations are outside the supported input format')
    root = ET.fromstring(raw)
    for node in root.iter():
        if node.tag.startswith('{'):
            namespace, tag = node.tag[1:].split('}', 1)
            if namespace != 'http://www.musicxml.org/ns/musicxml':
                raise ValueError('unsupported XML namespace')
            node.tag = tag
    if root.tag != 'score-partwise':
        raise ValueError('only uncompressed score-partwise is supported')
    entries = root.findall('part-list/score-part')
    ids = Counter(n.get('id') for n in entries)
    names = {n.get('id'): n.findtext('part-name') for n in entries if ids[n.get('id')] == 1}
    parts = []
    for index, node in enumerate(root.findall('part'), 1):
        state = {'divisions': None, 'meter': None, 'transpose': None, 'fifths': None,
                 'staves': None, 'context_error': None}
        measures = [read_measure(m, i, state) for i, m in enumerate(node.findall('measure'), 1)]
        counts = {m.context.get('staves') for m in measures}
        parts.append(Part(node.get('id'), names.get(node.get('id')), index, measures,
                          1 if counts == {1} else None))
    if not parts:
        raise ValueError('no parts available')
    return Score(parts, hashlib.sha256(raw).hexdigest())


def read_measure(node, index, state):
    cursor = Fraction(0)
    events = []
    presence = []
    error = None
    accidental_context = {}
    for element in node:
        tag = element.tag
        if tag == 'attributes':
            if cursor:
                error = '小節途中の属性変更は初回対応外'
            for key, xml_tag in [('divisions', 'divisions'), ('staves', 'staves')]:
                if element.find(xml_tag) is not None:
                    try:
                        value = whole(element.findtext(xml_tag))
                        state[key] = value if value > 0 else None
                    except (ValueError, ZeroDivisionError):
                        state[key] = None
            t = element.find('time')
            if t is not None:
                try:
                    beats, unit = whole(t.findtext('beats')), whole(t.findtext('beat-type'))
                    state['meter'] = Fraction(beats * 4, unit) if beats > 0 and unit > 0 else None
                except (ValueError, ZeroDivisionError):
                    state['meter'] = None
            tr = element.find('transpose')
            if tr is not None:
                try:
                    state['transpose'] = whole(tr.findtext('chromatic')) + 12 * whole(tr.findtext('octave-change', '0'))
                    if tr.find('double') is not None or tr.get('number') is not None:
                        state['transpose'] = None
                except (ValueError, ZeroDivisionError):
                    state['transpose'] = None
            k = element.find('key')
            if k is not None:
                try:
                    fifths = whole(k.findtext('fifths'))
                    state['fifths'] = fifths if -7 <= fifths <= 7 else None
                    if k.find('key-step') is not None:
                        state['fifths'] = None
                except (ValueError, ZeroDivisionError):
                    state['fifths'] = None
            if element.find('.//multiple-rest') is not None:
                error = '複数小節休符は初回対応外'
        elif tag in {'backup', 'forward'}:
            # Multiple timelines cannot be resolved under the one-voice contract.
            error = 'backup/forwardを含む時間軸は初回対応外'
        elif tag == 'note':
            source = len([m for e in events for m in e.members]) + 1
            risks = []
            if element.find('tie') is not None or element.find('notations/tied') is not None:
                risks.append('tie')
            if element.find('time-modification') is not None or element.find('notations/tuplet') is not None:
                risks.append('tuplet')
            if element.find('grace') is not None:
                risks.append('grace')
            if element.find('notations/slur') is not None:
                presence.append({'kind': 'slur', 'element': source})
            presence.extend({'kind': risk, 'element': source} for risk in risks)
            try:
                duration = rational(element.findtext('duration')) / state['divisions']
                if duration <= 0:
                    duration = None
            except (ValueError, TypeError, ZeroDivisionError):
                duration = None
            if duration is None:
                error = '音価・開始位置を計算できない'
            if 'grace' in risks:
                error = '装飾音の時間軸は初回対応外'
            kind = 'rest' if element.find('rest') is not None else 'note'
            pitch, pitch_error = None, None
            if kind == 'note':
                try:
                    pn = element.find('pitch')
                    if pn is None:
                        raise ValueError('無音高または音高情報なし')
                    step = pn.findtext('step')
                    alter = whole(pn.findtext('alter', '0'))
                    octave = whole(pn.findtext('octave'))
                    if step not in STEPS or not 0 <= octave <= 9:
                        raise ValueError('音高範囲外')
                    display = element.findtext('accidental')
                    if state['fifths'] is None:
                        raise ValueError('調号文脈が不明')
                    signature = {}
                    fifths = state['fifths']
                    order = 'FCGDAEB' if fifths >= 0 else 'BEADGCF'
                    for letter in order[:abs(fifths)]:
                        signature[letter] = 1 if fifths >= 0 else -1
                    effective = accidental_context.get((step, octave), signature.get(step, 0))
                    if display is not None:
                        if display not in ACCIDENTALS or ACCIDENTALS[display] != alter:
                            raise ValueError('臨時記号と音高の不整合')
                        accidental_context[step, octave] = alter
                    elif alter != effective:
                        raise ValueError('調号・臨時記号の文脈と音高の不整合')
                    pitch = (step, alter, octave)
                except (ValueError, ZeroDivisionError) as exc:
                    pitch_error = str(exc)
            if not risks:
                typ = element.findtext('type')
                if typ is not None:
                    expected = TYPE_LENGTH.get(typ)
                    dots = len(element.findall('dot'))
                    if expected is None or duration != expected * sum((Fraction(1, 2**i) for i in range(dots + 1)), Fraction(0)):
                        risks.append('duration_notation_inconsistent')
                        presence.append({'kind': 'duration_notation_inconsistent', 'element': source})
            member = Member(pitch, duration, element.findtext('accidental'), source, pitch_error, risks,
                            {'step': element.findtext('pitch/step'), 'alter': element.findtext('pitch/alter'),
                             'octave': element.findtext('pitch/octave'), 'duration': element.findtext('duration'),
                             'type': element.findtext('type'), 'dots': len(element.findall('dot')),
                             'divisions': state['divisions'], 'fifths': state['fifths']})
            voice, staff = element.findtext('voice'), element.findtext('staff')
            if element.find('chord') is not None:
                if not events or events[-1].kind == 'rest' or kind == 'rest':
                    error = '和音の先行音を特定できない'
                elif (events[-1].voice, events[-1].staff) != (voice, staff):
                    error = '和音内の声部・譜表が不整合'
                else:
                    events[-1].kind = 'chord'
                    events[-1].members.append(member)
            else:
                events.append(Event(cursor, kind, [member], voice, staff))
                if duration is not None:
                    cursor += duration
    voices = {e.voice for e in events}
    staffs = {e.staff for e in events}
    if not events:
        error = error or '音符・休符がなく比較対象を確定できない'
    if len(voices) != 1 or None in voices or '' in voices:
        error = error or '明示された単一声部ではない'
    if staffs != {'1'} or state['staves'] != 1:
        error = error or '明示された1譜表ではない'
    positions = [e.start for e in events]
    if len(positions) != len(set(positions)):
        error = error or '同位置の独立イベントを識別できない'
    return Measure(node.get('number'), index, state['meter'], state['transpose'], events,
                   cursor if all(m.duration is not None for e in events for m in e.members) else None,
                   error, presence, dict(state))


def location(label, part, measure=None, position=None, event=None):
    return {'input': label, 'part': part.id, 'part_order': part.index,
            'measure': measure.index if measure else None,
            'measure_number': measure.number if measure else None,
            'position': str(position) if position is not None else None,
            'staff': event.staff if event else None, 'voice': event.voice if event else None,
            'elements': [m.source for m in event.members] if event else []}


def reason(code, priority, detail, a=None, b=None):
    if code.startswith('alignment.') or code == 'measure.unavailable':
        check = '原本のパート・譜表・声部と小節の並び、欠落・重複、各入力の対応を確認してください。'
    elif code.startswith(('written_pitch.', 'sounding_pitch.', 'composition.')):
        check = '原本の符頭・和音構成音、調号・臨時記号、移調指定を確認してください。'
    elif code.startswith(('duration.', 'measure.length', 'meter.')):
        check = '原本の音符・休符の長さ、付点、拍子、タイ・連符を確認してください。'
    elif code.startswith('display.'):
        check = '原本の臨時記号の表示を確認してください。音高の正誤は断定していません。'
    else:
        check = '原本の該当位置の音符・休符・和音と、両入力の対応を確認してください。'
    return {'code': code, 'priority': priority, 'detail': detail, 'a': a, 'b': b,
            'check_original': check}


def aggregate(records):
    groups = {}
    for rec in records:
        if not rec['reasons']:
            continue
        key = (rec['scope'], json.dumps(rec['locations'], sort_keys=True, ensure_ascii=False))
        group = groups.setdefault(key, {'scope': rec['scope'], 'locations': rec['locations'],
                                       'record_ids': [], 'reasons': [], 'pdf_position': None})
        group['record_ids'].append(rec['id'])
        group['reasons'].extend(rec['reasons'])
    for group in groups.values():
        known = [x['priority'] for x in group['reasons'] if x['priority'] in ['P1', 'P2', 'P3']]
        group['representative_priority'] = min(known) if known else 'U'
        group['has_unknown_priority'] = any(x['priority'] not in ['P1', 'P2', 'P3'] for x in group['reasons'])
        group['display_priority'] = 'U' if group['has_unknown_priority'] else group['representative_priority']
    def key(group):
        loc = group['locations'][0]
        def missing(v):
            return (v is None, v if v is not None else '')
        pos = loc['position']
        return (['U', 'P1', 'P2', 'P3'].index(group['display_priority']), loc['input'],
                loc['part_order'], missing(loc['staff']), missing(loc['voice']),
                (loc['measure'] is None, loc['measure'] or 0),
                (pos is None, Fraction(pos) if pos is not None else Fraction(0)),
                min(x['code'] for x in group['reasons']))
    return sorted(groups.values(), key=key)


def compare_files(a, b):
    result = {'schema_version': '1', 'rule_version': RULE_VERSION, 'status': 'complete',
              'inputs': [], 'matches': [], 'records': [], 'presence': [], 'errors': [],
              'limitations': LIMITS, 'reviews': []}
    scores = []
    for label, path in [('A', a), ('B', b)]:
        try:
            score = read_score(path)
            scores.append(score)
            result['inputs'].append({'id': label, 'sha256': score.sha256})
        except (OSError, ET.ParseError, ValueError) as exc:
            scores.append(None)
            # Avoid leaking private file paths or arbitrary input metadata in errors.
            result['inputs'].append({'id': label, 'sha256': None})
            result['errors'].append({'input': label, 'code': 'input.unreadable',
                                     'detail': type(exc).__name__ + ': 入力形式・読取可否を確認してください。'})
    if None in scores:
        result['status'] = 'unavailable'
        result['summary'] = {'review_locations': 0, 'reasons': 0, 'matched_measures': 0, 'compared_events': 0}
        return result
    sa, sb = scores

    def emit(scope, locs, axes=None, reasons=None, detail=None):
        rec = {'id': f'R{len(result["records"])+1:05}', 'scope': scope, 'locations': locs,
               'axes': axes or {}, 'reasons': reasons or [], 'detail': detail}
        result['records'].append(rec)
        return rec

    for label, score in [('A', sa), ('B', sb)]:
        for part in score.parts:
            for m in part.measures:
                for present in m.presence:
                    result['presence'].append({'location': location(label, part, m), **present})

    ca, cb = Counter(p.id for p in sa.parts), Counter(p.id for p in sb.parts)
    used_b = set()
    for pa in sa.parts:
        candidates = [p for p in sb.parts if p.id == pa.id]
        pb = candidates[0] if ca[pa.id] == cb[pa.id] == 1 and pa.id else None
        if pb is None or not pa.name or pa.name != pb.name or pa.staff_count != 1 or pb.staff_count != 1:
            emit('part', [location('A', pa)], reasons=[reason('alignment.part', 'P1', 'パートID・名称・譜表構成から一意に対応できない')])
            continue
        used_b.add(pb.index)
        na, nb = Counter(m.number for m in pa.measures), Counter(m.number for m in pb.measures)
        for i in range(max(len(pa.measures), len(pb.measures))):
            ma = pa.measures[i] if i < len(pa.measures) else None
            mb = pb.measures[i] if i < len(pb.measures) else None
            if (ma is None or mb is None or not ma.number or ma.number != mb.number or
                    na[ma.number] != 1 or nb[mb.number] != 1 or ma.meter is None or mb.meter is None):
                locs = [location('A', pa, ma), location('B', pb, mb)]
                emit('range', locs, reasons=[reason('alignment.measure', 'P1', '小節対応が不成立。このパートの残りの範囲を保留')],
                     detail={'A': [location('A', pa, x) for x in pa.measures[i:]],
                             'B': [location('B', pb, x) for x in pb.measures[i:]]})
                break
            result['matches'].append([pa.id, ma.index, mb.index])
            if ma.error or mb.error:
                emit('measure', [location('A', pa, ma), location('B', pb, mb)],
                     reasons=[reason('measure.unavailable', 'P1', '時間軸・声部・譜表の比較不能', ma.error, mb.error)])
                continue
            lengths = []
            for label, part, m in [('A', pa, ma), ('B', pb, mb)]:
                if m.length != m.meter:
                    lengths.append(reason('measure.length', 'P2', f'{label}: 拍子に対する小節長不一致', str(m.meter), str(m.length)))
            if ma.meter != mb.meter:
                lengths.append(reason('meter.diff', 'P2', '拍子の長さが入力間で異なる', str(ma.meter), str(mb.meter)))
            emit('measure', [location('A', pa, ma), location('B', pb, mb)], reasons=lengths,
                 axes={'length': {'status': 'equal' if ma.length == mb.length else 'different',
                                  'a': str(ma.length), 'b': str(mb.length)}})
            ea, eb = {e.start: e for e in ma.events}, {e.start: e for e in mb.events}
            for pos in sorted(ea.keys() | eb.keys()):
                x, y = ea.get(pos), eb.get(pos)
                locs = [location('A', pa, ma, pos, x), location('B', pb, mb, pos, y)]
                if x is None or y is None:
                    emit('event', locs, reasons=[reason('event.only_b' if x is None else 'event.only_a', 'P2', 'この開始位置は片側にのみ存在。後続音と強制対応しない')],
                         detail={'A': event_values(x, ma), 'B': event_values(y, mb)})
                    continue
                axes, reasons = compare_events(x, y, ma, mb)
                emit('event', locs, axes, reasons,
                     {'A': event_values(x, ma), 'B': event_values(y, mb)})
    for pb in sb.parts:
        if pb.index not in used_b:
            emit('part', [location('B', pb)], reasons=[reason('alignment.part', 'P1', '対応先パートが一意に成立しない')])
    result['reviews'] = aggregate(result['records'])
    if any(r['priority'] == 'P1' or r['code'].endswith('.unavailable') for rec in result['records'] for r in rec['reasons']):
        result['status'] = 'partial'
    result['summary'] = {'review_locations': len(result['reviews']),
                         'reasons': sum(len(r['reasons']) for r in result['records']),
                         'matched_measures': len(result['matches']),
                         'compared_events': sum(bool(r['axes']) and r['scope'] == 'event' for r in result['records'])}
    return result


def ordered_members(event):
    return sorted(event.members, key=lambda m: (m.pitch is None, m.pitch or ('', 0, 0), m.source))


def event_values(event, measure):
    if event is None:
        return None
    return {'kind': event.kind, 'start': str(event.start), 'transpose': measure.transpose,
            'members': [{'pitch': m.pitch, 'duration': str(m.duration) if m.duration is not None else None,
                         'display': m.display, 'source_element': m.source,
                         'pitch_error': m.pitch_error, 'unsupported': m.risks, 'original': m.original} for m in event.members],
            'normalization': {'duration_unit': 'quarter-note rational', 'chord_order': 'ignored, multiplicity retained'}}


def compare_events(x, y, ma, mb):
    axes, reasons = {}, []
    def axis(name, av, bv, unavailable=None, applicable=True, priority='P2'):
        state = 'not_applicable' if not applicable else 'unavailable' if unavailable else 'equal' if av == bv else 'different'
        axes[name] = {'status': state, 'a': av, 'b': bv, 'reason': unavailable}
        if state in ['different', 'unavailable']:
            code = name + ('.diff' if state == 'different' else '.unavailable')
            reasons.append(reason(code, priority, unavailable or f'{name}: 入力間の差', av, bv))
    axis('kind', x.kind, y.kind)
    xm, ym = ordered_members(x), ordered_members(y)
    risks = sorted({r for e in [x, y] for m in e.members for r in m.risks})
    axis('duration', [str(m.duration) for m in xm], [str(m.duration) for m in ym],
         '意味的な音価比較は初回対象外: '+', '.join(risks) if risks else None)
    applicable = x.kind != 'rest' and y.kind != 'rest'
    err = '; '.join(sorted({m.pitch_error for m in xm + ym if m.pitch_error})) or None
    name = 'composition' if x.kind == 'chord' or y.kind == 'chord' else 'written_pitch'
    axis(name, [m.pitch for m in xm], [m.pitch for m in ym], err, applicable)
    axis('note_count', len(xm), len(ym), applicable=applicable)
    def sounding(members, tr):
        if tr is None or any(m.pitch is None for m in members):
            return None
        return sorted(STEPS[m.pitch[0]] + m.pitch[1] + 12 * (m.pitch[2] + 1) + tr for m in members)
    sound_err = err or ('明示的な移調情報がなく実音を確定しない' if ma.transpose is None or mb.transpose is None else None)
    axis('sounding_pitch', sounding(xm, ma.transpose), sounding(ym, mb.transpose), sound_err, applicable)
    display_a = [(m.pitch, m.display) for m in xm]
    display_b = [(m.pitch, m.display) for m in ym]
    # Display comparison is meaningful only when the written pitches are equal.
    display_applicable = applicable and axes[name]['status'] == 'equal'
    display_priority = 'P3' if all(a['status'] in ['equal', 'not_applicable'] for a in axes.values()) else 'P2'
    axis('display', display_a, display_b, applicable=display_applicable, priority=display_priority)
    return axes, reasons


def render_text(report):
    """Flatten the same report tree without dropping fields (JSON stays canonical)."""
    lines = ['score-reader 比較レポート（正誤判定ではありません）',
             '場所=locations / 差分=axes / 確認理由=reasons / 優先順位=display_priority / 原本確認=check_original']
    for group in report['reviews']:
        lines.append('')
        lines.append('優先順位: ' + group['display_priority'] + ' / 既知理由の代表: ' + group['representative_priority'])
        lines.append('場所: ' + json.dumps(group['locations'], ensure_ascii=False))
        for evidence in group['reasons']:
            lines.append('差分・確認理由: ' + evidence['detail'] + ' [' + evidence['code'] + ']')
            lines.append('入力A/Bの観測値: ' + json.dumps([evidence['a'], evidence['b']], ensure_ascii=False))
            lines.append('原本で確認する事項: ' + evidence['check_original'])
        lines.append('原本PDFのページ位置: 不明')
    lines.append('\n全情報（比較軸・出典・不能理由を含む）:')
    def walk(value, path):
        if isinstance(value, dict):
            if not value:
                lines.append(path + ' = {}')
            for k, v in value.items():
                walk(v, path + '.' + k if path else k)
        elif isinstance(value, (list, tuple)):
            if not value:
                lines.append(path + ' = []')
            for i, v in enumerate(value):
                walk(v, f'{path}[{i}]')
        else:
            lines.append(path + ' = ' + json.dumps(value, ensure_ascii=False))
    # Review priority groups are presented first; all axis/evidence details follow.
    for field_name in ['status', 'reviews', 'summary', 'presence', 'limitations', 'inputs', 'matches', 'records', 'errors', 'schema_version', 'rule_version']:
        walk(report[field_name], field_name)
    return '\n'.join(lines) + '\n'
