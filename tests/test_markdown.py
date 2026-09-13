from __future__ import annotations

import unittest

from dockle.markdown import normalize_github_alerts, render_markdown


class MarkdownTests(unittest.TestCase):
    def test_converts_github_alert_to_markdown_admonition(self) -> None:
        source = "> [!WARNING]\n> Generated files are temporary.\n"

        converted = normalize_github_alerts(source)

        self.assertIn("!!! warning", converted)
        self.assertIn("    Generated files are temporary.", converted)

    def test_renders_github_alert_with_semantic_classes(self) -> None:
        document = render_markdown("> [!NOTE]\n> One configuration.\n")

        self.assertIn('class="admonition note"', document)
        self.assertIn('class="admonition-title"', document)


if __name__ == "__main__":
    unittest.main()
