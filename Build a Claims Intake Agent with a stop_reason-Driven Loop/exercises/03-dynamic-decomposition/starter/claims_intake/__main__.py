import sys

from claims_intake import __version__


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "--version":
        print(__version__)
        return 0
    print(f"claims_intake {__version__}", file=sys.stderr)
    print("usage: python -m claims_intake.run --all", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
