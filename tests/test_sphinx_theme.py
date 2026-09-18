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
            (THEME_DIRECTORY / "static" / "lucide.min.js").is_file()
        )
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

    def test_sidebar_identity_stays_pinned_and_compacts_on_scroll(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn(".dockle-sidebar::before", stylesheet)
        self.assertIn("--dockle-sidebar-header-height", stylesheet)
        self.assertIn("scrollbar-gutter: stable", stylesheet)
        self.assertIn("data-dockle-has-logo", stylesheet)
        self.assertIn("data-dockle-sidebar-compact", stylesheet)
        self.assertIn("const sidebarScroller", script)
        self.assertIn("--dockle-sidebar-logo-size: 4.5rem", stylesheet)
        self.assertIn(
            "padding: var(--dockle-sidebar-header-height)", stylesheet
        )
        self.assertIn("overflow-anchor: none", stylesheet)
        self.assertIn("sidebarScroller.scrollTop >= 72", script)

    def test_sidebar_brand_links_share_hover_and_type_spacing(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")

        self.assertIn(".dockle-compat-brand:hover", stylesheet)
        self.assertIn(".dockle-brand a:hover", stylesheet)
        self.assertIn("line-height: 1.3", stylesheet)

    def test_content_columns_keep_a_stable_wide_screen_origin(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")

        self.assertIn("--dockle-column-gap", stylesheet)
        self.assertIn("justify-content: start", stylesheet)
        self.assertIn(
            'body.rustdoc:not(.src) > main {',
            stylesheet,
        )
        self.assertIn(
            "var(--dockle-content-width) + var(--dockle-column-gap)",
            stylesheet,
        )

    def test_attribution_resets_framework_typography(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")
        attribution = stylesheet.split(
            ".dockle-footer,\n.dockle-built-with {", 1
        )[1].split("}", 1)[0]

        self.assertIn("font-style: normal", attribution)

    def test_compatibility_adapters_receive_right_page_navigation(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("ensureCompatibilityPageToc", script)
        self.assertIn('["doxygen", "jsdoc", "rustdoc"]', script)
        self.assertIn("dockle-compat-toc", script)
        self.assertIn(".dockle-compat-toc", stylesheet)
        self.assertIn("border-left: 0 !important", stylesheet)

    def test_code_blocks_receive_shared_copy_controls(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("addCodeCopyButtons", script)
        self.assertIn('button.className = "dockle-copy-button"', script)
        self.assertIn('data-lucide="copy"', script)
        self.assertIn(".dockle-copy-button", stylesheet)
        self.assertNotIn(
            ".dockle-code-block:hover > .dockle-copy-button",
            stylesheet,
        )
        self.assertIn("div.fragment .clipboard", stylesheet)
        self.assertIn(
            '#nav-tree a:hover {\n  background-image: none !important;',
            stylesheet,
        )
        self.assertIn("font-size: 1rem !important", stylesheet)
        self.assertIn("text-indent: 0 !important", stylesheet)

    def test_rustdoc_uses_shared_lucide_toolbar_icons(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("replaceRustdocIcons", script)
        self.assertIn('["#copy-path", "copy"]', script)
        self.assertIn('[".settings-menu > a", "settings"]', script)
        self.assertIn('[".help-menu > a", "circle-help"]', script)
        self.assertIn(
            '["button#toggle-all-docs", "chevrons-down"]',
            script,
        )
        self.assertIn(".dockle-rustdoc-icon", stylesheet)
        self.assertIn("#copy-path::before", stylesheet)
        self.assertIn(
            '.dockle-code-block > pre > code {\n'
            "  background: transparent !important;\n"
            "  border-radius: 0 !important;",
            stylesheet,
        )
        self.assertIn(
            '.dockle-code-block\n  > .button-holder {\n'
            "  display: none !important;",
            stylesheet,
        )

    def test_footer_moves_into_each_framework_content_column(self) -> None:
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn('doxygen: "#doc-content .contents"', script)
        self.assertIn('jsdoc: "#main"', script)
        self.assertIn('mkdocs: ".dockle-article"', script)
        self.assertIn('rustdoc: "#main-content"', script)
        self.assertIn('sphinx: ".dockle-article"', script)

    def test_headings_receive_shared_lucide_permalinks(self) -> None:
        stylesheet = (
            THEME_DIRECTORY / "static" / "dockle.css"
        ).read_text(encoding="utf-8")
        script = (THEME_DIRECTORY / "static" / "dockle.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("addHeadingPermalinks", script)
        self.assertIn("globalThis.lucide", script)
        self.assertIn("lucide.createIcons", script)
        self.assertNotIn("const iconNodes", script)
        self.assertIn('link.className = "dockle-heading-anchor"', script)
        self.assertIn('data-lucide="pilcrow"', script)
        self.assertIn(".headerlink, :scope > .doc-anchor", script)
        self.assertIn(
            'pageNav.querySelectorAll(".dockle-heading-anchor")', script
        )
        self.assertIn(".dockle-heading-anchor", stylesheet)
        self.assertIn(
            ":where(h1, h2, h3, h4, h5, h6):hover", stylesheet
        )
        self.assertIn(".dockle-heading-anchor:focus-visible", stylesheet)


if __name__ == "__main__":
    unittest.main()
