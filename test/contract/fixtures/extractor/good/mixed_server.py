# ruff: noqa: F821

dependency = RuntimeDependency(  # type: ignore[unresolved-reference]
    id="mixed",
    platform_id=platform_key,  # type: ignore[unresolved-reference]
    url="https://example.test/mixed.zip",
    sha256="abc",
    allowed_hosts=["example.test"],
)


def install(url: object, target: object, checksum: object, hosts: object) -> None:
    FileUtils.download_and_extract_archive_verified(  # type: ignore[unresolved-reference]
        url, target, "zip", expected_sha256=checksum, allowed_hosts=hosts
    )
