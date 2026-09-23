from acn_preflight import ACNPreflightClient


def main() -> None:
    client = ACNPreflightClient(timeout=20)

    response = client.bounty_reality_check(
        "https://github.com/owner/repo/issues/123"
    )

    print(response.status_code)
    print(response.body)


if __name__ == "__main__":
    main()
