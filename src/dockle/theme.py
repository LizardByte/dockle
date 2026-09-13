"""Generate and apply Dockle's framework-neutral theme."""

from __future__ import annotations

import json
import os
import re
import shutil
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from dockle.config import DockleConfig, TargetConfig, ThemeConfig
from dockle.markdown import render_markdown

_HEAD_END = re.compile(r"</head\s*>", re.IGNORECASE)
_HTML_START = re.compile(r"<html(?P<attributes>\s[^>]*)?>", re.IGNORECASE)
_BODY_START = re.compile(r"<body(?P<attributes>\s[^>]*)?>", re.IGNORECASE)
_JSDOC_HOME_TITLE = re.compile(
    r'<h1\s+class=["\']page-title["\']>\s*Home\s*</h1>',
    re.IGNORECASE,
)


class ThemeError(RuntimeError):
    """Raised when generated HTML cannot be themed safely."""


class _SearchDocumentParser(HTMLParser):
    """Collect useful searchable text from one generated HTML page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: list[str] = []
        self.text: list[str] = []
        self._in_title = False
        self._ignored = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del attrs
        if tag in {"script", "style", "svg"}:
            self._ignored += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "svg"} and self._ignored:
            self._ignored -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored:
            return
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        self.text.append(cleaned)
        if self._in_title:
            self.title.append(cleaned)


def _theme_asset(name: str) -> Path:
    return (
        Path(__file__)
        .with_name("sphinx")
        .joinpath("themes", "dockle", "static", name)
    )


def render_theme(theme: ThemeConfig) -> str:
    """Combine the base stylesheet with configured design tokens."""

    base = _theme_asset("dockle.css").read_text(encoding="utf-8")
    tokens = f"""/* Generated from dockle.toml. */
:root,
:root[data-color-scheme="light"] {{
  --dockle-primary: {theme.primary};
  --dockle-content: {theme.content};
  --dockle-background: {theme.light_background};
  --dockle-font: {theme.font};
  --dockle-code-font: {theme.code_font};
}}

