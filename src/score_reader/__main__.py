"""CLI entry point; prints reports only, never writes inputs or derived scores."""
import argparse
import json
from .compare import compare_files, render_text


def main():
    parser = argparse.ArgumentParser(description='2つのMusicXMLの差分・比較不能箇所を報告します。')
    parser.add_argument('input_a')
    parser.add_argument('input_b')
    parser.add_argument('--json', action='store_true', help='同じレポートをJSONで標準出力へ表示')
    args = parser.parse_args()
    report = compare_files(args.input_a, args.input_b)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_text(report), end='\n' if args.json else '')
    return 1 if report['status'] == 'unavailable' else 0


if __name__ == '__main__':
    raise SystemExit(main())
