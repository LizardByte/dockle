from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from stat import S_IXUSR
from unittest.mock import patch

from dockle import __version__
from dockle.builders import BuildManager, Command
from dockle.config import load_config

ALL_TARGETS_CONFIG = """
[project]
name = "Example API"
version = "2.4.0"
description = "Example documentation"
repository = "https://example.invalid/project"
favicon = "favicon.svg"

[theme]
primary = "#7c4dff"

[build]
strict = true

[[targets]]
name = "sphinx"
framework = "sphinx"
source = "sphinx-docs"

[[targets]]
name = "doxygen"
framework = "doxygen"
source = "cpp"

[[targets]]
name = "mkdocs"
framework = "mkdocs"
source = "markdown"

[[targets]]
name = "jsdoc"
framework = "jsdoc"
source = "javascript"

[[targets]]
name = "rustdoc"
framework = "rustdoc"
source = "rust"
"""


class RecordingRunner:
    def __init__(self, html_output: Path) -> None:
        self.html_output = html_output
        self.commands: list[Command] = []

    def run(self, command: Command) -> None:
        self.commands.append(command)
        self.html_output.mkdir(parents=True, exist_ok=True)
        is_jsdoc = any("jsdoc.json" in argument for argument in command.args)
        root = ' data-dockle-framework="jsdoc"' if is_jsdoc else ""
        favicon = (
            '<link data-dockle-favicon><link data-dockle-theme="jsdoc">'
            if is_jsdoc
            else ""
        )
        (self.html_output / "index.html").write_text(
            f"<!doctype html><html{root}><head><title>Fixture</title>"
            f"{favicon}</head><body><main>Docs</main></body></html>",
            encoding="utf-8",
        )
        if is_jsdoc:
            (self.html_output / "dockle.css").write_text(
                "body {}", encoding="utf-8"
            )
            (self.html_output / "dockle-favicon.svg").write_text(
                "<svg/>", encoding="utf-8"
            )


class BuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        for name in ("sphinx-docs", "cpp", "markdown", "javascript", "rust"):
            (self.root / name).mkdir()
        (self.root / "favicon.svg").write_text("<svg/>", encoding="utf-8")
        self.config_path = self.root / "dockle.toml"
        self.config_path.write_text(ALL_TARGETS_CONFIG, encoding="utf-8")
        self.config = load_config(self.config_path)
        self.manager = BuildManager(self.config)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_sphinx_plan_uses_dockle_theme_and_generated_config(self) -> None:
        plan = self.manager.plan(self.config.targets[0])
        conf = plan.generated_files[plan.work / "conf.py"]

        self.assertIn("html_theme = 'dockle'", conf)
        self.assertIn("'dockle.sphinx_theme'", conf)
        self.assertIn("'myst_parser'", conf)
        self.assertIn("myst_enable_extensions = ['alert']", conf)
        self.assertIn("'sphinx.ext.autodoc'", conf)
        self.assertIn("#7c4dff", conf)
        self.assertIn("-W", plan.command.args)
        self.assertNotIn("conf.py", plan.command.args)

    def test_doxygen_plan_uses_supported_extra_stylesheet_hook(self) -> None:
        (self.config.targets[1].source / "index").write_text(
            "# API\n", encoding="utf-8"
        )
        plan = self.manager.plan(self.config.targets[1])
        doxyfile = plan.generated_files[plan.work / "Doxyfile"]

        self.assertIn("HTML_EXTRA_STYLESHEET", doxyfile)
        self.assertIn("GENERATE_TREEVIEW", doxyfile)
        self.assertIn("WARN_AS_ERROR", doxyfile)
        self.assertIn("USE_MDFILE_AS_MAINPAGE", doxyfile)
        self.assertIn(
            "EXTENSION_MAPPING        = python=Python "
            "javascript=JavaScript typescript=JavaScript "
            "json=JavaScript csharp=Csharp "
            "objective-c=Objective-C",
            doxyfile,
        )
        self.assertIn('ALIASES                += "danger{1}', doxyfile)
        self.assertIn('"_dockle_alert{4|:|}', doxyfile)
        self.assertIn('"admonition{2|:|}', doxyfile)
        self.assertIn("\\1|:|note|:|info|:|\\2", doxyfile)
        self.assertIn('data-lucide=\\"\\3\\"', doxyfile)
        self.assertIn(
            "dockle-alert-\\2\\\"><dt",
            doxyfile,
        )
        self.assertNotIn("dockle-alert- \\2", doxyfile)

    def test_mkdocs_plan_generates_only_dockle_owned_config(self) -> None:
        plan = self.manager.plan(self.config.targets[2])
        native = plan.generated_files[plan.work / "mkdocs.yml"]

        self.assertIn('site_name: "Example API"', native)
        self.assertIn('repo_url: "https://example.invalid/project"', native)
        self.assertIn('edit_uri: ""', native)
        self.assertIn("name: dockle", native)
        self.assertIn('primary: "#7c4dff"', native)
        self.assertIn("- dockle.markdown", native)
        self.assertIn("  - codehilite:", native)
        self.assertIn("      guess_lang: false", native)
        self.assertIn("      pygments_lang_class: true", native)
        self.assertIn(f'dockle_version: "{__version__}"', native)
        self.assertIn("--strict", plan.command.args)

    def test_frozen_build_uses_bundled_python_generators(self) -> None:
        with patch.object(sys, "frozen", True, create=True):
            sphinx = self.manager.plan(self.config.targets[0])
            mkdocs = self.manager.plan(self.config.targets[2])

        self.assertEqual(sphinx.command.args[:2], (sys.executable, "_run-sphinx"))
        self.assertEqual(mkdocs.command.args[:2], (sys.executable, "_run-mkdocs"))

    def test_jsdoc_plan_generates_json(self) -> None:
        (self.config.targets[3].source / "index").write_text(
            "# API\n", encoding="utf-8"
        )
        plan = self.manager.plan(self.config.targets[3])
        native = plan.generated_files[plan.work / "jsdoc.json"]

        self.assertIn('"destination"', native)
        self.assertIn('"recurse": true', native)
        self.assertIn('"readme"', native)
        self.assertIn('"template"', native)
        self.assertIn('"dockleVersion"', native)
        self.assertIn('"projectName": "Example API"', native)
        self.assertIn('"targetTitle": "Jsdoc"', native)
        self.assertIn('"stylesheet"', native)
        self.assertIn(
            plan.work / "theme" / "dockle.css", plan.generated_files
        )
        self.assertEqual(plan.command.args[1], "--configure")
        self.assertIn("--pedantic", plan.command.args)

    def test_jsdoc_plan_discovers_tutorials(self) -> None:
        source = self.config.targets[3].source
        (source / "tutorials").mkdir()
        plan = self.manager.plan(self.config.targets[3])
        native = plan.generated_files[plan.work / "jsdoc.json"]

        self.assertIn('"tutorials"', native)

    def test_rustdoc_plan_uses_cargo_without_dependencies(self) -> None:
        plan = self.manager.plan(self.config.targets[4])

        self.assertEqual(plan.command.args[1], "doc")
        self.assertIn("--no-deps", plan.command.args)
        self.assertTrue(
            plan.command.env["RUSTDOCFLAGS"].endswith("-D warnings")
        )

    def test_build_writes_generated_config_and_themes_html(self) -> None:
        fake_tool = self.root / "fake-jsdoc"
        fake_tool.touch()
        configured = ALL_TARGETS_CONFIG.replace(
            "[build]\nstrict = true",
            '[build]\nstrict = true\n\n[tools]\njsdoc = "./fake-jsdoc"',
        )
        self.config_path.write_text(configured, encoding="utf-8")
        config = load_config(self.config_path)
        target = config.select_targets(["jsdoc"])[0]
        runner = RecordingRunner(target.output)

        result = BuildManager(config, runner=runner).build((target,))

        self.assertEqual(result[0].themed_pages, 1)
        generated = (config.build.work / "jsdoc" / "jsdoc.json").read_text(
            encoding="utf-8"
        )
        html = (target.output / "index.html").read_text(encoding="utf-8")
        self.assertIn('"destination"', generated)
        self.assertIn('data-dockle-theme="jsdoc"', html)
        self.assertIn('data-dockle-framework="jsdoc"', html)
        self.assertTrue((target.output / "dockle.css").is_file())
        self.assertTrue((target.output / "dockle-favicon.svg").is_file())
        self.assertIn("data-dockle-favicon", html)
        portal = (config.build.output / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('data-dockle-framework="portal"', portal)
        self.assertIn('href="jsdoc/"', portal)
        self.assertIn("data-dockle-favicon", portal)

    def test_resolves_project_local_node_tool(self) -> None:
        executable = (
            self.root
            / "node_modules"
            / ".bin"
            / ("jsdoc.cmd" if sys.platform == "win32" else "jsdoc")
        )
        executable.parent.mkdir(parents=True)
        executable.touch()
        executable.chmod(executable.stat().st_mode | S_IXUSR)

        plan = self.manager.plan(self.config.targets[3], require_tool=True)

        self.assertTrue(Path(plan.command.args[0]).samefile(executable))

    def test_full_build_removes_stale_target_output(self) -> None:
        fake_tool = self.root / "fake-sphinx"
        fake_tool.touch()
        configured = ALL_TARGETS_CONFIG.replace(
            "[build]\nstrict = true",
            '[build]\nstrict = true\n\n[tools]\nsphinx = "./fake-sphinx"',
        )
        self.config_path.write_text(configured, encoding="utf-8")
        config = load_config(self.config_path)
        stale = config.build.output / "removed-target" / "index.html"
        stale.parent.mkdir(parents=True)
        stale.write_text("stale", encoding="utf-8")
        target = config.targets[0]

        BuildManager(config, runner=RecordingRunner(target.output)).build(
            config.targets[:1]
        )
        self.assertTrue(
            stale.is_file(),
            "a selected build must preserve other target outputs",
        )

        # A complete build owns the whole output tree. Use a runner that writes
        # minimal HTML wherever each adapter expects native output.
        class MultiTargetRunner:
            def run(inner_self, command: Command) -> None:
                for candidate in config.targets:
                    native_output = candidate.output
                    if candidate.framework == "rustdoc":
                        native_output = (
                            config.build.work
                            / candidate.name
                            / "cargo-target"
                            / "doc"
                            / "fixture"
                        )
                    native_output.mkdir(parents=True, exist_ok=True)
                    root = (
                        ' data-dockle-framework="jsdoc"'
                        if candidate.framework == "jsdoc"
                        else ""
                    )
                    (native_output / "index.html").write_text(
                        f"<!doctype html><html{root}><head></head>"
                        "<body>Docs</body></html>",
                        encoding="utf-8",
                    )

        # Point every native executable at the same harmless file; the custom
        # runner records no process invocation.
        frameworks = sorted({target.framework for target in config.targets})
        tools = "\n".join(
            f'{framework} = "./fake-sphinx"' for framework in frameworks
        )
        self.config_path.write_text(
            configured.replace('sphinx = "./fake-sphinx"', tools),
            encoding="utf-8",
        )
        config = load_config(self.config_path)
        BuildManager(config, runner=MultiTargetRunner()).build(config.targets)

        self.assertFalse(stale.exists())


if __name__ == "__main__":
    unittest.main()
