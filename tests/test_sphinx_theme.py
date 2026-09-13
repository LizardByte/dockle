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
        self.assertTrue(
            (THEME_DIRECTORY / "static" / "LUCIDE_LICENSE.txt").is_file()
        )
        self.assertTrue((THEME_DIRECTORY / "main.html").is_file())
        self.assertTrue((THEME_DIRECTORY / "mkdocs_theme.yml").is_file())
        self.assertNotIn(
            "furo",
            (THEME_DIRECTORY / "theme.toml")
            .read_text(encoding="utf-8")
            .lower(),
        )

    def test_theme_supports_auto_light_and_dark_modes(self) -> None:
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn('["auto", "light", "dark"]', script)
        self.assertIn('auto: "monitor"', script)
        self.assertIn("localStorage.removeItem(storageKey)", script)

    def test_admonitions_use_one_left_accent_layout(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")

        self.assertIn("dl.dockle-alert", stylesheet)
        self.assertIn(
            "border-left: 0.25rem solid var(--dockle-alert-color)",
            stylesheet,
        )
        self.assertNotIn(
            "border-top: 0.25rem solid var(--dockle-alert-color)",
            stylesheet,
        )

    def test_compatibility_sidebars_share_current_page_styles(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn('#nav-tree a[href="javascript:void(0)"]', stylesheet)
        self.assertIn("a.dockle-current", stylesheet)
        self.assertIn("markCurrentNavigation", script)


if __name__ == "__main__":
    unittest.main()
