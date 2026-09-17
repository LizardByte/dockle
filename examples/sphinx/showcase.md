# Markdown component reference

Each component shows the Markdown source followed by the rendered result. The
same reference is available in every example so framework output can be
compared directly.

## Admonitions

Dockle supports the five GitHub alert types and six additional documentation
types with the same blockquote syntax.

### Source

```markdown
> [!NOTE]
> Useful context that supplements the surrounding content.

> [!TIP]
> A practical suggestion that can improve the result.

> [!IMPORTANT]
> Information the reader must understand before continuing.

> [!WARNING]
> A condition that may cause an unexpected result.

> [!CAUTION]
> An action that may have harmful consequences.

> [!ATTENTION]
> Something that requires immediate consideration.

> [!DANGER]
> A condition likely to cause serious failure.

> [!ERROR]
> A failure state that must be corrected.

> [!HINT]
> A small clue that helps the reader make progress.

> [!SEEALSO]
> A closely related page or API.

> [!TODO]
> Work that remains to be completed.
```

### Result

> [!NOTE]
> Useful context that supplements the surrounding content.

> [!TIP]
> A practical suggestion that can improve the result.

> [!IMPORTANT]
> Information the reader must understand before continuing.

> [!WARNING]
> A condition that may cause an unexpected result.

> [!CAUTION]
> An action that may have harmful consequences.

> [!ATTENTION]
> Something that requires immediate consideration.

> [!DANGER]
> A condition likely to cause serious failure.

> [!ERROR]
> A failure state that must be corrected.

> [!HINT]
> A small clue that helps the reader make progress.

> [!SEEALSO]
> A closely related page or API.

> [!TODO]
> Work that remains to be completed.

## Code blocks

### Source

````markdown
```python
targets = ["sphinx", "doxygen", "mkdocs", "jsdoc", "rustdoc"]
enabled = [target for target in targets if target != "disabled"]
```
````

### Result

```python
targets = ["sphinx", "doxygen", "mkdocs", "jsdoc", "rustdoc"]
enabled = [target for target in targets if target != "disabled"]
```

Inline code such as `dockle build` uses the shared code font and background.

## Tables

### Source

```markdown
| Phase | Dockle responsibility |
| --- | --- |
| Configure | Generate native configuration |
| Build | Invoke the selected tool |
| Theme | Apply shared presentation |
```

### Result

| Phase | Dockle responsibility |
| --- | --- |
| Configure | Generate native configuration |
| Build | Invoke the selected tool |
| Theme | Apply shared presentation |

## Tabs

Portable tabs use semantic `details` elements and remain readable when
JavaScript is disabled. Dockle upgrades them into an accessible tab set.

### Source

```html
<div class="dockle-tabs">
  <details open>
    <summary>Configure</summary>
    <p>Dockle writes the native configuration.</p>
  </details>
  <details>
    <summary>Build</summary>
    <p>The upstream generator builds semantic HTML.</p>
  </details>
</div>
```

### Result

<div class="dockle-tabs">
  <details open>
    <summary>Configure</summary>
    <p>Dockle writes the native configuration.</p>
  </details>
  <details>
    <summary>Build</summary>
    <p>The upstream generator builds semantic HTML.</p>
  </details>
</div>

## Quotation

### Source

```markdown
> One project model should produce one recognizable documentation experience.
```

### Result

> One project model should produce one recognizable documentation experience.

## Sphinx-native admonition

MyST directives remain available when a custom title is useful.

### Source

````markdown
```{admonition} Adapter detail
:class: important
Dockle generates `conf.py`; the consumer does not maintain it.
```
````

### Result

```{admonition} Adapter detail
:class: important
Dockle generates `conf.py`; the consumer does not maintain it.
```
