import argparse
import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def read(path):
    return Path(path).read_text(encoding='utf-8').replace('\r\n', '\n')


def article(url):
    parsed = urlparse(url)
    match = re.fullmatch(r'/docs/laravel/([^/]+)/([^/]+)/(\d+)/?', parsed.path)
    if parsed.hostname != 'learnku.com' or not match:
        raise ValueError('需要带文章 ID 的 LearnKu Laravel 版本文档 URL')
    return match.groups()


def php_comment_shape(line, quote):
    escaped = False
    for index, char in enumerate(line):
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif line[index:index + 2] == '//':
            return line[:index] + '// COMMENT', None
    return line, quote


def shape(text):
    result, code, style = [], False, False
    code_language, php_quote = None, None
    for line in text.splitlines():
        if line.startswith('```'):
            code = not code
            code_language = line[3:].strip() if code else None
            php_quote = None
            result.append(line)
        elif code:
            if php_quote is None and (re.match(r'^\s*(//|\* )', line)
                    or re.fullmatch(r'\s*<!--(?:(?!-->).)*-->\s*', line)):
                result.append('COMMENT')
            elif code_language == 'php':
                normalized, php_quote = php_comment_shape(line, php_quote)
                result.append(normalized)
            else:
                result.append(line)
        elif line == '<style>':
            style = True
            result.append(line)
        elif line == '</style>':
            style = False
            result.append(line)
        elif style or re.match(r'^<|^> \[!', line):
            result.append(line)
        elif not line.strip():
            result.append('BLANK')
        elif line.startswith('#'):
            result.append(re.match(r'^#+', line)[0])
        elif re.match(r'^\s*- \[', line):
            result.append(re.match(r'^\s*- ', line)[0] + 'TOC')
        elif line.startswith('['):
            result.append('METHOD-LINK')
        else:
            result.append('TEXT')
    if code or style:
        raise ValueError('发现未闭合的代码围栏或 style 标签')
    return result


def validate(source, translated):
    errors = []
    if shape(source) != shape(translated):
        a, b = shape(source), shape(translated)
        changed = [i + 1 for i in range(max(len(a), len(b)))
                   if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
        errors.append(f'行结构或代码内容不一致，涉及行：{changed[:30]}')
    anchors = lambda s: re.findall(r'^<a name="([^"]+)"></a>', s, re.M)
    if anchors(source) != anchors(translated):
        errors.append('锚点或顺序不一致')
    links = lambda s: collections.Counter(re.findall(r'\]\(([^)]+)\)', s))
    if links(source) != links(translated):
        errors.append('链接目标不一致')
    for number, line in enumerate(translated.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f'第 {number} 行有尾随空格')
        if re.search(r'/docs/laravel/\d+\.x|\[!注意\]|\[!警告\]|utm_source', line):
            errors.append(f'第 {number} 行有旧版本链接或非标准提示块')
    if errors:
        raise ValueError('\n'.join(errors))
    return {'lines': len(source.splitlines()), 'anchors': len(anchors(source)),
            'code_fences': len(re.findall(r'^```', source, re.M)), 'status': 'passed'}


def prepare(args):
    old_version, slug, _ = article(args.old_url)
    new_version, new_slug, _ = article(args.new_url)
    if slug != new_slug or old_version == new_version:
        raise ValueError('两篇文档必须同名且版本不同')
    repo = Path(args.repo).resolve()
    original = read(repo / f'{slug}.md')
    reference = read(args.reference).rstrip() + '\n'
    targets = [(repo / old_version / 'zh' / f'{slug}.md', reference),
               (repo / new_version / 'en' / f'{slug}.md', original),
               (repo / new_version / 'zh' / f'{slug}.md', original)]
    if targets[1][0].exists() and read(targets[1][0]) != original:
        raise ValueError('已有英文备份与根目录源文件不同，需要先检查版本变化')
    for path, content in targets:
        if path.exists():
            print(f'保留已有文件：{path}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            print(f'创建：{path}')


def main():
    parser = argparse.ArgumentParser(description='LearnKu Laravel 留底、结构校验和区块提取')
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('old_url')
    p.add_argument('new_url')
    p.add_argument('--repo', default='.')
    p.add_argument('--reference', required=True)
    for command in ['validate', 'extract']:
        p = commands.add_parser(command)
        p.add_argument('source')
        p.add_argument('translated')
        if command == 'extract':
            selection = p.add_mutually_exclusive_group(required=True)
            selection.add_argument('--snippet')
            selection.add_argument('--lines', help='已复核的仓库行范围，例如 106:233，包含首尾行')
            p.add_argument('--web-version', help='投递时展开文档链接，例如 13.x')
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args)
        return
    source, translated = read(args.source), read(args.translated)
    report = validate(source, translated)
    if args.command == 'validate':
        print(json.dumps(report, ensure_ascii=False))
        return
    if args.lines:
        match = re.fullmatch(r'(\d+):(\d+)', args.lines)
        if not match:
            raise ValueError('行范围格式必须为 START:END')
        start, end = map(int, match.groups())
        if not 1 <= start <= end <= len(source.splitlines()):
            raise ValueError('行范围超出文档或顺序错误')
        first, length = start - 1, end - start + 1
    else:
        snippet = read(args.snippet).strip('\n')
        if not snippet or source.count(snippet) != 1:
            raise ValueError('区块原文在英文留底中未唯一匹配；请复核版本差异和边界后使用 --lines')
        offset = source.index(snippet)
        end = offset + len(snippet)
        if (offset and source[offset-1] != '\n') or (end < len(source) and source[end] != '\n'):
            raise ValueError('区块必须按完整行匹配')
        first = source[:offset].count('\n')
        length = len(snippet.splitlines())
    result = '\n'.join(translated.splitlines()[first:first+length])
    if args.web_version:
        if not re.fullmatch(r'\d+\.x', args.web_version):
            raise ValueError('网站版本格式必须为数字加 .x')
        result = result.replace('/docs/{{version}}/', f'/docs/laravel/{args.web_version}/')
    print(result)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
