# ruff: noqa: F821


def install(url: object, target: object) -> None:
    urllib.request.urlretrieve(url, target)  # type: ignore[unresolved-reference]
    urllib.request.urlopen(url)  # type: ignore[unresolved-reference]
