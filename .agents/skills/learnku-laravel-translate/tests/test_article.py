import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'article.py'
SPEC = importlib.util.spec_from_file_location('article', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
OLD_URL = 'https://learnku.com/docs/laravel/12.x/helpers/16967'
NEW_URL = 'https://learnku.com/docs/laravel/13.x/helpers/17083'


class ArticleTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.repo = Path(self.folder.name)
        self.source = self.repo / 'en.md'
        self.translated = self.repo / 'zh.md'
        self.source.write_text('# Intro\n\n<a name="new"></a>\n## New method\n\nSee [docs](/docs/{{version}}/helpers).\n\n```php\n$value = 1;\n// Explain this value\n```\n', encoding='utf-8')
        self.translated.write_text('# 简介\n\n<a name="new"></a>\n## 新方法\n\n参见[文档](/docs/{{version}}/helpers)。\n\n```php\n$value = 1;\n// 解释这个值\n```\n', encoding='utf-8')

    def run_script(self, *args):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], capture_output=True, text=True)

    def run_cli(self, *args):
        return self.run_script('extract', str(self.source), str(self.translated), *args)

    def prepare(self, old_url=OLD_URL, new_url=NEW_URL):
        return self.run_script('prepare', old_url, new_url, '--repo', str(self.repo), '--reference', str(self.translated))

    def test_prepare_uses_official_source_for_both_new_files(self):
        original = self.repo / 'helpers.md'
        original.write_bytes(self.source.read_bytes())
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.repo / '12.x/zh/helpers.md').read_bytes(), self.translated.read_bytes())
        for path in ['13.x/en/helpers.md', '13.x/zh/helpers.md']:
            self.assertEqual((self.repo / path).read_bytes(), original.read_bytes())

    def test_prepare_preserves_existing_reference_and_translation(self):
        (self.repo / 'helpers.md').write_bytes(self.source.read_bytes())
        self.assertEqual(self.prepare().returncode, 0)
        reference = self.repo / '12.x/zh/helpers.md'
        translation = self.repo / '13.x/zh/helpers.md'
        reference.write_text('# Existing reference\n', encoding='utf-8')
        translation.write_text('# Existing translation\n', encoding='utf-8')
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(reference.read_text(), '# Existing reference\n')
        self.assertEqual(translation.read_text(), '# Existing translation\n')

    def test_prepare_rejects_stale_backup_before_creating_other_files(self):
        (self.repo / 'helpers.md').write_bytes(self.source.read_bytes())
        backup = self.repo / '13.x/en/helpers.md'
        backup.parent.mkdir(parents=True)
        backup.write_text('# Older source\n', encoding='utf-8')
        result = self.prepare()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / '12.x').exists())
        self.assertFalse((self.repo / '13.x/zh').exists())
        self.assertEqual(backup.read_text(), '# Older source\n')

    def test_prepare_rejects_different_articles_or_same_versions(self):
        for old_url, new_url in [(OLD_URL, NEW_URL.replace('/helpers/', '/context/')), (NEW_URL, NEW_URL)]:
            result = self.prepare(old_url, new_url)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((self.repo / '12.x').exists())
            self.assertFalse((self.repo / '13.x').exists())

    def test_reviewed_range_keeps_new_method_and_code_language(self):
        result = self.run_cli('--lines', '3:11')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('## 新方法', result.stdout)
        self.assertIn('```php', result.stdout)
        self.assertNotIn('# 简介', result.stdout)

    def test_web_links_expand_without_changing_local_file(self):
        original = self.translated.read_bytes()
        result = self.run_cli('--lines', '3:6', '--web-version', '13.x')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('/docs/laravel/13.x/helpers', result.stdout)
        self.assertEqual(self.translated.read_bytes(), original)

    def test_exact_snippet_still_matches(self):
        snippet = self.repo / 'snippet.md'
        snippet.write_text('<a name="new"></a>\n## New method\n', encoding='utf-8')
        result = self.run_cli('--snippet', str(snippet))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '<a name="new"></a>\n## 新方法\n')

    def test_invalid_ranges_fail(self):
        for value in ['0:2', '4:3', '1:999', 'a:b']:
            result = self.run_cli('--lines', value)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')

    def test_semantic_source_difference_requires_review(self):
        snippet = self.repo / 'old.md'
        snippet.write_text('## Old method\n', encoding='utf-8')
        result = self.run_cli('--snippet', str(snippet))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--lines', result.stderr)

    def test_snippet_requires_unique_whole_line_match(self):
        snippet = self.repo / 'snippet.md'
        for content in ['Intro', '```']:
            snippet.write_text(content, encoding='utf-8')
            result = self.run_cli('--snippet', str(snippet))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')

    def test_validation_catches_code_and_link_changes(self):
        source = self.source.read_text()
        translated = self.translated.read_text()
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('$value = 1;', '$value = 2;'), translated.replace('/helpers', '/other')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_reviewed_fenced_prose_preserves_commands_and_inline_tokens(self):
        source = '```text tab=Codex\nOpen `MCP` settings.\ncodex mcp add boost -- php artisan boost:mcp\n```\n'
        translated = source.replace('Open `MCP` settings.', '打开 `MCP` 设置。')
        with self.assertRaises(ValueError):
            MODULE.validate(source, translated)
        self.assertEqual(MODULE.validate(source, translated, '2')['status'], 'passed')
        for changed, selection in [(translated.replace('`MCP`', '`Other`'), '2'),
                                   (translated.replace('add boost', 'add other'), '2:3')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed, selection)

    def test_reviewed_markdown_prose_preserves_example_code_and_frontmatter(self):
        source = '```markdown\nname: package-name\ndescription: Build components.\n## Features\nUse `PackageName`.\n$result = PackageName::run();\n```\n'
        translated = source.replace('Build components.', '构建组件。').replace('Features', '功能').replace('Use `PackageName`.', '使用 `PackageName`。')
        self.assertEqual(MODULE.validate(source, translated, '3:5')['status'], 'passed')
        for changed, selection in [(translated.replace('name: package-name', 'name: other'), '2:5'),
                                   (translated.replace('::run()', '::other()'), '3:6')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed, selection)
        with self.assertRaises(ValueError):
            MODULE.validate('```php\n$value = 1;\n```\n', '```php\n$value = 2;\n```\n', '2')

    def test_reviewed_prose_cli_extracts_from_unchanged_english_snapshot(self):
        self.source.write_text('```text\nRemember this rule.\n```\n')
        self.translated.write_text('```text\n请记住这条规则。\n```\n')
        result = self.run_cli('--lines', '1:3', '--prose-lines', '2')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, self.translated.read_text())
        for invalid in ['0', '4', '3:2', 'a']:
            with self.assertRaises(ValueError):
                MODULE.validate(self.source.read_text(), self.translated.read_text(), invalid)

    def test_html_table_label_translation_preserves_markup_and_code(self):
        source = '<tr><td><strong>Command</strong></td><td><code>php</code></td></tr>\n'
        translated = source.replace('Command', '命令')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('php', 'python'),
                        translated.replace('strong', 'em'),
                        translated.replace('<td>', '<td class="other">')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_learnku_table_container_requires_markdown_parsing(self):
        source = '<div class="overflow-auto">\n\n| Name |\n| --- |\n| Value |\n\n</div>\n'
        with self.assertRaisesRegex(ValueError, 'Markdown'):
            MODULE.validate(source, source)
        translated = source.replace('overflow-auto"', 'overflow-auto" markdown="1"')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        with self.assertRaises(ValueError):
            MODULE.validate(source, translated.replace('overflow-auto', 'other'))

    def test_container_markup_inside_code_remains_executable_content(self):
        source = '```blade\n<div class="overflow-auto">\n</div>\n```\n'
        self.assertEqual(MODULE.validate(source, source)['status'], 'passed')
        with self.assertRaises(ValueError):
            MODULE.validate(source, source.replace('overflow-auto"', 'overflow-auto" markdown="1"'))

    def test_method_heading_html_preserves_classes_and_api_name(self):
        source = '#### `bigIncrements()` {.collection-method .first-collection-method}\n'
        translated = '<h4 class="collection-method first-collection-method"><code>bigIncrements()</code></h4>\n'
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('bigIncrements', 'bigInteger'),
                        translated.replace(' first-collection-method', ''),
                        translated.replace('h4', 'h3')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_blade_comment_translation_preserves_executable_content(self):
        source = "```blade\n@can('update', $post)\n    <!-- The user can update the post. -->\n    <button>Update</button>\n@endcan\n```\n"
        translated = source.replace('The user can update the post.', '用户可以更新文章。')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('Update</button>', 'Delete</button>'),
                        translated.replace(' -->', ''),
                        translated.replace(' -->', ' --><script>run()</script>')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_inline_html_comment_does_not_hide_code_changes(self):
        source = '```blade\n<button>Update</button><!-- Explain -->\n```\n'
        with self.assertRaises(ValueError):
            MODULE.validate(source, source.replace('Update', 'Delete'))

    def test_php_inline_comment_translation_preserves_code(self):
        source = "```php\n'store' => 'passwords', // Optional...\n```\n"
        translated = source.replace('Optional...', '可选……')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace("'passwords'", "'other'"),
                        translated.replace(',', ';')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)
        self.source.write_text(source)
        self.translated.write_text(translated)
        result = self.run_cli('--lines', '2:2')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "'store' => 'passwords', // 可选……\n")

    def test_php_comment_markers_in_strings_remain_code(self):
        source = '''```php
$url = 'https://example.com/reset'; // Explain
$text = "escaped \\\" // literal"; // Explain
$multiline = 'first line
// This is string content
last line'; // Explain
```
'''
        translated = source.replace('// Explain', '// 说明')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('/reset', '/other'),
                        translated.replace('// literal', '// changed'),
                        translated.replace('// This is string content', '// 字符串内容')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_non_php_inline_comment_markers_remain_code(self):
        for language in ['ini', 'shell', 'blade']:
            source = f'```{language}\nvalue // literal\n```\n'
            with self.assertRaises(ValueError):
                MODULE.validate(source, source.replace('literal', 'changed'))

    def test_php_blank_line_whitespace_can_be_cleaned(self):
        source = "```php\n$value = 1;\n    \n$value++;\n```\n"
        translated = source.replace('\n    \n', '\n\n')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('$value++;', '$value--;'),
                        translated.replace('\n\n', '\n'),
                        source]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_php_multiline_string_blank_whitespace_remains_content(self):
        source = "```php\n$text = 'first\n    \nlast';\n```\n"
        with self.assertRaises(ValueError):
            MODULE.validate(source, source.replace('\n    \n', '\n\n'))

    def test_sql_hash_comment_translation_preserves_statements(self):
        source = '```sql\n# Offset pagination\nselect * from users limit 15; # Explain\n```\n'
        translated = source.replace('Offset pagination', '偏移量分页').replace('Explain', '说明')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('limit 15', 'limit 30'),
                        translated.replace('; #', ' #')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_sql_hash_markers_in_strings_remain_content(self):
        source = "```sql\nselect '#literal', 'it''s #literal', 'first\n# literal\nlast'; # Explain\n```\n"
        translated = source.replace('Explain', '说明')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('#literal', '#changed'),
                        translated.replace('# literal', '# 修改')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_shell_standalone_comment_translation_preserves_commands(self):
        source = '```shell\n# Refresh the database\nphp artisan migrate:refresh --seed\n```\n'
        translated = source.replace('Refresh the database', '刷新数据库')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        with self.assertRaises(ValueError):
            MODULE.validate(source, translated.replace('--seed', '--force'))

    def test_shell_hash_in_strings_and_expansions_remains_code(self):
        source = "```shell\necho ${#name}\nprintf '#literal'\nprintf 'first\n# literal\nlast'\n# Explain\n```\n"
        translated = source.replace('Explain', '说明')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('${#name}', '${#other}'),
                        translated.replace('#literal', '#changed'),
                        translated.replace('# literal', '# 修改')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_yaml_standalone_comment_translation_preserves_ci_commands(self):
        source = '```yaml\n# Include Chrome\nservices:\n  - dusk\npipeline:\n  - cmd: |\n      # Create a Dusk environment\n      cp .env .env.dusk.ci\n```\n'
        translated = source.replace('Include Chrome', '包含 Chrome').replace('Create a Dusk environment', '创建 Dusk 环境')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('  - dusk', '  - other'),
                        translated.replace('cp .env .env.dusk.ci', 'cp .env .env.production'),
                        translated.replace('      # 创建', '    # 创建')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_yaml_hash_markers_in_quoted_values_remain_content(self):
        source = "```yaml\nvalue: '#literal'\ntext: 'first\n# literal\nlast'\n# Explain\n```\n"
        translated = source.replace('Explain', '说明')
        self.assertEqual(MODULE.validate(source, translated)['status'], 'passed')
        for changed in [translated.replace('#literal', '#changed'),
                        translated.replace('# literal', '# 修改')]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)

    def test_validation_catches_anchor_fence_and_whitespace_changes(self):
        source = self.source.read_text()
        translated = self.translated.read_text()
        for changed in [translated.replace('name="new"', 'name="other"'), translated.replace('```php', '```'), translated.replace('# 简介\n', '# 简介 \n'), translated.rsplit('```', 1)[0]]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)


if __name__ == '__main__':
    unittest.main()
