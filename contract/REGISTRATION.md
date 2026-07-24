<!-- DO NOT EDIT: run `uv run python -m scripts.lsp_contract render-registration` -->
# Language-server registration surfaces

This table is derived from the CUE declarations. Each backend appears exactly once and has all ten required integration surfaces.

## Integration class: TCP-attach

### `gdscript` — TCP-attach

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_gdscript.cue`<br>`src/solidlsp/language_servers/godot_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | — | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | — | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: Bundled server

### `msl` — Bundled server

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_msl.cue`<br>`src/solidlsp/language_servers/msl_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/msl/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/msl/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: Source build

### `hlsl` — Source build

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_hlsl.cue`<br>`src/solidlsp/language_servers/hlsl_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/hlsl/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/hlsl/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: Multi-server composite

### `angular` — Multi-server composite, required fixture bootstrap

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_angular.cue`<br>`src/solidlsp/language_servers/angular_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/angular/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/angular/`<br>`test/solidlsp/angular/conftest.py` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `bash` — Multi-server composite

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_bash.cue`<br>`src/solidlsp/language_servers/bash_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/bash/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/bash/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `csharp_omnisharp` — Multi-server composite, Platform-exclusive, Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_csharp_omnisharp.cue`<br>`src/solidlsp/language_servers/omnisharp.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | — | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | — | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `groovy` — Multi-server composite

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_groovy.cue`<br>`src/solidlsp/language_servers/groovy_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/groovy/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/groovy/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `java` — Multi-server composite

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_java.cue`<br>`src/solidlsp/language_servers/eclipse_jdtls.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/java/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/java/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `solidity` — Multi-server composite

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_solidity.cue`<br>`src/solidlsp/language_servers/solidity_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/solidity/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/solidity/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `svelte` — Multi-server composite, required fixture bootstrap

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_svelte.cue`<br>`src/solidlsp/language_servers/svelte_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/svelte/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/svelte/`<br>`test/solidlsp/svelte/conftest.py` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `vue` — Multi-server composite, required fixture bootstrap

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_vue.cue`<br>`src/solidlsp/language_servers/vue_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/vue/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/vue/`<br>`test/solidlsp/vue/conftest.py` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: Project-dependent

### `lean4` — Project-dependent, CI-provided toolchain, required fixture bootstrap

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_lean4.cue`<br>`src/solidlsp/language_servers/lean4_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/lean4/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/lean4/`<br>`test/solidlsp/lean4/conftest.py` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `ocaml` — Project-dependent, CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_ocaml.cue`<br>`src/solidlsp/language_servers/ocaml_lsp_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/ocaml/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/ocaml/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `ruby` — Project-dependent, CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_ruby.cue`<br>`src/solidlsp/language_servers/ruby_lsp.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/ruby/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/ruby/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `ruby_solargraph` — Project-dependent, Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_ruby_solargraph.cue`<br>`src/solidlsp/language_servers/solargraph.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | — | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | — | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: Platform-exclusive

