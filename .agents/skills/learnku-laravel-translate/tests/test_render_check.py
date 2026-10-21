import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'render_check.py'
SPEC = importlib.util.spec_from_file_location('render_check', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RenderCheckTests(unittest.TestCase):
    def setUp(self):
        self.markdown = '# 标题\n\n<a name="table"></a>\n<div class="overflow-auto" markdown="1">\n\n| 方法 | 说明 |\n| --- | --- |\n| `run()` | 运行 |\n\n</div>\n\n```markdown\n| 示例 |\n| --- |\n| 保留源码 |\n```\n'
        self.observed = {'headings': [1], 'codeBlocks': 1, 'tables': [2],
                         'anchors': ['table'], 'links': [], 'rawMarkdown': [],
                         'rawHeadingClasses': [], 'codeImages': [], 'containers': [], 'listItems': 0}

    def test_counts_only_tables_outside_code_examples(self):
        self.assertEqual(MODULE.manifest(self.markdown)['tables'], [2])
        self.assertEqual(MODULE.check(self.markdown, self.observed)['status'], 'passed')

    def test_missing_table_and_literal_markdown_fail(self):
        for updates in [{'tables': []}, {'tables': [1]}, {'rawMarkdown': ['| --- |']}]:
            with self.assertRaises(ValueError):
                MODULE.check(self.markdown, dict(self.observed, **updates))

    def test_missing_code_heading_anchor_and_unrendered_classes_fail(self):
        for updates in [{'codeBlocks': 0}, {'headings': [2]}, {'anchors': []},
                        {'rawHeadingClasses': ['run() {.collection-method}']},
                        {'codeImages': [':MM:']}]:
            with self.assertRaises(ValueError):
                MODULE.check(self.markdown, dict(self.observed, **updates))

    def test_method_links_and_html_heading_are_checked(self):
        source = '[run](#run)\n<a name="run"></a>\n<h4 class="collection-method"><code>run()</code></h4>\n'
        observation = dict(self.observed, headings=[4], tables=[], codeBlocks=0,
                           anchors=['run'], links=['#run'])
        self.assertEqual(MODULE.check(source, observation)['status'], 'passed')
        with self.assertRaises(ValueError):
            MODULE.check(source, dict(observation, links=[]))

    def test_absent_observation_cannot_pass(self):
        with self.assertRaises(ValueError):
            MODULE.check(self.markdown, {})

    def test_indented_code_is_counted_but_css_and_nested_lists_are_not(self):
        markdown = '# 配置\n\n    "default": "/Users/Sally/Sites/example",\n\n<style>\n\n    .example { color: red; }\n</style>\n\n- 父项\n    - 子项\n'
        expected = MODULE.manifest(markdown)
        self.assertEqual(expected['codeBlocks'], 1)
        self.assertEqual(expected['listItems'], 2)


if __name__ == '__main__':
    unittest.main()
