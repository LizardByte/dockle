"""Command-line interface for Dockle."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from dockle import __version__
from dockle.builders import BuildError, BuildManager
from dockle.config import ConfigError, load_config
from dockle.theme import ThemeError


def build_parser() -> argparse.ArgumentParser:
    """Create the Dockle argument parser."""

    parser = argparse.ArgumentParser(
        prog="dockle",
        description="Build documentation with multiple frameworks and one consistent theme.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("dockle.toml"),
        help="Dockle configuration file (default: dockle.toml)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="validate configuration, sources, and tools")
    check.add_argument("targets", nargs="*", help="target names (default: all)")

    build = subparsers.add_parser("build", help="build one or more documentation targets")
    build.add_argument("targets", nargs="*", help="target names (default: all)")
    build.add_argument(
        "--dry-run",
        action="store_true",
        help="print generated commands without writing or running them",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Dockle CLI and return a process exit code."""

    arguments = build_parser().parse_args(argv)
    try:
        config = load_config(arguments.config)
        targets = config.select_targets(arguments.targets)
        manager = BuildManager(config)

        if arguments.command == "check":
            failed = False
            print(f"OK configuration: {config.path}")
            for target, problem in manager.check(targets):
                if problem:
                    failed = True
                    print(f"ERROR {target.name} ({target.framework}): {problem}")
                else:
                    print(f"OK {target.name} ({target.framework}): {target.source}")
            return 1 if failed else 0

        if arguments.dry_run:
            for target in targets:
                plan = manager.plan(target)
                print(f"{target.name} ({target.framework}) -> {target.output}")
                print(f"  {plan.command.display()}")
            return 0

        for result in manager.build(targets):
            suffix = f", themed {result.themed_pages} HTML page(s)" if result.themed_pages else ""
            print(f"Built {result.target.name} -> {result.target.output}{suffix}")
        return 0
    except (BuildError, ConfigError, ThemeError) as error:
        print(f"dockle: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

