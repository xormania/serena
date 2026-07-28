# Security Considerations

Security is important to us, and we take this topic seriously.

(serena-assumptions)=
## Serena's Assumptions

The current security model for Serena assumes:

- the local machine is trusted,  
- the MCP client (i.e. the LLM) is trusted,
- the code repository being worked on is trusted,
- user configuration is trusted,
- package manager configuration (e.g. npm) for downloading additional dependencies (i.e. language servers when using Serena with the LSP backend) is trusted.

Serena contains tools for executing shell commands and modifying files.
As such tools are, however, an essential part of coding agent workflows, they typically need to be made available – and need to be made available in a flexible, general form.
Therefore, the only way to *fully* protect against unintended consequences is to use a [sandboxed environment](sandboxing) for running Serena.

:::{admonition} Security Advisories
:class: note
Security advisories are welcome for issues that violate the security model described on this page.
However, reports which amount to noting that Serena's tools can execute commands or modify files
describe intended functionality rather than vulnerabilities, and we will reject advisories that fail to recognise this
or otherwise ignore the above assumptions.  
Sandboxing is the *only* way to fully protect against unintended consequences when using coding agents;
constraints on the tools themselves cannot achieve this and are therefore not an approach we pursue.
:::

## General Recommendations for Risk Reduction

