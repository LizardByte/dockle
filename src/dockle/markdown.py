"""Markdown helpers shared by the portal and compatible generators."""

from __future__ import annotations

import re

from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

_ALERT_START = re.compile(
    r"^>\s*\[!(ATTENTION|CAUTION|DANGER|ERROR|HINT|IMPORTANT|NOTE|SEEALSO|TIP|TODO|WARNING)\]\s*$",
    re.IGNORECASE,
)
_FENCE_START = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def normalize_github_alerts(source: str) -> str:
    """Translate GitHub alerts into Python-Markdown admonitions."""

    lines = source.splitlines()
    normalized: list[str] = []
    index = 0
    fence_character = ""
    fence_length = 0
    while index < len(lines):
        line = lines[index]
        if fence_character:
            normalized.append(line)
            closing_fence = re.match(
                rf"^ {{0,3}}{re.escape(fence_character)}{{{fence_length},}}\s*$",
                line,
            )
            if closing_fence:
                fence_character = ""
                fence_length = 0
            index += 1
            continue

        opening_fence = _FENCE_START.match(line)
        if opening_fence:
            fence_character = opening_fence.group(1)[0]
            fence_length = len(opening_fence.group(1))
            normalized.append(line)
            index += 1
            continue

        match = _ALERT_START.match(line)
        if match is None:
            normalized.append(line)
            index += 1
            continue

        normalized.append(f"!!! {match.group(1).lower()}")
        index += 1
        while index < len(lines):
            line = lines[index]
            if not line.startswith(">"):
                break
            content = line[1:]
            if content.startswith(" "):
                content = content[1:]
            normalized.append(f"    {content}" if content else "")
            index += 1
        normalized.append("")
    return "\n".join(normalized)


class GithubAlertPreprocessor(Preprocessor):
    """Normalize GitHub alert blockquotes before Markdown parsing."""

    def run(self, lines: list[str]) -> list[str]:
        """Return normalized source lines."""

        return normalize_github_alerts("\n".join(lines)).splitlines()


class GithubAlertsExtension(Extension):
    """Add GitHub alert syntax to Python-Markdown."""

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802
        """Register the alert preprocessor."""

        processor = GithubAlertPreprocessor(md)
        md.preprocessors.register(processor, "dockle_github_alerts", 35)


def makeExtension(**kwargs: object) -> GithubAlertsExtension:  # noqa: N802
    """Return the extension for Python-Markdown and MkDocs."""

    return GithubAlertsExtension(**kwargs)


def render_markdown(source: str) -> str:
    """Render project Markdown with Dockle's supported extensions."""

    renderer = Markdown(
        extensions=[
            "extra",
            "admonition",
            GithubAlertsExtension(),
        ]
    )
    return renderer.convert(source)
