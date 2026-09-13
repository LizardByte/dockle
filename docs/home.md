# One configuration, one documentation experience

Dockle builds several documentation systems and gives every result the same
navigation, search, typography, colors, responsive layout, and project
branding. Consumers describe the project once in `dockle.toml`; Dockle writes
the temporary native configuration and invokes each upstream generator.

> [!IMPORTANT]
> Dockle is pre-alpha. The configuration model and adapters are ready for
> experimentation, but the public contract is still evolving.

## Quick start

Install Dockle with the adapters used by the project:

```console
python -m pip install -e ".[all]"
npm ci --ignore-scripts
python -m dockle check
python -m dockle build
```

The root output page contains the project documentation and cards for every
configured target. Each target also links back here.

## A framework-neutral configuration

```toml
[project]
name = "Example"
version = "1.0.0"
home = "docs/index.md"
logo = "branding/logo.png"

[theme]
primary = "#2962ff"

[[targets]]
name = "python"
framework = "sphinx"
source = "docs/python"

[[targets]]
name = "cpp"
framework = "doxygen"
source = "src"
```

Dockle resolves paths relative to the configuration file, keeps generated
native files in its work directory, and writes each target below one output
root. Strict mode maps to each generator's warning-as-error behavior.

## Current adapters

| Framework | Dockle supplies | Example language |
| --- | --- | --- |
| Sphinx | `conf.py` and a first-party theme | Python |
| Doxygen | `Doxyfile` and compatibility styling | C++ |
| MkDocs | `mkdocs.yml` and a first-party theme | TOML/configuration |
| JSDoc | `jsdoc.json` and compatibility styling | JavaScript |
| rustdoc | Cargo invocation and compatibility styling | Rust |

All five examples above intentionally cover almost the same content. Use them
to compare headings, code blocks, tables, GitHub-style alerts, API reference,
navigation, and search without the source material skewing the result.

## Design boundary

Dockle owns orchestration and presentation. The upstream tools still parse
their own source languages and produce their native semantic HTML. This keeps
Dockle small enough to add more generators without reimplementing them.
