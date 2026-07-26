# ruff: noqa: F821


def install(dep: object, target: object) -> None:
    FileUtils.download_and_extract_archive_verified(  # type: ignore[unresolved-reference]
        dep.url,
        target,
        dep.archive_type,
        expected_sha256=dep.sha256,
        allowed_hosts=dep.allowed_hosts,
    )
