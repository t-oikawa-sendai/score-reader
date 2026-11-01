"""Acceptance oracle: immutable authored expectations, never generated from reports."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from score_reader.compare import compare_files
FIXTURES = ROOT / 'tests/fixtures/comparison'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(issue):
    return (issue['part'], issue['measure'], issue['position'], issue['scope'], issue['code'], issue['priority'])


def check_case(entry):
    case_path = FIXTURES / entry['case']
    case = json.loads(case_path.read_text())
    expected_path = FIXTURES / entry['expected']
    expected = json.loads(expected_path.read_text())
    inputs = [FIXTURES / x for x in case['inputs']]
    before = [sha(p) for p in inputs]
    report = compare_files(*inputs)
    errors = []
    actual = []
    for rec in report['records']:
        loc = rec['locations'][0]
        actual.extend({'part':loc['part'], 'measure':loc['measure'], 'position':loc['position'],
                       'scope':rec['scope'], 'code':r['code'], 'priority':r['priority']} for r in rec['reasons'])
    wanted, got = Counter(map(identity, expected['issues_exact'])), Counter(map(identity, actual))
    missing = list((wanted-got).elements())
    extra = list((got-wanted).elements())
    if missing: errors.append({'missing':missing})
    if extra: errors.append({'unnecessary':extra})
    if report['matches'] != expected['matches_exact']:
        errors.append({'misalignment':{'expected':expected['matches_exact'],'actual':report['matches']}})
    if len(report['reviews']) != expected['review_groups']:
        errors.append({'aggregation_count':len(report['reviews']),'expected':expected['review_groups']})
    for check in expected['axes']:
        found = [r for r in report['records'] if r['scope']=='event' and
                 all(r['locations'][0][key]==check[key] for key in ['part','measure','position'])]
        axis = found[0]['axes'].get(check['axis'], {}) if len(found)==1 else {}
        for key in ['status','a','b']:
            if key in check and axis.get(key)!=check[key]:errors.append({'axis':check,'actual':axis})
    present = {p['kind'] for p in report['presence']}
    if not set(expected['presence_required']) <= present:errors.append({'presence':sorted(present)})
    if report['errors']:errors.append({'input_errors':report['errors']})
    if before != [sha(p) for p in inputs]:errors.append({'input_modified':True})
    # Grouping must retain every reason once, without erasing duplicate evidence.
    raw = Counter(json.dumps(r,sort_keys=True,ensure_ascii=False) for rec in report['records'] for r in rec['reasons'])
    grouped = Counter(json.dumps(r,sort_keys=True,ensure_ascii=False) for g in report['reviews'] for r in g['reasons'])
    if raw != grouped:errors.append({'evidence_loss':True})
    for group in report['reviews']:
        known = [r['priority'] for r in group['reasons'] if r['priority']!='U']
        if group['representative_priority'] != (min(known) if known else 'U'):errors.append({'priority':group})
        if group['pdf_position'] is not None:errors.append({'invented_pdf_location':True})
        if not all(r.get('check_original') for r in group['reasons']):errors.append({'missing_original_check':True})
    return {'id':case['id'],'passed':not errors,'errors':errors,
            'missing':len(missing),'unnecessary':len(extra),
            'misalignment':int(report['matches'] != expected['matches_exact']),
            'reviews':len(report['reviews']), 'reasons':len(actual),
            'case_sha256':sha(case_path),'expected_sha256':sha(expected_path),'inputs_sha256':before},report


def verify_manifest(suite):
    for name,digest in suite['files'].items():
        if sha(FIXTURES/name)!=digest:raise AssertionError('Fixture modified: '+name)
