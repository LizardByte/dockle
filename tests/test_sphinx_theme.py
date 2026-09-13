from __future__ import annotations

import unittest

from dockle.sphinx_theme import THEME_DIRECTORY, setup


class FakeSphinxApp:
    def __init__(self) -> None:
        self.themes: list[tuple[str, object]] = []

    def add_html_theme(self, name: str, path: object) -> None:
        self.themes.append((name, path))


class SphinxThemeTests(unittest.TestCase):
    def test_setup_registers_first_party_theme(self) -> None:
        app = FakeSphinxApp()

        metadata = setup(app)

        self.assertEqual(app.themes, [("dockle", THEME_DIRECTORY)])
        self.assertTrue(metadata["parallel_write_safe"])

    def test_theme_contains_owned_template_and_assets(self) -> None:
        self.assertTrue((THEME_DIRECTORY / "theme.toml").is_file())
        self.assertTrue((THEME_DIRECTORY / "layout.html").is_file())
        self.assertTrue((THEME_DIRECTORY / "static" / "dockle.css").is_file())
        self.assertTrue((THEME_DIRECTORY / "static" / "dockle.js").is_file())
        self.assertTrue((THEME_DIRECTORY / "main.html").is_file())
        self.assertTrue((THEME_DIRECTORY / "mkdocs_theme.yml").is_file())
        self.assertNotIn(
            "furo",
            (THEME_DIRECTORY / "theme.toml")
            .read_text(encoding="utf-8")
            .lower(),
        )


if __name__ == "__main__":
    unittest.main()
