# Configuration notes

Dockle resolves every source, work, and output path against the directory containing `dockle.toml`. Generated output
cannot escape that project directory.

## Strict builds

Strict mode maps to the warning-as-error behavior offered by each generator. A missing executable or source directory
is reported before the build begins when you run:

```console
dockle check
```

The generated site uses relative theme asset paths, including from nested pages like this one, so it remains usable
under versioned Read the Docs URLs.
