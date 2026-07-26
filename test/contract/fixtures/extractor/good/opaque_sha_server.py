# ruff: noqa: F821


def checksum_for(version: str) -> str:
    return version


dependency = RuntimeDependency(  # type: ignore[unresolved-reference]
    id="opaque-sha",
    platform_id="linux-x64",
    url="https://example.test/opaque-sha.zip",
    sha256=checksum_for("1.0.0"),
    allowed_hosts=["example.test"],
    archive_type="zip",
)
