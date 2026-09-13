# rustdoc example

This fixture demonstrates the rustdoc adapter with Rust API documentation.
Dockle runs Cargo with an isolated target directory and normalizes the generated
HTML with the shared presentation layer.

> [!NOTE]
> This source tree contains no consumer-maintained rustdoc configuration.

## What to compare

| Page | Purpose |
| --- | --- |
| [Component showcase](showcase/index.html) | Typography, code, tables, and alerts |
| [API reference](struct.DocumentationTarget.html) | Framework-native Rust API output |

## Quick start

```rust
use dockle_preview::{DocumentationTarget, WarningPolicy};

let target = DocumentationTarget::new(
    "api",
    "rustdoc",
    WarningPolicy::Fail,
);
assert_eq!(target.framework(), "rustdoc");
```

Every example uses the same concepts and page structure so visual differences
come from the generator integration rather than unrelated prose.
