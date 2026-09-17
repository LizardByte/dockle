"""Dockle builds documentation with a shared configuration and visual language."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("dockle")
except PackageNotFoundError:  # pragma: no cover - source tree without package metadata
    __version__ = "0.0.0"
