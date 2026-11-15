"""Allow ``python -m baselineguard`` and zipapp execution."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