:root[data-color-scheme="dark"] {{
  --dockle-content: #e5e7eb;
  --dockle-background: {theme.dark_background};
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-color-scheme]) {{
    --dockle-content: #e5e7eb;
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
    logo: Path | None = None,
) -> int:
    """Inject shared assets, navigation, branding, and client search."""

    html_files = sorted(output.rglob("*.html"))
    if not html_files:
        raise ThemeError(
            f"{framework} did not generate any HTML files in {output}"
        )

    asset_dir = output / "_dockle"
    asset_dir.mkdir(parents=True, exist_ok=True)
    (asset_dir / "dockle.css").write_text(stylesheet, encoding="utf-8")
    shutil.copyfile(_theme_asset("dockle.js"), asset_dir / "dockle.js")
    logo_asset = _copy_logo(logo, asset_dir)
    search_documents = _build_search_documents(html_files, output)
    (asset_dir / "search.json").write_text(
        json.dumps({"docs": search_documents}, ensure_ascii=False),
        encoding="utf-8",
    )

    native_theme = framework in {"sphinx", "doxygen", "mkdocs"}
    themed = 0
    for html_file in html_files:
        document = html_file.read_text(encoding="utf-8")
        changed = False
        if framework == "jsdoc" and html_file == output / "index.html":
            document, replacements = _JSDOC_HOME_TITLE.subn(
                "",
                document,
                count=1,
            )
            changed = replacements > 0

        if not native_theme and "data-dockle-theme" not in document:
            relative_css = _relative(asset_dir / "dockle.css", html_file)
            link = (
                f'<link rel="stylesheet" href="{relative_css}" '
                f'data-dockle-theme="{framework}">\n'
            )
            document = _insert_before_head_end(document, link, html_file)
            changed = True

        if "dockle.js" not in document:
            relative_script = _relative(asset_dir / "dockle.js", html_file)
            script = (
                f'<script defer src="{relative_script}" '
                "data-dockle-script></script>\n"
            )
            document = _insert_before_head_end(document, script, html_file)
            changed = True

        if "data-dockle-framework" not in document:
            html_start = _HTML_START.search(document)
            if html_start is None:
                raise ThemeError(
                    f"generated HTML has no root html element: {html_file}"
                )
            attributes = html_start.group("attributes") or ""
            themed_root = (
                f'<html data-dockle-framework="{framework}"{attributes}>'
            )
            document = (
                f"{document[:html_start.start()]}{themed_root}"
                f"{document[html_start.end():]}"
            )
            changed = True

        decorations = _page_decorations(
            html_file=html_file,
            output=output,
            portal=portal,
            framework=framework,
            project_name=project_name,
            project_version=project_version,
            logo_asset=logo_asset,
            include_theme_toggle=(
                "data-dockle-theme-toggle" not in document
            ),
        )
        if "data-dockle-universal-search" not in document:
            document = _insert_after_body(document, decorations, html_file)
            changed = True

        if changed:
            html_file.write_text(document, encoding="utf-8")
            themed += 1
    return themed


def _insert_before_head_end(
    document: str,
    markup: str,
    html_file: Path,
) -> str:
    match = _HEAD_END.search(document)
    if match is None:
        raise ThemeError(
            f"generated HTML has no closing head element: {html_file}"
        )
    return f"{document[:match.start()]}{markup}{document[match.start():]}"


def _insert_after_body(
    document: str,
    markup: str,
    html_file: Path,
) -> str:
    match = _BODY_START.search(document)
    if match is None:
        raise ThemeError(f"generated HTML has no body element: {html_file}")
    return f"{document[:match.end()]}{markup}{document[match.end():]}"


def _relative(asset: Path, html_file: Path) -> str:
    return Path(os.path.relpath(asset, html_file.parent)).as_posix()


def _copy_logo(logo: Path | None, asset_dir: Path) -> Path | None:
    if logo is None:
        return None
    destination = asset_dir / f"logo{logo.suffix.lower()}"
    shutil.copyfile(logo, destination)
    return destination


def _build_search_documents(
    html_files: list[Path],
    output: Path,
) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for html_file in html_files:
        parser = _SearchDocumentParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        text = " ".join(parser.text)
        title = " ".join(parser.title)
        if not title:
            title = html_file.stem.replace("-", " ").title()
        documents.append(
            {
                "location": html_file.relative_to(output).as_posix(),
                "title": title,
                "text": text[:4000],
            }
        )
    return documents


def _page_decorations(
    *,
    html_file: Path,
    output: Path,
    portal: Path | None,
    framework: str,
    project_name: str,
    project_version: str,
    logo_asset: Path | None,
    include_theme_toggle: bool,
) -> str:
    relative_index = _relative(
        output / "_dockle" / "search.json",
        html_file,
    )
    relative_root = _relative(output, html_file)
    logo_url = _relative(logo_asset, html_file) if logo_asset else ""
    search = f"""
<div class="dockle-search dockle-universal-search"
     data-dockle-universal-search data-dockle-logo-url="{logo_url}">
  <label class="visually-hidden" for="dockle-search-input">
    Search documentation
  </label>
  <input id="dockle-search-input" type="search"
         placeholder="Search documentation" autocomplete="off"
         data-dockle-search="{relative_index}"
         data-dockle-root="{relative_root}">
  <ul class="dockle-search-results"
      data-dockle-search-results="dockle-search-input"
      aria-live="polite" hidden></ul>
</div>"""
    links = ""
    if portal is not None:
        relative_portal = _relative(portal / "index.html", html_file)
        links += (
            f'<a class="dockle-home" href="{relative_portal}" '
            "data-dockle-home>All docs</a>"
        )
    if (
        portal is not None
        and project_name
        and framework in {"doxygen", "jsdoc", "rustdoc"}
    ):
        relative_portal = _relative(portal / "index.html", html_file)
        version = (
            f"<span>{escape(project_version)}</span>"
            if project_version
            else ""
        )
        links += (
            f'<a class="dockle-compat-brand" href="{relative_portal}" '
            f"data-dockle-brand><strong>{escape(project_name)}</strong>"
            f"{version}</a>"
        )
    toggle = ""
    if include_theme_toggle:
        toggle = (
            '<button type="button" class="dockle-theme-toggle" '
            'data-dockle-theme-toggle aria-label="Toggle color scheme">'
            '<span aria-hidden="true">◐</span></button>'
        )
    return f"{links}{search}{toggle}"


def write_portal(
    config: DockleConfig,
    targets: tuple[TargetConfig, ...],
    stylesheet: str,
) -> Path:
    """Write the root project documentation and comparison cards."""

    output = config.build.output
    output.mkdir(parents=True, exist_ok=True)
    asset_dir = output / "_dockle"
    asset_dir.mkdir(parents=True, exist_ok=True)
    (asset_dir / "dockle.css").write_text(stylesheet, encoding="utf-8")
    shutil.copyfile(_theme_asset("dockle.js"), asset_dir / "dockle.js")
    logo_asset = _copy_logo(config.project.logo, asset_dir)

    cards: list[str] = []
    for target in targets:
        relative = target.output.relative_to(output).as_posix()
        description = target.description or (
            f"Documentation generated with {target.framework}."
        )
        cards.append(
            f"""      <a class="dockle-portal-card" href="{escape(relative)}/">
        <span class="dockle-portal-framework">{escape(target.framework)}</span>
        <strong>{escape(target.title)}</strong>
        <span>{escape(description)}</span>
      </a>"""
        )

    version = (
        f" <span>{escape(config.project.version)}</span>"
        if config.project.version
        else ""
    )
    repository = ""
    if config.project.repository:
        repository = (
            '    <p class="dockle-portal-repository">'
            f'<a href="{escape(config.project.repository)}">'
            "Source repository</a></p>\n"
        )
    logo = ""
    if logo_asset is not None:
        logo = (
            f'      <img class="dockle-portal-logo" '
            f'src="_dockle/{escape(logo_asset.name)}" alt="">\n'
        )
    project_docs = ""
    if config.project.home is not None:
        source = config.project.home.read_text(encoding="utf-8")
        project_docs = (
            '    <article class="dockle-portal-docs">\n'
            f"{render_markdown(source)}\n"
            "    </article>\n"
        )

    document = f"""<!doctype html>
<html lang="en" data-dockle-framework="portal">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(config.project.description)}">
  <title>{escape(config.project.name)} documentation</title>
  <link rel="stylesheet" href="_dockle/dockle.css" data-dockle-theme="portal">
  <script defer src="_dockle/dockle.js" data-dockle-script></script>
</head>
<body class="dockle-portal">
  <main>
    <header>
{logo}      <div>
        <p class="dockle-portal-kicker">Documentation</p>
        <h1>{escape(config.project.name)}{version}</h1>
        <p>{escape(config.project.description)}</p>
      </div>
    </header>
    <section class="dockle-portal-grid" aria-label="Documentation examples">
{chr(10).join(cards)}
    </section>
{project_docs}{repository}  </main>
  <button type="button" class="dockle-theme-toggle"
          data-dockle-theme-toggle aria-label="Toggle color scheme">
    <span aria-hidden="true">◐</span>
  </button>
</body>
</html>
"""
    portal = output / "index.html"
    portal.write_text(document, encoding="utf-8")
    return portal
