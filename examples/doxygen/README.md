# Doxygen example

This fixture demonstrates the Doxygen adapter with C++ API documentation.
Dockle generates the complete `Doxyfile`, enables strict warnings, and attaches
the shared presentation layer through supported Doxygen hooks.

> [!NOTE]
> This source tree contains no consumer-maintained Doxygen configuration.

## What to compare

| Page | Purpose |
| --- | --- |
| [Component showcase](showcase.md) | Typography, code, tables, and alerts |
| [API reference](annotated.html) | Framework-native C++ API output |

## Quick start

```cpp
#include "include/dockle_demo.hpp"

using dockle::demo::target;
using dockle::demo::warning_policy;

constexpr target docs{"api", "doxygen", warning_policy::fail};
static_assert(docs.generator() == "doxygen");
```

Every example uses the same concepts and page structure so visual differences
come from the generator integration rather than unrelated prose.
