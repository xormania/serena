# ruff: noqa: F821


def install(url: object, target: object, checksum: object, hosts: object) -> None:
    FileUtils.download_and_extract_archive_verified(  # type: ignore[unresolved-reference]
        url, target, "zip", expected_sha256=checksum, allowed_hosts=hosts
    )
