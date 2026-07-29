from __future__ import annotations

import argparse

from .pipeline import (
    build_bundles,
    build_postgres,
    build_release,
    build_sqlite,
    load,
    quality_report,
    validate,
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="usmle_kb")
    parser.add_argument(
        "command", choices=["validate", "build", "quality-report", "diff-release", "all"]
    )
    parser.add_argument("target", nargs="?")
    args = parser.parse_args()
    tables = load()
    if args.command == "validate":
        errors = validate(tables)
        if errors:
            parser.error("; ".join(errors))
        print("Validation passed")
    elif args.command == "quality-report":
        print(quality_report(tables))
    elif args.command == "diff-release":
        print("No prior release baseline configured.")
    elif args.command == "all":
        build_release(tables)
        quality_report(tables)
        print("Release pipeline completed")
    elif args.target == "sqlite":
        print(build_sqlite(tables))
    elif args.target == "postgres":
        print(build_postgres(tables))
    elif args.target == "bundles":
        print(build_bundles(tables))
    elif args.target == "release":
        print(build_release(tables))
    else:
        parser.error("build requires sqlite, postgres, bundles, or release")


if __name__ == "__main__":
    main()
