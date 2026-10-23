"""Compare a local article with observations from the actual published LearnKu DOM."""
import argparse
import collections
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class HtmlTables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.stack.append(len(self.tables))
            self.tables.append([self.getpos()[0] - 1, 0])
        elif tag == 'tr':
            for index in self.stack:
                self.tables[index][1] += 1

    def handle_endtag(self, tag):
        if tag == 'table' and self.stack:
            self.stack.pop()


def manifest(markdown):
    lines, code, code_blocks = [], False, 0
    indented, style = False, False
    for line in markdown.splitlines():
        if line.startswith('```'):
            indented = False
            if not code:
                code_blocks += 1
            code = not code
            lines.append('')
        elif code:
            lines.append('')
        elif line.strip() == '<style>':
            style = True
            lines.append('')
        elif line.strip() == '</style>':
            style = False
            lines.append('')
        elif style:
            lines.append('')
        elif line.startswith('    ') and line.strip() and not re.match(r'^\s*(?:[-*+]|\d+[.)])\s', line):
            if indented or not lines or not lines[-1].strip():
                if not indented:
                    code_blocks += 1
                indented = True
                lines.append('')
            else:
                lines.append(line)
        else:
            if line.strip():
                indented = False
            lines.append(line)
    if code:
        raise ValueError('代码围栏未闭合')
    html_tables = HtmlTables()
    html_tables.feed('\n'.join(lines))
    headings, tables, links = [], list(html_tables.tables), []
    for i, line in enumerate(lines):
        heading = re.match(r'^(#{1,6})\s', line)
        html_heading = re.match(r'^<h([1-6])\b', line)
        if heading or html_heading:
            headings.append(len(heading[1]) if heading else int(html_heading[1]))
        if re.fullmatch(r'\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*', line) and '|' in line:
            if i == 0 or '|' not in lines[i-1]:
                continue
            rows, j = 1, i + 1
            while j < len(lines) and lines[j].strip().startswith('|'):
                rows += 1
                j += 1
            tables.append([i, rows])
        method_link = re.match(r'^\[[^\]]+\]\((#[^)]+)\)', line)
        if method_link:
            links.append(method_link[1])
    return {'headings': headings, 'codeBlocks': code_blocks,
            'tables': [rows for _, rows in sorted(tables)],
            'anchors': re.findall(r'<a name="([^"]+)"></a>', '\n'.join(lines)),
            'methodLinks': links,
            'listItems': sum(bool(re.match(r'^\s*[-*+]\s+', line)) for line in lines)}


def check(markdown, observed):
    expected = manifest(markdown)
    required = ['headings', 'codeBlocks', 'tables', 'anchors', 'links', 'listItems',
                'rawMarkdown', 'rawHeadingClasses', 'codeImages', 'containers']
    missing = [key for key in required if key not in observed]
    if missing:
        raise ValueError('缺少实际 DOM 观察字段：' + ', '.join(missing))
    errors = []
    for key in ['headings', 'codeBlocks', 'tables', 'listItems']:
        if observed[key] != expected[key]:
            errors.append(f'{key} 不一致：预期 {expected[key]}；实际 {observed[key]}')
    for key in ['anchors', 'methodLinks']:
        actual = collections.Counter(observed['links' if key == 'methodLinks' else key])
        absent = collections.Counter(expected[key]) - actual
        if absent:
            errors.append(f'{key} 缺失：{dict(absent)}')
    for key in ['rawMarkdown', 'rawHeadingClasses', 'codeImages']:
        if observed[key]:
            errors.append(f'{key} 发现未正确渲染的内容：{observed[key][:3]}')
    if errors:
        raise ValueError('\n'.join(errors))
    return {'status': 'passed', 'headings': len(expected['headings']),
            'code_blocks': expected['codeBlocks'], 'tables': len(expected['tables']),
            'list_items': expected['listItems'], 'method_links': len(expected['methodLinks'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('article')
    parser.add_argument('observation', nargs='?')
    args = parser.parse_args()
    markdown = Path(args.article).read_text(encoding='utf-8')
    result = check(markdown, json.loads(Path(args.observation).read_text(encoding='utf-8'))) if args.observation else manifest(markdown)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
