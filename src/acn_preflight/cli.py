from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .client import ACNPreflightClient, ACNPreflightError, DEFAULT_BASE_URL, DEFAULT_TIMEOUT


def _emit(response) -> int:
    payload = {
        "http_status": response.status_code,
        "body": response.body,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if response.status_code < 400 or response.status_code == 402 else 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acn-preflight",
        description="Deterministic preflight checks for AI agents and automation.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("ACN_PREFLIGHT_BASE_URL", DEFAULT_BASE_URL),
        help="Hosted ACN Preflight base URL.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout in seconds. Default: 30.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    bounty = sub.add_parser(
        "bounty",
        help="Check current public evidence for a GitHub bounty or issue.",
    )
    bounty.add_argument("issue_url")

    repo = sub.add_parser(
        "repo",
        help="Check repository contribution readiness.",
    )
    repo.add_argument("repo_url")
    repo.add_argument(
        "--change-type",
        choices=["bugfix", "feature", "docs", "dependency"],
    )

    payment = sub.add_parser(
        "payment",
        help="Run technical payment preflight.",
    )
    payment.add_argument("--chain", required=True)
    payment.add_argument("--address", required=True)
    payment.add_argument("--token-contract")
    payment.add_argument("--amount")

    sub.add_parser(
        "x402",
        help="Fetch the hosted x402 capability manifest.",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        client = ACNPreflightClient(args.base_url, timeout=args.timeout)

        if args.command == "bounty":
            raise SystemExit(_emit(client.bounty_reality_check(args.issue_url)))
        if args.command == "repo":
            raise SystemExit(
                _emit(
                    client.repo_contribution_readiness(
                        args.repo_url,
                        change_type=args.change_type,
                    )
                )
            )
        if args.command == "payment":
            raise SystemExit(
                _emit(
                    client.payment_preflight(
                        chain=args.chain,
                        address=args.address,
                        token_contract=args.token_contract,
                        amount=args.amount,
                    )
                )
            )

        raise SystemExit(_emit(client.x402_manifest()))
    except (ACNPreflightError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "error": "acn_preflight_client_error",
                    "message": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
