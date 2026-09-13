# MkDocs example

This fixture demonstrates the MkDocs adapter with Markdown configuration
documentation. Dockle generates `mkdocs.yml`, enables common Markdown
extensions, and selects its first-party MkDocs theme.

> [!NOTE]
> This source tree contains no consumer-maintained MkDocs configuration.

## What to compare

| Page | Purpose |
| --- | --- |
| [Component showcase](showcase.md) | Typography, code, tables, and alerts |
| [API reference](api.md) | A configuration-oriented reference page |

## Quick start

```toml
[[targets]]
name = "guide"
framework = "mkdocs"
source = "docs"
```

Every example uses the same concepts and page structure so visual differences
come from the generator integration rather than unrelated prose.
