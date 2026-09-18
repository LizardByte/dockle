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
            PROJECT_ROOT / "branding" / "dockle-logo.svg",
        )
        self.assertEqual(
            config.project.favicon,
            PROJECT_ROOT / "branding" / "dockle-logo.svg",
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
        self.assertEqual(package["name"], "@lizardbyte/dockle")
        self.assertEqual(package["version"], "0.0.0")
        self.assertEqual(package["author"], "LizardByte")
        self.assertEqual(package["license"], "MIT")
        self.assertNotIn("private", package)
        self.assertEqual(
            package["bin"]["dockle-jsdoc"], "bin/dockle-jsdoc.cjs"
        )
        self.assertEqual(package["dependencies"]["jsdoc"], "4.0.5")
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

    def test_examples_document_portable_doxygen_authoring(self) -> None:
        showcase = (
            PROJECT_ROOT / "examples" / "doxygen" / "showcase.md"
        ).read_text(encoding="utf-8")

        self.assertIn("```python", showcase)
        self.assertIn("```javascript", showcase)
        self.assertIn(
            "@admonition{Custom title |:| "
            "A neutral custom admonition can contain A | B.}",
            showcase,
        )

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

        self.assertEqual(project["project"]["name"], "lizardbyte-dockle")
        self.assertEqual(project["project"]["version"], "0.0.0")
        self.assertEqual(
            project["project"]["authors"], [{"name": "LizardByte"}]
        )
        self.assertEqual(project["project"]["license"], "MIT")
        self.assertNotIn(
            "Development Status :: 2 - Pre-Alpha",
            project["project"]["classifiers"],
        )
        self.assertIn("test", project["dependency-groups"])
        self.assertIn("package", project["dependency-groups"])
        self.assertEqual(
            project["tool"]["hatch"]["build"]["targets"]["sdist"]["include"],
            ["/LICENSE", "/README.md", "/pyproject.toml", "/src"],
        )
        self.assertTrue((PROJECT_ROOT / "uv.lock").is_file())

    def test_ci_uses_release_version_and_uploads_codecov_reports(self) -> None:
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("actions/release_setup@", workflow)
        self.assertIn("uv version", workflow)
        self.assertIn("uv sync --locked", workflow)
        self.assertIn("python-version:\n          - '3.11'", workflow)
        self.assertIn("Smoke test installed wheel", workflow)
        self.assertIn("name: Node package", workflow)
        self.assertIn('NODE_VERSION: \'24\'', workflow)
        self.assertIn("npm publish --dry-run", workflow)
        self.assertIn("./coverage/lcov.info", workflow)
        self.assertIn("./junit-node.xml", workflow)
        self.assertIn("report_type: coverage", workflow)
        self.assertIn("report_type: test_results", workflow)
        self.assertIn(
            "if: needs.release-setup.outputs.publish_release == 'true'",
            workflow,
        )
        self.assertIn("publish_release == 'true'", workflow)
        self.assertIn("virustotal_api_key:", workflow)
        self.assertIn("watchdog must build", workflow)
        self.assertEqual(
            workflow.count("NOSONAR(githubactions:S8541)"), 3
        )
        self.assertEqual(
            workflow.count("NOSONAR(githubactions:S8544)"), 2
        )
        self.assertEqual(
            workflow.count("--no-deps prevents unlocked dependency"), 2
        )
        self.assertIn("--no-sync prevents installs", workflow)
        self.assertIn("standalone matrix portable", workflow)
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
        self.assertIn("https://pypi.org/p/lizardbyte-dockle", workflow)
        self.assertIn('"lizardbyte_dockle-*.whl"', workflow)
        self.assertIn('"lizardbyte_dockle-*.tar.gz"', workflow)
        self.assertIn("gh-action-pypi-publish@", workflow)

    def test_npm_publish_requires_a_release_event(self) -> None:
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "_update-npm.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("release:", workflow)
        self.assertIn("- released", workflow)
        self.assertIn("__call-update-npm.yml@master", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("release_version:", workflow)

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
        self.assertIn("executable: dockle.exe", workflow)
        self.assertIn("executable: dockle", workflow)
        self.assertIn("--name dockle", workflow)
        self.assertIn("azure/trusted-signing-action@", workflow)
        self.assertIn("apple-actions/import-codesign-certs@", workflow)
        self.assertIn("--codesign-identity", workflow)
        self.assertIn("--collect-all sphinx", workflow)
        self.assertIn("--collect-all dockle", workflow)
        self.assertIn("Smoke test bundled Python adapters", workflow)
        self.assertIn("xcrun notarytool submit", workflow)
        self.assertEqual(
            workflow.count("- name: Build standalone executable\n"), 1
        )
        self.assertNotIn(
            "Build and sign macOS standalone executable", workflow
        )
        self.assertIn(
            "APPLE_CODESIGN_IDENTITY: ${{ secrets.APPLE_CODESIGN_IDENTITY }}",
            workflow,
        )
        self.assertIn(
            'if [[ "${RUNNER_OS}" == "macOS" && \\',
            workflow,
        )
        self.assertGreaterEqual(
            workflow.count(
                "if: needs.release-setup.outputs.publish_release == 'true'"
            ),
            2,
        )
        self.assertNotIn("- name: Smoke test Windows executable", workflow)
        self.assertIn(
            "- name: Smoke test standalone executable on Windows", workflow
        )
        self.assertIn("runs-on: windows-latest", workflow)
        self.assertGreaterEqual(workflow.count("archive: false"), 2)
        self.assertIn("dockle-${{ matrix.artifact }}.tar.gz", workflow)
        self.assertIn("dockle-${{ matrix.artifact }}.zip", workflow)
        self.assertNotIn("SHA256SUMS", workflow)
        self.assertIn("--onefile", workflow)
        self.assertIn("--copy-metadata lizardbyte-dockle", workflow)


if __name__ == "__main__":
    unittest.main()
