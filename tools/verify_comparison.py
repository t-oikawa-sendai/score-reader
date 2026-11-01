#!/usr/bin/env python3
"""Run immutable synthetic cases and retain a restorable, uncommitted source state."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tests'))
from acceptance import FIXTURES, check_case, sha, verify_manifest
from score_reader.compare import render_text


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def source_state():
    tracked = set(git('ls-files','-z').decode().strip('\0').split('\0'))
    others = set(git('ls-files','--others','--exclude-standard','-z').decode().strip('\0').split('\0'))
    names = sorted(n for n in tracked | others if n and not n.startswith('tests/results/'))
    hashes = {n: sha(ROOT/n) if (ROOT/n).is_file() else None for n in names}
    patch = git('diff','--binary','HEAD','--','.',':(exclude)tests/results')
    return {'head':git('rev-parse','HEAD').decode().strip(), 'files':hashes,
            'untracked':sorted(n for n in others if n and not n.startswith('tests/results/')),
            'patch_sha256':hashlib.sha256(patch).hexdigest()},patch


def compare_runs(previous, current):
    before={c['id']:c for c in previous['cases']};after={c['id']:c for c in current['cases']}
    common=[];changed=[]
    def signature(c):return (c['case_sha256'],c['expected_sha256'],tuple(c['inputs_sha256']))
    for cid in sorted(before.keys() & after.keys()):
        if signature(before[cid])!=signature(after[cid]):changed.append(cid);continue
        common.append({'id':cid,'before':{k:before[cid][k] for k in ['passed','missing','unnecessary','misalignment','reviews','reasons']},
                       'after':{k:after[cid][k] for k in ['passed','missing','unnecessary','misalignment','reviews','reasons']}})
    return {'common_cases':common,'added_cases':sorted(after.keys()-before.keys()),
            'changed_cases':changed,'removed_cases':sorted(before.keys()-after.keys()),
            'note':'警告数の減少だけで精度向上とは判定しない。人工データのみ。'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--suite',default='v003')
    ap.add_argument('--output',required=True,help='new directory below tests/results/comparison/')
    ap.add_argument('--compare-run',help='previous result.json')
    args=ap.parse_args()
    output=Path(args.output).resolve()
    if not output.is_relative_to(ROOT/'tests/results/comparison'):
        ap.error('output must be below tests/results/comparison/')
    if output.exists():ap.error('refusing to overwrite an existing run')
    suite_path=FIXTURES/'suites'/f'{args.suite}.json'
    suite=json.loads(suite_path.read_text());verify_manifest(suite)
    before,patch=source_state()
    output.mkdir(parents=True)
    (output/'tracked.patch').write_bytes(patch)
    with tarfile.open(output/'untracked.tar.gz','w:gz') as archive:
        for n in before['untracked']:
            archive.add(ROOT/n,arcname=n,recursive=False)
    (output/'source-state.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
    cases=[]
    for entry in suite['cases']:
        outcome,report=check_case(entry);cases.append(outcome)
        (output/(entry['id']+'.txt')).write_text(render_text(report))
        (output/(entry['id']+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    env={**os.environ,'PYTHONPATH':str(ROOT/'src')}
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],cwd=ROOT,env=env,capture_output=True,text=True)
    (output/'boundary-tests.txt').write_text(test.stdout+test.stderr)
    after,_=source_state();stable=before==after
    result={'run_id':output.name,'created_utc':datetime.now(timezone.utc).isoformat(),
            'platform':platform.platform(),'python':sys.version,'implementation_commit':before['head'],
            'dirty':bool(patch or before['untracked']),'source_state_sha256':sha(output/'source-state.json'),
            'tracked_patch_sha256':sha(output/'tracked.patch'),'untracked_archive_sha256':sha(output/'untracked.tar.gz'),
            'suite_version':suite['version'],'suite_sha256':sha(suite_path),'stable_sources':stable,
            'boundary_tests_passed':test.returncode==0,'macos_verified':sys.platform=='darwin',
            'cases':cases,'passed':all(c['passed'] for c in cases) and test.returncode==0 and stable and sys.platform=='darwin',
            'limits':'人工ケースの動作検証。実OMRの精度・時間削減は未評価。'}
    if args.compare_run:
        result['comparison']=compare_runs(json.loads(Path(args.compare_run).read_text()),result)
    (output/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (output/'RESTORE.md').write_text('''# Restore this run in an isolated checkout

1. Obtain the repository commit recorded in source-state.json in a separate checkout.
2. Apply tracked.patch with `git apply --binary`.
3. Inspect the archive paths, then extract untracked.tar.gz into that checkout.
4. Verify every path in source-state.json against its SHA-256 (null means deleted).
5. Use the Python version in result.json and run the recorded suite. No third-party runtime dependencies are needed.

Do not apply this snapshot over existing work. Results are not part of the source snapshot and can be copied separately.
The patch represents the final worktree relative to HEAD, including staged and unstaged changes; staged-state identity is not required to reproduce execution.
''')
    print(json.dumps({'run':str(output.relative_to(ROOT)),'passed':result['passed'],
                      'cases':[{k:c[k] for k in ['id','passed','missing','unnecessary','misalignment','reviews']} for c in cases]},ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
