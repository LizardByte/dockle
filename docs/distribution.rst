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

Standalone executables
----------------------

Planned release artifacts will package the same Python command as a standalone executable for each supported operating
system and architecture. These binaries make Dockle usable from C++, JavaScript, and Rust repositories without asking
contributors to manage a Python environment. They do not bundle the upstream documentation generators.

An npm package can be a small launcher that downloads and verifies the matching standalone executable. A future Cargo
package should follow the same model unless Dockle gains a useful Rust-native API; publishing a second implementation
would make behavior drift between ecosystems.

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

Before the first registry release, Dockle needs reproducible multi-platform executable builds, checksums, provenance,
smoke tests for every installation route, a real project license to replace the repository's current placeholder, and
a documented compatibility matrix for the native generators. Registry publishing should happen from one trusted
release workflow after all artifacts pass those checks.
