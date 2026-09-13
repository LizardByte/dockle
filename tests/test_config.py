from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dockle.config import ConfigError, load_config

MINIMAL_CONFIG = """
[project]
name = "Example"

[[targets]]
name = "manual"
framework = "sphinx"
source = "docs"
"""


class ConfigTests(unittest.TestCase):
    def test_loads_defaults_and_resolves_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "dockle.toml"
            path.write_text(MINIMAL_CONFIG, encoding="utf-8")

            config = load_config(path)

            self.assertEqual(config.project.name, "Example")
            self.assertEqual(config.build.output, root.resolve() / "_site")
            self.assertEqual(config.targets[0].source, root.resolve() / "docs")
            self.assertEqual(
                config.targets[0].output, root.resolve() / "_site" / "manual"
            )
            self.assertEqual(config.targets[0].title, "Manual")
            self.assertEqual(config.targets[0].description, "")
            self.assertTrue(config.build.strict)
            self.assertTrue(config.build.clean)

    def test_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            contents = MINIMAL_CONFIG.replace(
                'name = "Example"', 'name = "Example"\ncolour = "blue"'
            )
            path.write_text(contents, encoding="utf-8")

            with self.assertRaisesRegex(ConfigError, "unknown key.*colour"):
                load_config(path)

    def test_resolves_project_home_and_logo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "home.md").write_text("# Home\n", encoding="utf-8")
            (root / "logo.png").write_bytes(b"logo")
            path = root / "dockle.toml"
            contents = MINIMAL_CONFIG.replace(
                'name = "Example"',
                'name = "Example"\nhome = "home.md"\nlogo = "logo.png"',
            )
            path.write_text(contents, encoding="utf-8")

            config = load_config(path)

            self.assertEqual(config.project.home, (root / "home.md").resolve())
            self.assertEqual(config.project.logo, (root / "logo.png").resolve())

    def test_rejects_missing_project_asset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            contents = MINIMAL_CONFIG.replace(
                'name = "Example"',
                'name = "Example"\nlogo = "missing.png"',
            )
            path.write_text(contents, encoding="utf-8")

            with self.assertRaisesRegex(ConfigError, "project.logo"):
                load_config(path)

    def test_rejects_theme_values_that_could_escape_css(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            path.write_text(
                MINIMAL_CONFIG.replace(
                    "[[targets]]",
                    '[theme]\nprimary = "red; display: none"\n\n[[targets]]',
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ConfigError, "unsafe in CSS"):
                load_config(path)

    def test_rejects_output_outside_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            path.write_text(
                MINIMAL_CONFIG.replace(
                    "[[targets]]",
                    '[build]\noutput = "../published"\n\n[[targets]]',
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ConfigError, "build.output"):
                load_config(path)

    def test_rejects_duplicate_target_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            path.write_text(
                MINIMAL_CONFIG
                + """
[[targets]]
name = "manual"
framework = "mkdocs"
source = "guide"
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ConfigError, "duplicate target name"):
                load_config(path)

    def test_rejects_overlapping_target_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            path.write_text(
                MINIMAL_CONFIG.replace(
                    'name = "manual"', 'name = "manual"\noutput = "reference"'
                )
                + """
[[targets]]
name = "api"
framework = "doxygen"
source = "src"
output = "reference/api"
""",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ConfigError, "output overlaps"):
                load_config(path)

    def test_rejects_entry_outside_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            path.write_text(
                MINIMAL_CONFIG.replace(
                    'source = "docs"', 'source = "docs"\nentry = "../README"'
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ConfigError, "entry must be a relative path"
            ):
                load_config(path)

    def test_selects_targets_in_configuration_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            path.write_text(
                MINIMAL_CONFIG
                + """
[[targets]]
name = "api"
framework = "doxygen"
source = "src"
""",
                encoding="utf-8",
            )
            config = load_config(path)

            selected = config.select_targets(["api", "manual"])

            self.assertEqual(
                [target.name for target in selected], ["manual", "api"]
            )

    def test_allows_project_root_as_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dockle.toml"
            path.write_text(
                MINIMAL_CONFIG.replace(
                    'framework = "sphinx"', 'framework = "rustdoc"'
                ).replace('source = "docs"', 'source = "."'),
                encoding="utf-8",
            )

            config = load_config(path)

            self.assertEqual(config.targets[0].source, path.parent.resolve())


if __name__ == "__main__":
    unittest.main()
