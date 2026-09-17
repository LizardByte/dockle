Installation and distribution
=============================

Dockle has one implementation: the Python package. Every installation route should expose the same ``dockle`` command
rather than reimplementing configuration or adapter behavior in another language.

Python projects
---------------

PyPI will be the canonical package channel. After the first release, install the core command or select the
Python-backed adapters that the project needs:

.. code-block:: console

   python -m pip install dockle
   python -m pip install "dockle[sphinx]"
   python -m pip install "dockle[mkdocs]"
   python -m pip install "dockle[all]"

``pipx install "dockle[all]"`` is a good fit for developers who want a globally available command in an isolated
environment. Doxygen, Node.js/JSDoc, Cargo, and Graphviz remain native tool dependencies when their adapters are used.

Tested compatibility
--------------------

The release workflows and hosted dogfood build exercise the following compatibility baseline. Python dependencies are
resolved by ``uv.lock``; native tools are pinned in the Read the Docs environment or selected by the hosted runner.

================  =======================  ================================================
Component         Tested versions          Compatibility promise
================  =======================  ================================================
Python            3.11 and 3.14            Supported range starts at Python 3.11.
Sphinx            9.0.4 and 9.1.0          ``sphinx>=8.1``; both locked Python resolutions.
MyST Parser       5.1.0                    Markdown support for Sphinx.
MkDocs            1.6.1                    ``mkdocs>=1.6``.
Doxygen           1.18.0                   Pinned hosted end-to-end build.
Graphviz          14.1.2                   Pinned with Doxygen for graph generation.
JSDoc             4.0.5                    Pinned npm fixture and hosted build.
Node.js           22                       Read the Docs JSDoc runtime.
Rust and rustdoc  1.91                     Read the Docs rustdoc runtime.
================  =======================  ================================================

Newer native generator versions are expected to work but are not part of the initial compatibility promise until the
dogfood build and visual fixtures exercise them.

Standalone executables
----------------------

Release artifacts package the same Python command as a standalone executable for Windows, Linux, and macOS on Intel
and ARM64. These binaries make Dockle usable from C++, JavaScript, and Rust repositories without asking contributors
to manage a Python environment. Sphinx, MyST, MkDocs, and Markdown are bundled because they run in Python. Doxygen,
Graphviz, Node.js/JSDoc, and Cargo/rustdoc remain external native toolchains.

A scoped npm package can expose the standalone executable through platform-specific optional packages, following the
same model as other native Node.js tools without creating a second implementation. A crates.io package is less useful:
Cargo expects source that it can compile, while Dockle has no Rust API. Cargo users can consume the standalone release
asset directly; a crate should wait for a Rust-native API or a supported ``cargo-binstall`` contract.

CMake projects
--------------

CMake integration locates the installed or standalone ``dockle`` command and exposes a documentation target. It does
not make Dockle itself a CMake project. ``dockle cmake-dir`` prints the module directory from any Python installation;
add that directory to ``CMAKE_MODULE_PATH`` and use:

.. code-block:: cmake

   include(Dockle)
   dockle_add_docs(docs CONFIG "${PROJECT_SOURCE_DIR}/dockle.toml")

Add ``ALL`` to include documentation in the default build, or ``TARGETS cpp-api`` to build only named Dockle targets.
Set ``DOCKLE_EXECUTABLE`` when a project keeps a standalone binary in a tools directory. Otherwise the module finds the
``dockle`` command and falls back to ``Python3 -m dockle``.

Release requirements
--------------------

The CI workflow obtains its build version from LizardByte's ``release_setup`` action, updates the Python project
metadata only inside the runner, builds the source archive, wheel, and six native executables, and smoke-tests every
executable. A selected ``master`` build creates a draft prerelease containing the Python distributions and native
executables. Changing that release to a stable release triggers the separate release workflow, which downloads the
attached Python distributions and publishes them through PyPI OpenID Connect trusted publishing. Pull requests,
ordinary pushes, drafts, and prereleases never publish to PyPI. GitHub provides artifact digests in its API and user
interface.

Before the first registry release, configure a pending PyPI trusted publisher for the ``LizardByte/dockle`` repository,
the ``ci-release.yml`` workflow, and the ``pypi`` environment. Dockle also needs a documented compatibility matrix for
the native generators.
