from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dockle.config import ThemeConfig
from dockle.theme import ThemeError, apply_theme, render_theme


class ThemeTests(unittest.TestCase):
    def test_render_theme_includes_configured_tokens(self) -> None:
        stylesheet = render_theme(
            ThemeConfig(primary="#abcdef", dark_background="#010203")
        )

        self.assertIn("--dockle-primary: #abcdef", stylesheet)
        self.assertIn("--dockle-background: #010203", stylesheet)
        self.assertIn("body > nav", stylesheet)

    def test_apply_theme_uses_relative_asset_paths_for_nested_pages(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            nested = output / "api" / "types"
            nested.mkdir(parents=True)
            html = nested / "index.html"
            html.write_text(
                "<html><head></head><body></body></html>", encoding="utf-8"
            )

            count = apply_theme(
                output, "rustdoc", "body { color: red; }", portal=output.parent
            )

            document = html.read_text(encoding="utf-8")
            self.assertEqual(count, 1)
            self.assertIn("../../_dockle/dockle.css", document)
            self.assertIn('data-dockle-framework="rustdoc"', document)
            self.assertIn("../../../index.html", document)
            self.assertIn("data-dockle-home", document)
            self.assertIn("data-dockle-universal-search", document)
            self.assertIn("../../_dockle/search.json", document)
            self.assertTrue((output / "_dockle" / "search.json").is_file())

    def test_apply_theme_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            html = output / "index.html"
            html.write_text(
                "<html><head></head><body></body></html>", encoding="utf-8"
            )

            first = apply_theme(output, "jsdoc", "body {}")
            second = apply_theme(output, "jsdoc", "body {}")

            self.assertEqual(first, 1)
            self.assertEqual(second, 0)

    def test_apply_theme_rejects_malformed_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "index.html").write_text(
                "<html><body></body></html>", encoding="utf-8"
            )

            with self.assertRaisesRegex(ThemeError, "closing head"):
                apply_theme(output, "jsdoc", "body {}")

    def test_native_theme_gets_framework_marker_without_duplicate_stylesheet(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            html = output / "index.html"
            html.write_text(
                '<html><head><link rel="stylesheet" href="dockle.css"></head><body></body></html>',
                encoding="utf-8",
            )

            count = apply_theme(
                output,
                "doxygen",
                "unused",
                portal=output.parent,
                project_name="Dockle",
                project_version="0.1.0",
            )

            document = html.read_text(encoding="utf-8")
            self.assertEqual(count, 1)
            self.assertIn('data-dockle-framework="doxygen"', document)
            self.assertIn("data-dockle-brand", document)
            self.assertEqual(document.count("dockle.css"), 1)

    def test_apply_theme_copies_and_exposes_project_logo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "site"
            output.mkdir()
            logo = root / "logo.png"
            logo.write_bytes(b"image")
            html = output / "index.html"
            html.write_text(
                "<html><head></head><body></body></html>",
                encoding="utf-8",
            )

            apply_theme(output, "jsdoc", "body {}", logo=logo)

            document = html.read_text(encoding="utf-8")
            self.assertTrue((output / "_dockle" / "logo.png").is_file())
            self.assertIn('data-dockle-logo-url="_dockle/logo.png"', document)


if __name__ == "__main__":
    unittest.main()