To reduce the risk of unintended consequences, we recommend that you:
- back up your work regularly (keep the project being worked on under version control),
- restrict the set of allowed tools via the [configuration](050_configuration),
- do not expose [Serena's network services](network-security) to untrusted networks.

If you do not fully trust the client/the LLM, we additionally recommend to monitor tool executions carefully 
(provided that your MCP client supports this).

(sandboxing)=
## Sandboxing

Sandboxing is the most effective way to mitigate risks when using coding agents.
[Running Serena inside a docker container](docker) which only exposes the necessary files and tools to the agent is a good way to achieve this.

While setting up a sandboxed environment may require some initial effort, we highly recommend it for all security-conscious users.

(network-security)=
## Network Security

Serena includes several network services:
- the Serena MCP server itself (when run in [HTTP or SSE mode](streamable-http) instead of stdio mode)
- the Serena Dashboard web server
- the Serena JetBrains Plugin server, which runs within the JetBrains IDE (when using the JetBrains language backend)
- the Serena Project Server (only started explicitly for [project querying](query-projects)) 

By default, these services accept connections from localhost only, which is a secure default for most users
(given our assumption that the local machine is trusted; see above).

These services can be reconfigured to listen on other addresses, but doing so may have security implications.
If you need to allow connections from other machines, we recommend that you set up a secure networking environment 
(e.g. using a VPN or SSH tunnels) and ensure that only trusted machines can connect to these services.

## Supply Chain Security

Serena has two language backends with different security characteristics:

- the JetBrains-based variant, which integrates with a running JetBrains IDE, and
- the language-server-based variant (the free variant), which can automatically acquire language server dependencies on demand.

While we can assume that JetBrains IDEs installed by the user do not pose a security risk,
language server dependencies (if not handled with care) could. 
For convenience, Serena downloads or installs certain language server dependencies on demand.
We treat this path as security-sensitive and have hardened it accordingly.

The most important supply chain protections are:

- exact version pinning,
- hash verification,
- host restriction,
- and isolated Serena-managed installation directories.

### Auto-Downloaded Language Server Dependencies

For language servers that are auto-installed by downloading archives, binaries, VSIX packages, NuGet packages, or other release artifacts, Serena uses a hardened shared download path with the following protections:

- **Pinned versions by default**: default downloads use exact versions instead of floating `latest` or nightly channels.
- **Integrity verification**: downloaded artifacts are checked against pinned SHA256 hashes stored in Serena's source code.
- **Host allowlists**: download URLs are restricted to the expected hosts for a given dependency.
- **Safe extraction**: archive extraction validates paths to prevent path traversal and zip-slip style attacks.
- **Managed install locations**: dependencies are installed into Serena-managed directories instead of into the project repository.

In practice, this means that a downloaded artifact must match all of the following:

- the expected version,
- the expected host,
- the expected SHA256 checksum,
- and the expected extraction layout.

If any of these checks fail, Serena aborts the installation instead of continuing.

### npm-Based Language Servers

Some language servers are distributed primarily through npm. For those, Serena currently uses pinned package versions and installs them into Serena-managed directories.

By default, Serena uses the **user's normal npm configuration**. We do **not** force a registry override unless one is explicitly configured. If needed, both the package version and the registry can be overridden through `ls_specific_settings`.

For npm-based installs, Serena's current security posture is based on these rules:

- **Exact package versions are pinned by default**.
- **The install location is isolated from the project** and lives in Serena-managed language-server directories.
- **The user's npm configuration is trusted by default**.
- **Repository and user configuration are assumed to be trusted**.

This means Serena protects well against accidental version drift, but npm installs still rely on the npm ecosystem and package-manager execution model. In particular, Serena does **not** currently use lockfile-based `npm ci` installs for bundled language-server dependencies.

### `uvx` and Python Dependency Pinning

Some parts of Serena rely on `uv` / `uvx`.

One important detail is that `uvx` ignores the lockfile when installing directly from a Git repository. Because of that, we pin Serena's Python dependencies exactly in `pyproject.toml` so that installations from Git still resolve to exact dependency versions rather than floating ranges.

For the Pyright, BasedPyright, and `ty` Python language servers, Serena uses exact pinned versions when
invoking them through `uvx` / `uv tool run`. Pyright and BasedPyright default to `1.1.403` and `1.39.9`,
respectively; `ls_specific_settings.python.pyright_version` and
`ls_specific_settings.python_basedpyright.basedpyright_version` can override those pins.

```{dropdown} What Serena Downloads by Default for Language Servers
:open:

Only the language servers listed below download or install additional dependencies automatically by default when the required dependency is missing. Everything else either relies on a system-installed server or on tooling you install separately.

### Release Artifacts, Archives, or VSIX Packages

- **AL**: the pinned Microsoft AL VS Code extension (`ms-dynamics-smb.al`) from the VS Code Marketplace.
- **C/C++ (`clangd`)**: pinned `clangd` release archives on supported platforms.
- **C# (Roslyn LS)**: pinned Roslyn language-server NuGet package for the current platform.
- **Clojure**: pinned `clojure-lsp` release artifact.
- **Dart**: pinned Dart SDK archive that contains the language server.
- **Elixir (`expert`)**: pinned Expert release binary, if not already available locally.
- **Groovy**: pinned `vscode-java` runtime bundle used to provide Java for the Groovy LS setup.
- **HLSL / shader-language-server**: pinned GitHub release artifacts on supported prebuilt platforms.
- **Java (`eclipse.jdt.ls`)**: pinned Gradle distribution, pinned `vscode-java` extension bundle, and pinned IntelliCode VSIX.
- **Kotlin**: pinned Kotlin LSP archive.
- **Lua**: pinned `lua-language-server` release archive.
- **Luau**: pinned `luau-lsp` release archive. In Roblox or standard-doc modes it may also download Luau/Roblox docs and type-definition files.
- **Markdown (`marksman`)**: pinned Marksman release binary.
- **MATLAB**: the pinned MathWorks MATLAB VS Code extension from the VS Code Marketplace.
- **OmniSharp (legacy C# backend)**: pinned OmniSharp and Razor plugin archives.
- **Pascal**: pinned Pascal language-server release artifact.
- **PHP (`phpactor`)**: pinned `phpactor.phar`.
- **PowerShell**: pinned PowerShell Editor Services archive.
- **SystemVerilog (`verible`)**: pinned Verible release archive on supported platforms.
- **TOML (`taplo`)**: pinned Taplo release artifact.
- **Terraform**: pinned `terraform-ls` release archive. The Terraform CLI itself must still already be installed.

### npm Package Installs

- **Angular**: `@angular/language-server`, `@angular/language-service`, plus `typescript` and `typescript-language-server`
- **Ansible**: `@ansible/ansible-language-server`
- **Bash**: `bash-language-server`
- **Elm**: `@elm-tooling/elm-language-server`
- **HTML**: `vscode-langservers-extracted` (provides `vscode-html-language-server`)
- **PHP (`intelephense`)**: `intelephense`
- **SCSS / Sass / CSS**: `some-sass-language-server`
- **Solidity**: `@nomicfoundation/solidity-language-server`
- **Svelte**: `svelte-language-server`
- **TypeScript**: `typescript` and `typescript-language-server`
- **Vue**: `@vue/language-server`, plus `typescript` and `typescript-language-server`
- **VTSLS**: `@vtsls/language-server`
- **YAML**: `yaml-language-server`

All of the above are installed with exact pinned package versions by default, into Serena-managed directories.

### Other Package-Manager Based Installs

- **F#**: installs pinned `fsautocomplete` via `dotnet tool install`.
- **Ruby (`ruby-lsp`)**: if not already available through Bundler or as a global executable, Serena installs a pinned `ruby-lsp` gem.
- **Python (`python`)**: Pyright is launched through `uvx` / `uv tool run` using an exact pinned version.
  Supplying `ls_path` bypasses this managed invocation.
- **Python (`python_basedpyright`)**: BasedPyright is launched through `uvx` / `uv tool run` using an exact
  pinned version. Supplying `ls_path` bypasses this managed invocation.
- **Python (`python_ty`)**: launched through `uvx` / `uv tool run` using an exact pinned `ty` version.
- **HLSL on macOS**: if no prebuilt binary is used, Serena builds `shader_language_server` from a pinned version using Cargo.

### No Automatic Download by Serena

- **Go (`gopls`)**, **Rust (`rust-analyzer`)**, and several other system-tool based integrations expect the language server to be available locally and do not download it automatically.
```

(repository-trust)=
## Repository Trust and Language Servers

Serena's security model assumes that the code repository being worked on is trusted (see [Serena's Assumptions](serena-assumptions)).
This section makes the practical consequences of that assumption explicit, so that you can judge whether it holds for a given repository.

