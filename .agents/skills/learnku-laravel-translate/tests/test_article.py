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

    def test_validation_catches_anchor_fence_and_whitespace_changes(self):
        source = self.source.read_text()
        translated = self.translated.read_text()
        for changed in [translated.replace('name="new"', 'name="other"'), translated.replace('```php', '```'), translated.replace('# 简介\n', '# 简介 \n'), translated.rsplit('```', 1)[0]]:
            with self.assertRaises(ValueError):
                MODULE.validate(source, changed)


if __name__ == '__main__':
    unittest.main()
