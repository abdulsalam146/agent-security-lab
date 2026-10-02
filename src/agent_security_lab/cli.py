"""Command line entry point."""
import argparse
import json
from pathlib import Path

from .core import load_cases, markdown_report, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run offline agent security fixtures")
    parser.add_argument("--cases", type=Path, default=Path("cases/starter.json"))
    parser.add_argument("--output", type=Path, default=Path("reports"))
    args = parser.parse_args()
    result = run(load_cases(args.cases))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (args.output / "report.md").write_text(markdown_report(result), encoding="utf-8")
    print(f"Evaluated {result['total_cases']} cases; reports saved to {args.output}")


if __name__ == "__main__":
    main()
