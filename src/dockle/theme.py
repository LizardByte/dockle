"""Generate and apply Dockle's framework-neutral theme."""

from __future__ import annotations

import os
import re
from html import escape
from pathlib import Path

from dockle.config import DockleConfig, TargetConfig, ThemeConfig

_HEAD_END = re.compile(r"</head\s*>", re.IGNORECASE)
_HTML_START = re.compile(r"<html(?P<attributes>\s[^>]*)?>", re.IGNORECASE)
_BODY_START = re.compile(r"<body(?P<attributes>\s[^>]*)?>", re.IGNORECASE)
_JSDOC_HOME_TITLE = re.compile(
    r'<h1\s+class=["\']page-title["\']>\s*Home\s*</h1>',
    re.IGNORECASE,
)


class ThemeError(RuntimeError):
    """Raised when generated HTML cannot be themed safely."""


def render_theme(theme: ThemeConfig) -> str:
    """Combine the base stylesheet with configured design tokens."""

    base = (
        Path(__file__)
        .with_name("sphinx")
        .joinpath("themes", "dockle", "static", "dockle.css")
        .read_text(encoding="utf-8")
    )
    tokens = f"""/* Generated from dockle.toml. */
:root {{
  --dockle-primary: {theme.primary};
  --dockle-content: {theme.content};
  --dockle-background: {theme.light_background};
  --dockle-font: {theme.font};
  --dockle-code-font: {theme.code_font};
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --dockle-background: {theme.dark_background};
  }}
}}
"""
    return f"{tokens}\n{base}"


def apply_theme(
    output: Path,
    framework: str,
    stylesheet: str,
    *,
    portal: Path | None = None,
    project_name: str = "",
    project_version: str = "",
) -> int:
    """Inject the shared stylesheet into generated HTML.

    Sphinx and Doxygen receive the stylesheet through their native generated
    configuration. Other adapters are normalized after generation because
    their stable CSS hooks do not share the same path semantics.
    """

    html_files = sorted(output.rglob("*.html"))
    if not html_files:
        raise ThemeError(f"{framework} did not generate any HTML files in {output}")

    native_theme = framework in {"sphinx", "doxygen", "mkdocs"}
    asset_dir = output / "_dockle"
    if not native_theme:
        asset_dir.mkdir(parents=True, exist_ok=True)
        (asset_dir / "dockle.css").write_text(stylesheet, encoding="utf-8")

    themed = 0
    for html_file in html_files:
        document = html_file.read_text(encoding="utf-8")
        changed = False
        if framework == "jsdoc" and html_file == output / "index.html":
            document, replacements = _JSDOC_HOME_TITLE.subn("", document, count=1)
            changed = replacements > 0

        if not native_theme and "data-dockle-theme" not in document:
            match = _HEAD_END.search(document)
            if match is None:
                raise ThemeError(f"generated HTML has no closing head element: {html_file}")
            relative_asset = Path(os.path.relpath(asset_dir / "dockle.css", html_file.parent)).as_posix()
            link = (
                f'<link rel="stylesheet" href="{relative_asset}" '
                f'data-dockle-theme="{framework}">\n'
            )
            document = f"{document[:match.start()]}{link}{document[match.start():]}"
            changed = True

        if "data-dockle-framework" not in document:
            html_start = _HTML_START.search(document)
            if html_start is None:
                raise ThemeError(f"generated HTML has no root html element: {html_file}")
            attributes = html_start.group("attributes") or ""
            themed_root = f'<html data-dockle-framework="{framework}"{attributes}>'
            document = f"{document[:html_start.start()]}{themed_root}{document[html_start.end():]}"
            changed = True

        if portal is not None and "data-dockle-home" not in document:
            body_start = _BODY_START.search(document)
            if body_start is None:
                raise ThemeError(f"generated HTML has no body element: {html_file}")
            relative_portal = Path(os.path.relpath(portal / "index.html", html_file.parent)).as_posix()
            home = f'<a class="dockle-home" href="{relative_portal}" data-dockle-home>All docs</a>'
            document = f"{document[:body_start.end()]}{home}{document[body_start.end():]}"
            changed = True

        if (
            portal is not None
            and project_name
            and framework in {"doxygen", "jsdoc", "rustdoc"}
            and "data-dockle-brand" not in document
        ):
            body_start = _BODY_START.search(document)
            if body_start is None:
                raise ThemeError(f"generated HTML has no body element: {html_file}")
            relative_portal = Path(os.path.relpath(portal / "index.html", html_file.parent)).as_posix()
            version = f"<span>{escape(project_version)}</span>" if project_version else ""
            brand = (
                f'<a class="dockle-compat-brand" href="{relative_portal}" data-dockle-brand>'
                f"<strong>{escape(project_name)}</strong>{version}</a>"
            )
            document = f"{document[:body_start.end()]}{brand}{document[body_start.end():]}"
            changed = True

        if changed:
            html_file.write_text(document, encoding="utf-8")
            themed += 1
    return themed


def write_portal(config: DockleConfig, targets: tuple[TargetConfig, ...], stylesheet: str) -> Path:
    """Write the root page that ties independently generated targets together."""

    output = config.build.output
    output.mkdir(parents=True, exist_ok=True)
    asset_dir = output / "_dockle"
    asset_dir.mkdir(parents=True, exist_ok=True)
    (asset_dir / "dockle.css").write_text(stylesheet, encoding="utf-8")

    cards: list[str] = []
    for target in targets:
        relative = target.output.relative_to(output).as_posix()
        description = target.description or f"Documentation generated with {target.framework}."
        cards.append(
            f"""      <a class="dockle-portal-card" href="{escape(relative)}/">
        <span class="dockle-portal-framework">{escape(target.framework)}</span>
        <strong>{escape(target.title)}</strong>
        <span>{escape(description)}</span>
      </a>"""
        )

    version = f" <span>{escape(config.project.version)}</span>" if config.project.version else ""
    repository = ""
    if config.project.repository:
        repository = (
            f'    <p><a href="{escape(config.project.repository)}">Source repository</a></p>\n'
        )
    document = f"""<!doctype html>
<html lang="en" data-dockle-framework="portal">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(config.project.description)}">
  <title>{escape(config.project.name)} documentation</title>
  <link rel="stylesheet" href="_dockle/dockle.css" data-dockle-theme="portal">
</head>
<body class="dockle-portal">
  <main>
    <header>
      <p class="dockle-portal-kicker">Documentation</p>
      <h1>{escape(config.project.name)}{version}</h1>
      <p>{escape(config.project.description)}</p>
    </header>
    <section class="dockle-portal-grid" aria-label="Documentation sets">
{chr(10).join(cards)}
    </section>
{repository}  </main>
</body>
</html>
"""
    portal = output / "index.html"
    portal.write_text(document, encoding="utf-8")
    return portal