### `ansible` — Platform-exclusive, CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_ansible.cue`<br>`src/solidlsp/language_servers/ansible_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/ansible/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/ansible/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `cpp_ccls` — Platform-exclusive, CI-provided toolchain, Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_cpp_ccls.cue`<br>`src/solidlsp/language_servers/ccls_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/cpp/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/cpp/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `erlang` — Platform-exclusive, required fixture bootstrap

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_erlang.cue`<br>`src/solidlsp/language_servers/erlang_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/erlang/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/erlang/`<br>`test/solidlsp/erlang/conftest.py` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `nix` — Platform-exclusive, CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_nix.cue`<br>`src/solidlsp/language_servers/nixd_ls.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/nix/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/nix/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `perl` — Platform-exclusive, CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_perl.cue`<br>`src/solidlsp/language_servers/perl_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/perl/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/perl/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `swift` — Platform-exclusive, CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_swift.cue`<br>`src/solidlsp/language_servers/sourcekit_lsp.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/swift/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/swift/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `zig` — Platform-exclusive, CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_zig.cue`<br>`src/solidlsp/language_servers/zls.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/zig/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/zig/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: CI-provided toolchain

### `clojure` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_clojure.cue`<br>`src/solidlsp/language_servers/clojure_lsp.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/clojure/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/clojure/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `cpp` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_cpp.cue`<br>`src/solidlsp/language_servers/clangd_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/cpp/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/cpp/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `elm` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_elm.cue`<br>`src/solidlsp/language_servers/elm_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/elm/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/elm/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `go` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_go.cue`<br>`src/solidlsp/language_servers/gopls.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/go/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/go/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `haskell` — CI-provided toolchain, required fixture bootstrap

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_haskell.cue`<br>`src/solidlsp/language_servers/haskell_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/haskell/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/haskell/`<br>`test/solidlsp/haskell/conftest.py` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `haxe` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_haxe.cue`<br>`src/solidlsp/language_servers/haxe_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/haxe/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/haxe/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `julia` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_julia.cue`<br>`src/solidlsp/language_servers/julia_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/julia/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/julia/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `lua` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_lua.cue`<br>`src/solidlsp/language_servers/lua_ls.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/lua/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/lua/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `pascal` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_pascal.cue`<br>`src/solidlsp/language_servers/pascal_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/pascal/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/pascal/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `qml` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_qml.cue`<br>`src/solidlsp/language_servers/qml_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/qml/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/qml/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `r` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_r.cue`<br>`src/solidlsp/language_servers/r_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/r/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/r/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `rego` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_rego.cue`<br>`src/solidlsp/language_servers/regal_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/rego/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/rego/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `rust` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_rust.cue`<br>`src/solidlsp/language_servers/rust_analyzer.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/rust/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/rust/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `scala` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_scala.cue`<br>`src/solidlsp/language_servers/scala_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/scala/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/scala/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `systemverilog` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_systemverilog.cue`<br>`src/solidlsp/language_servers/systemverilog_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/systemverilog/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/systemverilog/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `terraform` — CI-provided toolchain

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_terraform.cue`<br>`src/solidlsp/language_servers/terraform_ls.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/terraform/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/terraform/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: Alternate backend

### `php_phpactor` — Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_php_phpactor.cue`<br>`src/solidlsp/language_servers/phpactor.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/php/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/php/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `php_phpantom` — Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_php_phpantom.cue`<br>`src/solidlsp/language_servers/phpantom.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/php/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/php/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `python_basedpyright` — Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_python_basedpyright.cue`<br>`src/solidlsp/language_servers/basedpyright_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/python/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/python/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `python_jedi` — Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_python_jedi.cue`<br>`src/solidlsp/language_servers/jedi_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | — | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | — | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `python_pyrefly` — Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_python_pyrefly.cue`<br>`src/solidlsp/language_servers/pyrefly_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/python/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/python/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `python_ty` — Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_python_ty.cue`<br>`src/solidlsp/language_servers/ty_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/python/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/python/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `typescript_vts` — Alternate backend

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_typescript_vts.cue`<br>`src/solidlsp/language_servers/vts_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | — | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | — | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

## Integration class: Standard

