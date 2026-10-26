"""Minimal CLI for the China engine probe contract."""

from __future__ import annotations

import argparse
import json
import sys

from .base import ProbeContext
from .models import EngineId
from .registry import get_probe, list_engines, live_engines, refresh_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m probes.cn.cli",
        description=(
            "China AI engine visibility probes. "
            "Default is stub/dry-run. Live DeepSeek + 智谱 when API keys are set and --live is passed."
        ),
        epilog=(
            "Env: DEEPSEEK_API_KEY; ZHIPU_API_KEY or BIGMODEL_API_KEY; "
            "optional DEEPSEEK_WEB_SEARCH=1 for Anthropic web_search path. "
            "Other engines (doubao/tongyi/kimi/ernie/yuanbao) remain stub."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    list_p = sub.add_parser("list-engines", help="List engine IDs (includes zhipu)")
    list_p.add_argument(
        "--live-status",
        action="store_true",
        help="Also print which engines have live adapters registered from env keys",
    )
    list_p.set_defaults(fn="list")

    probe_p = sub.add_parser("probe", help="Run one engine probe")
    probe_p.add_argument("--engine", required=True, choices=list_engines())
    probe_p.add_argument("--query", required=True)
    probe_p.add_argument("--brand")
    probe_p.add_argument("--url")
    probe_p.add_argument("--json", action="store_true")
    probe_p.add_argument(
        "--live",
        action="store_true",
        help="dry_run=False; call live adapters when keys are present (else STUB/ERROR honestly)",
    )
    probe_p.add_argument(
        "--web-search",
        action="store_true",
        help="Hint DeepSeek Anthropic web_search path (or set DEEPSEEK_WEB_SEARCH=1)",
    )
    probe_p.set_defaults(fn="probe")

    args = parser.parse_args(argv)

    # Re-read env in case keys were exported after import
    refresh_registry()

    if args.fn == "list":
        print("\n".join(list_engines()))
        if args.live_status:
            live = live_engines()
            print("---")
            print(
                "live_adapters="
                + (",".join(live) if live else "(none — set DEEPSEEK_API_KEY / ZHIPU_API_KEY)")
            )
        return 0

    extra = {}
    if args.web_search:
        extra["web_search"] = True
    result = get_probe(EngineId(args.engine)).probe(
        args.query,
        brand=args.brand,
        url=args.url,
        context=ProbeContext(dry_run=not args.live, extra=extra),
    )
    payload = result.to_dict()
    if args.json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"engine={payload['engine']} status={payload['status']} query={payload['query']}")
        if payload.get("brand_mentioned") is not None:
            print(
                f"brand_mentioned={payload['brand_mentioned']} brand_cited={payload.get('brand_cited')}"
            )
        if payload.get("answer_excerpt"):
            print(f"excerpt={payload['answer_excerpt'][:200]}")
        if payload.get("error"):
            print(f"error={payload['error']}")
        for note in payload.get("notes") or []:
            print(f"- {note}")
    return 0 if payload.get("status") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
