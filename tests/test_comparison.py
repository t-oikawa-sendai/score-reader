"""Approved cases plus boundary tests for preservation and conservative comparison."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from acceptance import ROOT, FIXTURES, sha, check_case, verify_manifest
from score_reader.compare import compare_files, aggregate, reason, render_text

SUITE = FIXTURES/'suites/v003.json'
BASE = FIXTURES/'bases/BASIC-4M/v001/base.musicxml'


class ComparisonTests(unittest.TestCase):
    def test_approved_cases(self):
        suite=json.loads(SUITE.read_text());verify_manifest(suite)
        for case in suite['cases']:
            with self.subTest(case=case['id']):
                outcome,_=check_case(case)
                self.assertTrue(outcome['passed'],json.dumps(outcome,ensure_ascii=False))

    def saved(self,name):
        p=FIXTURES/'support/v001'/(name+'.musicxml')
        before=sha(p);r=compare_files(BASE,p);self.assertEqual(before,sha(p));return r

    def test_support_integrity(self):
        root=FIXTURES/'support/v001'
        manifest=json.loads((root/'manifest.json').read_text())
        for name,digest in manifest['files'].items():self.assertEqual(sha(root/name),digest)

    def test_no_forced_multivoice_match(self):
        r=self.saved('multivoice')
        self.assertTrue(any(q['code']=='measure.unavailable' for rec in r['records'] for q in rec['reasons']))
        self.assertFalse(any(rec['scope']=='event' and rec['locations'][0]['measure']==1 for rec in r['records']))
        self.assertTrue(any(rec['scope']=='event' and rec['locations'][0]['measure']==2 for rec in r['records']))

    def test_time_failure_does_not_hide_following_measure(self):
        r=self.saved('invalid-duration')
        self.assertEqual(r['status'],'partial')
        self.assertTrue(any(rec['scope']=='event' and rec['locations'][0]['measure']==2 for rec in r['records']))

    def test_tuplet_and_grace_are_explicit(self):
        r=self.saved('tuplet')
        self.assertIn('tuplet',[p['kind'] for p in r['presence']])
        self.assertIn('duration.unavailable',[q['code'] for rec in r['records'] for q in rec['reasons']])
        r=self.saved('grace')
        self.assertIn('measure.unavailable',[q['code'] for rec in r['records'] for q in rec['reasons']])

    def test_pitch_error_retains_duration_and_kind(self):
        r=self.saved('microtone')
        rec=next(rec for rec in r['records'] if rec['scope']=='event')
        self.assertEqual(rec['axes']['written_pitch']['status'],'unavailable')
        self.assertEqual(rec['axes']['sounding_pitch']['status'],'unavailable')
        self.assertEqual(rec['axes']['duration']['status'],'equal')
        self.assertEqual(rec['axes']['kind']['status'],'equal')

    def test_same_name_ids_and_other_part_continue(self):
        base=FIXTURES/'bases/TWO-PART/v001/base.musicxml'
        r=compare_files(base,base)
        self.assertEqual(len(r['matches']),8);self.assertFalse(r['reviews'])
        r=compare_files(base,FIXTURES/'support/v001/other-part-continues.musicxml')
        self.assertEqual([m for m in r['matches'] if m[0]=='P2'],[['P2',i,i] for i in range(1,5)])

    def test_unknown_priority_and_scope(self):
        data=json.loads((FIXTURES/'support/v001/aggregation.json').read_text())
        loc=data['location']
        def rec(i,scope,rs):return {'id':i,'scope':scope,'locations':[loc],'reasons':rs}
        rr=[rec('1','event',[reason('a','P2','a')]),rec('2','event',[reason('b','U','b')]),rec('3','measure',[reason('c','P1','c')])]
        groups=aggregate(rr)
        self.assertEqual(len(groups),2);self.assertEqual(groups[0]['display_priority'],'U')
        self.assertEqual(groups[0]['representative_priority'],'P2');self.assertEqual(len(groups[0]['reasons']),2)
        rr[1]['reasons'][0]['priority']='P1';self.assertEqual(aggregate(rr)[0]['representative_priority'],'P1')
        self.assertFalse(aggregate([rec('x','event',[])]))

    def test_cli_and_text_json_equivalence(self):
        env={**os.environ,'PYTHONPATH':str(ROOT/'src')}
        pairs=[tuple(FIXTURES/p for p in json.loads((FIXTURES/c['case']).read_text())['inputs']) for c in json.loads(SUITE.read_text())['cases']]
        for a,b in pairs+[(BASE,Path('/nonexistent-score-reader-input'))]:
            j=subprocess.run([sys.executable,'-m','score_reader',str(a),str(b),'--json'],env=env,capture_output=True,text=True)
            t=subprocess.run([sys.executable,'-m','score_reader',str(a),str(b)],env=env,capture_output=True,text=True)
            report=json.loads(j.stdout)
            self.assertEqual(j.returncode,t.returncode)
            self.assertEqual(t.stdout,render_text(report))
            # Every JSON leaf is exposed by the independent text parser.
            flat={line.split(' = ',1)[0]:json.loads(line.split(' = ',1)[1]) for line in t.stdout.splitlines() if ' = ' in line}
            def leaves(value,path=''):
                if isinstance(value,dict) and value:
                    for k,v in value.items():yield from leaves(v,path+'.'+k if path else k)
                elif isinstance(value,list) and value:
                    for i,v in enumerate(value):yield from leaves(v,f'{path}[{i}]')
                else:yield path,value
            self.assertEqual(flat,dict(leaves(report)))
        for args in [[],[str(BASE)],[str(BASE)]*3]:
            proc=subprocess.run([sys.executable,'-m','score_reader',*args],env=env,capture_output=True)
            self.assertEqual(proc.returncode,2)

    def test_invalid_xml_and_doctype(self):
        for name in ['invalid','doctype','timewise']:
            p=FIXTURES/'support/v001'/(name+'.xml')
            r=compare_files(BASE,p);self.assertEqual(r['status'],'unavailable');self.assertTrue(r['errors'])

    def test_run_comparison_separates_changed_added_removed(self):
        sys.path.insert(0,str(ROOT/'tools'))
        from verify_comparison import compare_runs
        def case(cid,expected='e'):
            return dict(id=cid,case_sha256='c',expected_sha256=expected,inputs_sha256=['a','b'],
                        passed=True,missing=0,unnecessary=0,misalignment=0,reviews=1,reasons=2)
        r=compare_runs({'cases':[case('same'),case('changed'),case('removed')]},
                       {'cases':[case('same'),case('changed','new'),case('added')]})
        self.assertEqual([c['id'] for c in r['common_cases']],['same'])
        self.assertEqual(r['added_cases'],['added'])
        self.assertEqual(r['changed_cases'],['changed'])
        self.assertEqual(r['removed_cases'],['removed'])

    def test_repeated_execution_and_voice_source(self):
        b=FIXTURES/'cases/SYN-009/v001/variant.musicxml'
        a=compare_files(BASE,b);self.assertEqual(a,compare_files(BASE,b))
        e=next(r for r in a['records'] if r['scope']=='event');self.assertEqual(e['locations'][1]['voice'],'7')


if __name__=='__main__':unittest.main()
