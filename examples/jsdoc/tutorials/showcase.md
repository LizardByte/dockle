# Component showcase

This page exercises common documentation components with the same content used
by the Sphinx, Doxygen, MkDocs, and rustdoc examples.

## GitHub-style alerts

> [!NOTE]
> Dockle recognizes GitHub alert syntax in Markdown sources.

> [!TIP]
> Keep shared concepts in prose and let each API tool document its language.

> [!IMPORTANT]
> Strict builds turn generator warnings into build failures.

> [!WARNING]
> Generated native configuration belongs in Dockle's work directory.

> [!CAUTION]
> Do not publish the work directory as documentation output.

## Code block

```javascript
const targets = ["sphinx", "doxygen", "mkdocs", "jsdoc", "rustdoc"];
const enabled = targets.filter((target) => target !== "disabled");
```

Inline code such as `dockle build` uses the shared code font and background.

## Table

| Phase | Dockle responsibility |
| --- | --- |
| Configure | Generate native configuration |
| Build | Invoke the selected tool in strict mode |
| Theme | Apply shared assets and structural normalization |
| Publish | Connect the target to the root project docs |

## Quotation

> One project model should produce one recognizable documentation experience.
