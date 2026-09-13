from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

from dockle.config import load_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProjectDogfoodTests(unittest.TestCase):
    def test_root_config_exercises_every_adapter(self) -> None:
        config = load_config(PROJECT_ROOT / "dockle.toml")

        self.assertEqual(
            [target.framework for target in config.targets],
            ["sphinx", "doxygen", "mkdocs", "jsdoc", "rustdoc"],
        )
        for target in config.targets:
            self.assertTrue(target.source.exists(), target.source)
        self.assertEqual(config.project.home, PROJECT_ROOT / "docs" / "home.md")
        self.assertEqual(
            config.project.logo,
            PROJECT_ROOT / "branding" / "dockle-logo.png",
        )

    def test_common_cpp_lint_submodule_is_configured(self) -> None:
        modules = (PROJECT_ROOT / ".gitmodules").read_text(encoding="utf-8")

        self.assertIn("third-party/lizardbyte-common", modules)
        self.assertIn("LizardByte/lizardbyte-common.git", modules)
        clang_format = (PROJECT_ROOT / ".clang-format").read_text(
            encoding="utf-8"
        )
        self.assertIn("centrally managed", clang_format)

    def test_read_the_docs_build_publishes_dockle_output(self) -> None:
        contents = (PROJECT_ROOT / ".readthedocs.yaml").read_text(
            encoding="utf-8"
        )

        self.assertIn("commands:", contents)
        self.assertNotIn("jobs:", contents)
        self.assertIn(
            'conda env create --quiet --name "${READTHEDOCS_VERSION}"',
            contents,
        )
        self.assertIn(
            'conda run --no-capture-output --name "${READTHEDOCS_VERSION}" python -m dockle check',
            contents,
        )
        self.assertIn(
            'conda run --no-capture-output --name "${READTHEDOCS_VERSION}" python -m dockle build',
            contents,
        )
        self.assertIn("${READTHEDOCS_OUTPUT}html/", contents)
        self.assertIn("npm ci --ignore-scripts", contents)
        self.assertIn('python: "miniforge3-26.3"', contents)
        self.assertIn("environment: environment.yml", contents)

        environment = (PROJECT_ROOT / "environment.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("- doxygen==1.18.0", environment)
        self.assertIn("- graphviz==14.1.2", environment)
        self.assertIn("- pip==26.2.1", environment)
        self.assertIn("- python==3.13.15", environment)

    def test_conda_dependencies_are_hard_pinned(self) -> None:
        lines = (
            (PROJECT_ROOT / "environment.yml")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        dependencies = []
        for line in lines[lines.index("dependencies:") + 1:]:
            if line and not line.startswith(" "):
                break
            if line.startswith("  - "):
                dependencies.append(line.removeprefix("  - "))

        self.assertTrue(dependencies)
        for dependency in dependencies:
            self.assertRegex(
                dependency, r"^[A-Za-z0-9_.-]+==[A-Za-z0-9_.+-]+$"
            )

    def test_furo_is_not_a_package_dependency(self) -> None:
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
            project = tomllib.load(stream)["project"]
        declared = list(project.get("dependencies", []))
        for extra in project.get("optional-dependencies", {}).values():
            declared.extend(extra)

        self.assertNotIn("furo", " ".join(declared).lower())

    def test_reference_doxygen_projects_are_not_dependencies(self) -> None:
        dependency_files = [
            PROJECT_ROOT / "pyproject.toml",
            PROJECT_ROOT / "package.json",
            PROJECT_ROOT / ".gitmodules",
        ]

        declared = "\n".join(
            path.read_text(encoding="utf-8") for path in dependency_files
        ).lower()
        self.assertNotIn("doxygen-awesome-css", declared)
        self.assertNotIn("doxyconfig", declared)


if __name__ == "__main__":
    unittest.main()
