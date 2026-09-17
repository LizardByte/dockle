from __future__ import annotations

import json
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
            ["sphinx", "sphinx", "doxygen", "mkdocs", "jsdoc", "rustdoc"],
        )
        for target in config.targets:
            self.assertTrue(target.source.exists(), target.source)
        self.assertIsNone(config.project.home)
        self.assertTrue(config.targets[0].home)
        self.assertEqual(config.targets[0].output, config.build.output)
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

    def test_lucide_runtime_is_managed_by_npm(self) -> None:
        with (PROJECT_ROOT / "package.json").open(encoding="utf-8") as stream:
            package = json.load(stream)
        version = package["dependencies"]["lucide"]
        runtime = (
            PROJECT_ROOT
            / "src"
            / "dockle"
            / "sphinx"
            / "themes"
            / "dockle"
            / "static"
            / "lucide.min.js"
        ).read_text(encoding="utf-8")

        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertTrue(
            runtime.startswith(f"/*! Lucide {version} | ISC |"),
            "run npm run sync:lucide after changing the Lucide dependency",
        )

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

    def test_cmake_module_invokes_the_canonical_cli(self) -> None:
        module = (
            PROJECT_ROOT / "src" / "dockle" / "cmake" / "Dockle.cmake"
        ).read_text(encoding="utf-8")
        example = (
            PROJECT_ROOT / "examples" / "doxygen" / "CMakeLists.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("function(dockle_add_docs target)", module)
        self.assertIn("find_program(dockle_program", module)
        self.assertIn("-m dockle", module)
        self.assertIn("include(Dockle)", example)
        self.assertIn("TARGETS doxygen", example)

    def test_python_packaging_uses_locked_uv_dependencies(self) -> None:
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as stream:
            project = tomllib.load(stream)

        self.assertEqual(project["project"]["version"], "0.0.0")
        self.assertIn("test", project["dependency-groups"])
        self.assertIn("package", project["dependency-groups"])
        self.assertTrue((PROJECT_ROOT / "uv.lock").is_file())

    def test_ci_uses_release_version_and_uploads_codecov_reports(self) -> None:
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("actions/release_setup@", workflow)
        self.assertIn("uv version", workflow)
        self.assertIn("uv sync --locked", workflow)
        self.assertIn("report_type: coverage", workflow)
        self.assertIn("report_type: test_results", workflow)
        self.assertIn("github.event_name == 'push'", workflow)
        self.assertIn("publish_release == 'true'", workflow)
        self.assertIn("virustotal_api_key:", workflow)
        self.assertNotIn("gh-action-pypi-publish@", workflow)

    def test_pypi_publish_requires_a_stable_release_event(self) -> None:
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "ci-release.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("release:", workflow)
        self.assertIn("- released", workflow)
        self.assertIn("github.event.action == 'released'", workflow)
        self.assertIn("github.event.release.draft == false", workflow)
        self.assertIn("github.event.release.prerelease == false", workflow)
        self.assertIn("gh release download", workflow)
        self.assertIn("gh-action-pypi-publish@", workflow)

    def test_ci_builds_all_requested_standalone_executables(self) -> None:
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        ).read_text(encoding="utf-8")

        for runner in (
            "windows-latest",
            "windows-11-arm",
            "ubuntu-latest",
            "ubuntu-24.04-arm",
            "macos-latest",
            "macos-26-intel",
        ):
            self.assertIn(f"os: {runner}", workflow)
        self.assertIn("dockle-windows-amd64.exe", workflow)
        self.assertIn("dockle-windows-arm64.exe", workflow)
        self.assertNotIn("SHA256SUMS", workflow)
        self.assertIn("--onefile", workflow)
        self.assertIn("--copy-metadata dockle", workflow)


if __name__ == "__main__":
    unittest.main()
