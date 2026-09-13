# MkDocs preview

This Markdown guide is built with a configuration generated entirely by Dockle. It provides a direct comparison with
the Sphinx guide and the three API-documentation generators on the same hosted site.

> **Note:** The source project does not contain a native MkDocs configuration.

## One configuration

```toml
[project]
name = "Example"

[[targets]]
name = "guide"
framework = "mkdocs"
source = "docs"
```

## Adapter behavior

| Phase | Dockle responsibility |
| --- | --- |
| Configure | Generate `mkdocs.yml` in the work directory |
| Build | Invoke MkDocs in strict mode |
| Theme | Attach the shared stylesheet with relative asset URLs |
| Publish | Add the output to the root documentation portal |

> The source project never has to maintain a native MkDocs configuration.

Continue to the [configuration notes](configuration.md).
