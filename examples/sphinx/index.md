# Sphinx example

This fixture demonstrates the Sphinx adapter with Python API documentation.
Dockle generates `conf.py`, enables MyST Markdown and autodoc, and selects its
first-party Sphinx theme.

> [!NOTE]
> This source tree contains no consumer-maintained Sphinx configuration.

## What to compare

| Page | Purpose |
| --- | --- |
| [Component showcase](showcase.md) | Typography, code, tables, and alerts |
| [API reference](api.md) | Framework-native Python API output |

## Quick start

```python
from dockle_demo import DocumentationTarget, WarningPolicy

target = DocumentationTarget("api", "sphinx", WarningPolicy.FAIL)
assert target.framework == "sphinx"
```

Every example uses the same concepts and page structure so visual differences
come from the generator integration rather than unrelated prose.

```{toctree}
:maxdepth: 2
:hidden:

showcase
api
```
