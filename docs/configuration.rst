Configuration reference
=======================

Dockle reads one TOML file, ``dockle.toml``, from the current directory by default. Use
``dockle --config path/to/dockle.toml`` to select another file. Relative paths are resolved from the directory that
contains the selected configuration file.

Complete example
----------------

.. code-block:: toml

   [project]
   name = "Example"
   version = "1.2.0"
   description = "Example project documentation"
   repository = "https://github.com/example/example"
   author = "Example maintainers"
   copyright = "2026, Example maintainers"
   logo = "branding/logo.png"
   favicon = "branding/favicon.svg"

   [theme]
   primary = "#2962ff"
   content = "#2e3440"
   light_background = "#ffffff"
   dark_background = "#131416"

   [build]
   output = "_site"
   work = ".dockle"
   strict = true
   clean = true

   [tools]
   doxygen = "/opt/doxygen/bin/doxygen"

   [[targets]]
   name = "docs"
   title = "Project documentation"
   framework = "sphinx"
   source = "docs"
   home = true

   [[targets]]
   name = "guide"
   title = "User guide"
   description = "Tutorials and configuration reference."
   framework = "sphinx"
   source = "docs"
   entry = "index"

Project metadata
----------------

``project.name`` is required. The optional ``version``, ``description``, ``repository``, ``author``, and ``copyright``
values are translated into native metadata where a generator supports them. The optional ``logo`` and ``favicon``
paths must name files within the project. Dockle copies the favicon into every generated backend and the portal. The
portal always uses the name, description, version, and repository.

Theme tokens
------------

All theme settings are optional. ``primary``, ``content``, ``light_background``, and ``dark_background`` accept CSS
color values. ``font`` and ``code_font`` accept CSS font-family stacks. Unsafe delimiters are rejected because these
values are written into a generated stylesheet.

Build behavior
--------------

``build.output``
   Root of the publishable site. Defaults to ``_site``.

``build.work``
   Disposable native configurations and intermediate files. Defaults to ``.dockle``.

``build.strict``
   Enables warning-as-error behavior in each adapter. Defaults to ``true``.

``build.clean``
   Replaces generated output instead of merging into it. A full build owns and cleans the whole output tree; a build
   naming one or more targets only cleans those target directories. Defaults to ``true``.

Both output paths must stay within the project and must not contain one another.

Targets
-------

At least one ``[[targets]]`` table is required. ``name``, ``framework``, and ``source`` are required. Names use
lowercase letters, numbers, hyphens, and underscores and become output directory names by default. ``title`` and
``description`` label the target on the generated portal. ``output`` can select another directory below
``build.output``.

One Sphinx target may set ``home = true``. Dockle publishes that target at ``build.output`` and injects the comparison
cards after its first heading. To control their exact location, add ``<div data-dockle-target-cards></div>`` in a raw
HTML block. A home target cannot set ``output``; all other targets remain in their own directories below it.

The supported framework names and ``entry`` behavior are:

==========  =======================  =============================================================
Framework   Native requirement       ``entry``
==========  =======================  =============================================================
Sphinx      Python ``sphinx``         Root document without its extension; defaults to ``index``.
Doxygen     ``doxygen`` executable    Existing Markdown main page; otherwise normal Doxygen behavior.
MkDocs      Python ``mkdocs``         Reserved; MkDocs discovers ``index.md`` normally.
JSDoc       ``jsdoc`` executable      Existing README or Markdown landing page.
rustdoc     Cargo and Rust            Reserved; ``source`` names a crate directory or ``Cargo.toml``.
==========  =======================  =============================================================

Each non-home output directory must be unique and must remain below ``build.output``. Entry paths cannot be absolute
or escape the source directory.

Tool resolution
---------------

Dockle normally finds native executables on ``PATH``. Python console scripts are also resolved beside the running
Python interpreter, and Node.js tools are resolved from ``node_modules/.bin`` in the project. A ``[tools]`` entry can
override any adapter with a command name or a path relative to ``dockle.toml``:

.. code-block:: toml

   [tools]
   sphinx = ".venv/bin/sphinx-build"
   doxygen = "vendor/doxygen/bin/doxygen"
   mkdocs = ".venv/bin/mkdocs"
   jsdoc = "node_modules/.bin/jsdoc"
   rustdoc = "cargo"

Generated native files
----------------------

Dockle writes generated native configuration under ``build.work/<target>/`` and replaces it on every build. These
files are deliberately not a public configuration surface and should not be edited or committed. Use
``dockle build --dry-run`` to inspect commands without generating files, and ``dockle check`` to validate sources and
tool availability before building.