Language servers are ordinary development tools, and Serena runs them the way a code editor does: each language server is started with the project directory as its working directory and as its workspace root.
For many languages, producing accurate symbol information *requires* the language server to understand the project's build, so it resolves the build definition and, in several cases, executes it, exactly as an IDE would.
This happens when the project's language server starts, i.e. when you activate or index a project, and therefore before any tool call is made.

Activating a project in Serena should therefore be treated like opening it in a full-featured IDE, or like running its build: build logic provided by the repository may run.
Where a language server would otherwise run *user*-provided startup files that are not needed for analysis (shell profiles, `.Rprofile`, Julia startup files), Serena suppresses them; those cases are listed below.
Build logic provided by the repository is not suppressed, because the analysis depends on it.

If you need to work with a repository that you do not fully trust, use a [sandboxed environment](sandboxing).

```{dropdown} What Language Servers Execute from the Repository by Default
:open:

The lists below cover the cases that are explicit in Serena's language server integrations.
They are informational rather than a security boundary, and are not guaranteed to be exhaustive: a language server may invoke project tooling on its own, and its behaviour can change between its own versions.
Read the "does not enable this" list as "Serena configures no such behaviour", not as a guarantee.

### Build Definitions and Project Models

- **C#**: Serena opens the repository's `.sln`/`.slnx` and `.csproj` files, so that MSBuild evaluates the project's own props and targets. Serena does not trigger `dotnet restore`.
- **Elixir**: the server runs with `mix_env: dev`, so the project's `mix.exs` is evaluated. Credo integration is enabled and reads the project's `.credo.exs`.
- **F#**: automatic workspace initialisation opens the repository's `.fsproj`/`.sln` files for MSBuild evaluation.
- **Java**: Maven and Gradle project import are enabled and run automatically on first start, with annotation processing and autobuild enabled, so `pom.xml`, `build.gradle`, `build.gradle.kts` and `settings.gradle` are evaluated. By default, Serena uses its own pinned Gradle distribution rather than the repository's `gradlew` (`ls_specific_settings.java.gradle_wrapper_enabled`); this selects *which* Gradle runs the project's build scripts, not *whether* they run.
- **Kotlin**: Serena enables build script support, so Gradle Kotlin build scripts (`build.gradle.kts`) are part of the analysis.
- **Lean 4**: Serena runs `lake env` in the project directory to obtain `LEAN_PATH`, which elaborates the project's `lakefile.lean`.
- **OCaml**: Serena runs `dune build @ocaml-index` in the project directory before starting the server, which executes the project's dune rules.
- **Ruby**: if the project has a `Gemfile`, the server is started through `bundle exec`, which evaluates that `Gemfile`. A `.ruby-version` or `.tool-versions` file is honoured by version managers on the `PATH` and therefore influences which Ruby runs. This applies to both `ruby` (ruby-lsp) and `ruby_solargraph`.
- **Rust**: Cargo build scripts and procedural macros are enabled, so the project's `build.rs` and its proc-macro crates are compiled and run by rust-analyzer.
- **Scala**: Metals derives its compilation model from the project's build definition (`build.sbt` and equivalents) and drives the corresponding build tool in order to do so. This is Metals' own behaviour rather than a Serena setting.
- **Swift**: background indexing and background preparation are enabled, so SourceKit-LSP builds the package; `Package.swift` is itself a Swift program and is run in order to describe the package.
- **Zig**: Serena opens the project's `build.zig` so that ZLS can determine the build graph from it.

### Configuration Discovered in the Repository

- **Clojure**: if the project contains `.lsp/config.edn`, clojure-lsp reads it natively. That file may specify a `:classpath-cmd`, which clojure-lsp runs.
- **Haxe**: Serena auto-discovers an `.hxml` file in the project and passes it to the language server as `displayArguments`. An `.hxml` file may contain compiler directives, including `--cmd`. Set `ls_specific_settings.haxe.buildFile` to choose the file explicitly.
- **Svelte**: Serena starts svelte-language-server in its trusted mode, which is the mode in which it loads the project's `svelte.config.js`.

### Repository-Driven Network Requests

These do not execute content from the repository, but content in the repository determines what is fetched.

- **TOML**: Taplo reads a project-level `.taplo.toml`, which may point it at schema URLs. This is Taplo's own behaviour; Serena passes no schema configuration.
- **YAML**: the SchemaStore catalog is enabled, and per-file `$schema` references cause the referenced schemas to be fetched.

### Language Servers for Which Serena Does Not Enable This

For reference, Serena configures no evaluation of repository build logic for `bash`, `clangd` and `ccls` (C/C++), `gdscript`, `gopls` (Go), `marksman` (Markdown), the Python servers (`python`/Pyright, `python_basedpyright`, `python_ty`, `python_pyrefly`, `python_jedi`) and `typescript` (automatic type acquisition is disabled, so `@types/*` packages are not fetched during indexing).

### Where Serena Suppresses Startup Code

Serena deliberately suppresses startup files that are not needed for analysis:

- **Ansible**: `ansible-lint` integration is off by default (`lint_enabled`), so the project's `.ansible-lint` is not loaded unless you enable it.
- **Julia**: launched with `--startup-file=no --history-file=no`.
- **PowerShell**: launched with `-NoProfile`.
- **R**: launched with `--vanilla`, which suppresses `.Rprofile` and `.Renviron`.
```
