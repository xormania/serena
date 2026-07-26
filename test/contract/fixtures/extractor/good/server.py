# ruff: noqa: F821

import shutil

DEFAULT_VERSION = "v1.2.3"
dependency = RuntimeDependency(  # type: ignore[unresolved-reference]
    platform_id=PlatformId.LINUX_X64,  # type: ignore[unresolved-reference]
    url="https://example.test/server.tar.gz",
    sha256="abc",
    binary_name="server",
)
provider = LanguageServerDependencyProviderUvx(  # type: ignore[unresolved-reference]
    package_name="example-ls", package_version="1.2.3", entrypoint="example-ls"
)


def resolve_version() -> str:
    return "1.2.3"


version = resolve_version()
command = ["cargo", "install", "example-ls", "--version", version, "--locked"]
probe = shutil.which("example-ls")
