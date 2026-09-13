Architecture and roadmap
========================

Goals
-----

Dockle owns the stable, framework-neutral interface for documentation builds. It should:

* describe project metadata, build targets, and visual tokens once;
* generate disposable native configuration rather than modifying consumer files;
* invoke upstream generators normally so their source-language features remain available;
* make generated sites feel like parts of one documentation system; and
* fail clearly when a tool, source path, or configuration value is invalid.

Dockle is not a new documentation parser. Reimplementing Sphinx domains, Doxygen's language model, rustdoc's type
information, or JSDoc's tag processing would discard the strongest part of each tool.

Build pipeline
--------------

::

   dockle.toml
       |
       v
   validated neutral model
       |
       +--> Sphinx adapter  --> generated conf.py
       +--> Doxygen adapter --> generated Doxyfile
       +--> MkDocs adapter  --> generated mkdocs.yml
       +--> JSDoc adapter   --> generated jsdoc.json
       +--> rustdoc adapter --> generated Cargo invocation
       |
       v
   upstream HTML output
       |
       v
   Dockle compatibility theme --> publishable target directories
       |
       v
   root portal and cross-target links --> one hosted documentation site

Configuration boundary
----------------------

``dockle.toml`` is the public contract. Generated files under ``.dockle/<target>`` are implementation details and are
deleted before each build. The first schema deliberately exposes only concepts shared by the supported frameworks:

* project name, version, description, repository, author, and copyright;
* theme colors and font stacks;
* output/work directories and strict/clean behavior; and
* named targets with a title, description, framework, source, output, and entry document.

Framework-specific passthrough dictionaries are intentionally absent. They make an integration quick to ship but turn
the wrapper into five native configuration files hidden inside TOML. New settings should first be evaluated for a
portable meaning. An explicit, namespaced escape hatch can be added later for irreducible cases.

Theme strategy
--------------

Furo is a visual reference only: content-first pages, quiet navigation chrome, readable typography, responsive
behavior, and automatic light/dark palettes. Dockle does not depend on or inherit from Furo. It ships and registers its
own Sphinx theme, inheriting only Sphinx's intentionally minimal ``basic`` template primitives. Doxygen receives
Dockle's generated CSS through its supported extra-stylesheet setting. The other initial adapters inject the same
generated stylesheet into their HTML after the upstream build.

The compatibility stylesheet currently normalizes design tokens and common content components. Post-processing marks
each page with its framework, attaches subpath-safe relative assets where needed, and adds a common return link to the
root portal. A CSS overlay cannot make unrelated document trees structurally identical, so the next theme phase will
add maintained native templates for navigation, search, version indicators, and mobile controls. Those templates will
consume the same Dockle model and tokens rather than creating new user-facing configuration.

Milestones
----------

Milestone 0: executable foundation (implemented)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Strict TOML loader with safe, project-relative output paths.
* ``build``, ``build --dry-run``, and ``check`` commands.
* Initial adapters for Sphinx, Doxygen, MkDocs, JSDoc, and rustdoc.
* Generated Furo-inspired CSS with per-project design tokens.
* Framework-free unit tests for configuration, adapters, and HTML normalization.

Milestone 1: theme fidelity (in progress)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Representative visual fixtures for every supported generator are implemented and built together.
* The native MkDocs theme now shares Dockle's sidebar/page structure and assets with Sphinx.
* Build a native JSDoc template with the common sidebar/page structure.
* Define supported-version ranges and visual regression baselines.
* Add accessible color contrast, keyboard navigation, and mobile-layout checks.
* Decide whether rustdoc needs a maintained template or a deliberately narrower compatibility promise.

Milestone 2: multi-target documentation sites (in progress)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* A generated root landing page and cross-target return links are implemented.
* Theme and portal URLs are relative and safe under hosted, versioned subpaths.
* Build a combined search index without replacing framework-local search prematurely.
* Add ``serve`` with file watching and incremental rebuilds.

Hosted dogfood build
--------------------

The repository's Read the Docs configuration deliberately has no top-level Sphinx or MkDocs selection. A conda
environment provides pinned Doxygen and Graphviz together so strict graph generation cannot depend on the base image.
Custom commands create that environment and run Dockle inside it, then publish ``_site`` as the HTML artifact. This
exercises the public configuration path rather than maintaining a second hosting-only build graph.

Milestone 3: ecosystem and distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Define a typed third-party adapter interface.
* Add adapters based on demand, with TypeDoc and Dokka as likely candidates.
* Publish reproducible Python packages and a supported CI action.
* Add machine-readable schema documentation and configuration migration tooling before stabilizing version 1.

Known risks
-----------

Generated HTML and native template APIs change between upstream releases. Dockle should test explicit compatibility
ranges and prefer stable extension hooks over copied upstream headers. Shared styling also needs semantic fixture pages;
a successful generator exit alone does not prove navigation, search, or responsive layout.
