# JSDoc example

This fixture demonstrates the JSDoc adapter with JavaScript API documentation.
Dockle generates `jsdoc.json`, points it at the source and tutorials, and
normalizes the generated HTML with the shared presentation layer.

> [!NOTE]
> This source tree contains no consumer-maintained JSDoc configuration.

## What to compare

| Page | Purpose |
| --- | --- |
| [Component showcase](tutorial-showcase.html) | Typography, code, tables, and alerts |
| [API reference](module-dockle-demo.html) | Framework-native JavaScript API output |

## Quick start

```javascript
import { DocumentationTarget, WarningPolicy } from "./dockle-demo.js";

const target = new DocumentationTarget(
  "api",
  "jsdoc",
  WarningPolicy.Fail,
);
console.assert(target.framework === "jsdoc");
```

Every example uses the same concepts and page structure so visual differences
come from the generator integration rather than unrelated prose.