### `ada` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_ada.cue`<br>`src/solidlsp/language_servers/ada_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/ada/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/ada/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `al` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_al.cue`<br>`src/solidlsp/language_servers/al_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/al/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/al/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `bsl` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_bsl.cue`<br>`src/solidlsp/language_servers/bsl_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/bsl/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/bsl/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `crystal` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_crystal.cue`<br>`src/solidlsp/language_servers/crystal_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/crystal/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/crystal/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `csharp` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_csharp.cue`<br>`src/solidlsp/language_servers/csharp_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/csharp/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/csharp/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `cue` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_cue.cue`<br>`src/solidlsp/language_servers/cue_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/cue/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/cue/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `dart` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_dart.cue`<br>`src/solidlsp/language_servers/dart_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/dart/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/dart/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `elixir` — required fixture bootstrap

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_elixir.cue`<br>`src/solidlsp/language_servers/elixir_tools/elixir_tools.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/elixir/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/elixir/`<br>`test/solidlsp/elixir/conftest.py` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `fortran` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_fortran.cue`<br>`src/solidlsp/language_servers/fortran_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/fortran/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/fortran/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `fsharp` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_fsharp.cue`<br>`src/solidlsp/language_servers/fsharp_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/fsharp/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/fsharp/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `html` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_html.cue`<br>`src/solidlsp/language_servers/vscode_html_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/html/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/html_ls/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `json` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_json.cue`<br>`src/solidlsp/language_servers/json_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/json/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/json_ls/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `kotlin` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_kotlin.cue`<br>`src/solidlsp/language_servers/kotlin_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/kotlin/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/kotlin/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `latex` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_latex.cue`<br>`src/solidlsp/language_servers/texlab_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/latex/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/latex/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `luau` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_luau.cue`<br>`src/solidlsp/language_servers/luau_lsp.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/luau/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/luau/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `markdown` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_markdown.cue`<br>`src/solidlsp/language_servers/marksman.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/markdown/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/markdown/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `matlab` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_matlab.cue`<br>`src/solidlsp/language_servers/matlab_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/matlab/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/matlab/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `php` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_php.cue`<br>`src/solidlsp/language_servers/intelephense.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/php/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/php/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `powershell` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_powershell.cue`<br>`src/solidlsp/language_servers/powershell_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/powershell/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/powershell/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `python` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_python.cue`<br>`src/solidlsp/language_servers/pyright_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/python/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/python/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `scss` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_scss.cue`<br>`src/solidlsp/language_servers/some_sass_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/scss/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/scss/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `toml` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_toml.cue`<br>`src/solidlsp/language_servers/taplo_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/toml/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/toml/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `typescript` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_typescript.cue`<br>`src/solidlsp/language_servers/typescript_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/typescript/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/typescript/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |

### `yaml` — Standard

| Surface | Path | Authority | Enforced by |
|---:|---|---|---|
| 1 | `contract/declaration_backend_yaml.cue`<br>`src/solidlsp/language_servers/yaml_language_server.py` | contract-authoritative + declared<br>code-authoritative + extracted | C-PROV-001, C-PROV-002, C-PROV-003, C-PROV-004, C-PROV-005, C-PROV-006, C-PLAT-001, C-CACHE-001 |
| 2 | `src/solidlsp/ls_config.py#LanguageServerId` | code-authoritative + extracted | C-REG-001 |
| 3 | `src/solidlsp/ls_config.py#get_source_fn_matcher` | code-authoritative + extracted | C-REG-003, B-REG-001 |
| 4 | `src/solidlsp/ls_config.py#get_ls_class` | code-authoritative + extracted | C-REG-002, B-REG-002 |
| 5 | `src/solidlsp/ls_config.py#is_experimental`<br>`src/solidlsp/ls_config.py#is_programming_language`<br>`src/solidlsp/ls_config.py#get_priority` | code-authoritative + extracted | C-REG-004 |
| 6 | `pyproject.toml#tool.pytest.ini_options.markers` | code-authoritative + extracted | C-TEST-001, C-TEST-004 |
| 7 | `test/resources/repos/yaml/test_repo/` | code-authoritative + extracted | C-TEST-002, C-TEST-006 |
| 8 | `test/solidlsp/yaml_ls/` | code-authoritative + extracted | C-TEST-003, C-FIX-001, C-FIX-002, C-FIX-003 |
| 9 | `test/conftest.py`<br>`test/serena/test_serena_agent.py` | code-authoritative + extracted | C-TEST-005, C-SKIP-001, C-SKIP-002, C-CAP-001, B-SKIP-001 |
| 10 | `.github/workflows/pytest.yml`<br>`README.md`<br>`docs/01-about/020_programming-languages.md`<br>`CHANGELOG.md`<br>`src/serena/resources/project.template.yml` | code-authoritative + extracted<br>contract-derived + generated | C-CI-001, C-CI-002, C-CI-003, C-CI-004, C-CI-005, C-CI-006, C-CI-007, C-CACHE-001, C-CACHE-002, C-DOC-001, C-GEN-001, C-REG-007 |
