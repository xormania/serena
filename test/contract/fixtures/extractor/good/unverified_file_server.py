# ruff: noqa: F821


def install(url: object, target: object) -> None:
    FileUtils.download_file_verified(url, target)  # type: ignore[unresolved-reference]
