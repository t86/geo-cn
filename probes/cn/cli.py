"""Minimal CLI for the China engine probe contract."""

from __future__ import annotations

import argparse
import json
import sys

from .base import ProbeContext
from .models import EngineId
from .registry import get_probe, list_engines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m probes.cn.cli",
        description="China AI engine visibility probes (stub by default).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_p = sub.add_parser("list-engines", help="List P0 engine IDs")
    list_p.set_defaults(fn="list")

    probe_p = sub.add_parser("probe", help="Run one engine probe")
    probe_p.add_argument("--engine", required=True, choices=list_engines())
    probe_p.add_argument("--query", required=True)
    probe_p.add_argument("--brand")
    probe_p.add_argument("--url")
    probe_p.add_argument("--json", action="store_true")
    probe_p.set_defaults(fn="probe")

    args = parser.parse_args(argv)

    if args.fn == "list":
        print("\n".join(list_engines()))
        return 0

    result = get_probe(EngineId(args.engine)).probe(
        args.query,
        brand=args.brand,
        url=args.url,
        context=ProbeContext(dry_run=True),
    )
    payload = result.to_dict()
    if args.json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"engine={payload['engine']} status={payload['status']} query={payload['query']}")
        for note in payload.get("notes") or []:
            print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
