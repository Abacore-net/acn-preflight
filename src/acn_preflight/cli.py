from __future__ import annotations

import argparse
import json
from .client import ACNPreflightClient

def _emit(response) -> int:
    print(json.dumps({"http_status": response.status_code, "body": response.body}, indent=2, sort_keys=True))
    return 0 if response.status_code < 500 else 1

def main() -> None:
    parser = argparse.ArgumentParser(prog="acn-preflight")
    parser.add_argument("--base-url", default="https://preflight.abacore.net")
    sub = parser.add_subparsers(dest="command", required=True)
    bounty = sub.add_parser("bounty")
    bounty.add_argument("issue_url")
    repo = sub.add_parser("repo")
    repo.add_argument("repo_url")
    repo.add_argument("--change-type", choices=["bugfix", "feature", "docs", "dependency"])
    repo.add_argument("--access-token")
    payment = sub.add_parser("payment")
    payment.add_argument("--chain", required=True)
    payment.add_argument("--address", required=True)
    payment.add_argument("--token-contract")
    payment.add_argument("--amount")
    payment.add_argument("--access-token")
    sub.add_parser("x402")
    args = parser.parse_args()
    client = ACNPreflightClient(args.base_url)
    if args.command == "bounty":
        raise SystemExit(_emit(client.bounty_reality_check(args.issue_url)))
    if args.command == "repo":
        raise SystemExit(_emit(client.repo_contribution_readiness(args.repo_url, change_type=args.change_type, access_token=args.access_token)))
    if args.command == "payment":
        raise SystemExit(_emit(client.payment_preflight(chain=args.chain, address=args.address, token_contract=args.token_contract, amount=args.amount, access_token=args.access_token)))
    raise SystemExit(_emit(client.x402_manifest()))

if __name__ == "__main__":
    main()
