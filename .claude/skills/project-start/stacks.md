# Stack reference for `project-start`

Derive `scripts/project/verify-impl.sh` and `.github/actions/setup/action.yml`
from the developer's answers. The rows are each stack's usual choices — offer
them as defaults, never apply them silently. For a stack not listed, ask for
the lint and test commands and the file that marks the project as created.

Verify each command against the tool's current documentation before relying on
it; toolchains change faster than this table.

## Commands

| Stack | Marker file | Lint | Test |
|---|---|---|---|
| Java · Maven | `pom.xml` | `./mvnw -q spotless:check` (Spotless) · `./mvnw -q checkstyle:check` (Checkstyle) | `./mvnw -q verify` |
| Java / Kotlin · Gradle | `build.gradle` or `build.gradle.kts` | `./gradlew --quiet spotlessCheck` · `./gradlew --quiet ktlintCheck` | `./gradlew --quiet test` |
| Node · npm | `package.json` | `npm run --silent lint` (ESLint) | `npm test --silent` |
| Node · pnpm | `package.json` | `pnpm lint` | `pnpm test` |
| Node · yarn | `package.json` | `yarn lint` | `yarn test` |
| Python · uv | `pyproject.toml` | `uv run ruff check .` | `uv run pytest -q` |
| Python · Poetry | `pyproject.toml` | `poetry run ruff check .` | `poetry run pytest -q` |
| Python · pip | `pyproject.toml` or `requirements.txt` | `ruff check .` | `pytest -q` |
| Go | `go.mod` | `go vet ./...` · `golangci-lint run` | `go test ./...` |
| .NET | `*.sln` or `*.csproj` | `dotnet format --verify-no-changes` | `dotnet test` |
| Rust | `Cargo.toml` | `cargo clippy -- -D warnings` · `cargo fmt --check` | `cargo test` |

## `verify-impl.sh` pattern

Keep the file's header comment. Guard every function on the marker file, so
verify reports the project as *not scaffolded yet* — visibly, without failing —
until change 001 creates it. Example for Java · Maven · Spotless:

```bash
SCAFFOLD_MSG="not scaffolded yet — change 001 creates the project skeleton"

project_lint() {
  if [ ! -f pom.xml ]; then skip "$SCAFFOLD_MSG"; return; fi
  run "spotless" ./mvnw -q spotless:check
}

project_test() {
  if [ ! -f pom.xml ]; then skip "$SCAFFOLD_MSG"; return; fi
  run "mvnw verify" ./mvnw -q verify
}

project_evals() {
  if [ -f evals/run.py ] && [ -n "$PY" ]; then
    run "eval suite" "$PY" -I evals/run.py
  else
    skip "no eval runner — edit scripts/project/verify-impl.sh"
  fi
}
```

For a glob marker (`*.csproj`) use `compgen -G "*.csproj" >/dev/null` instead of
`[ -f … ]`. Keep `project_evals` as shipped unless the stack runs evals itself.

## CI setup action

`.github/actions/setup/action.yml` is a composite action. Pin the versions from
the interview.

**Day one has no lockfile.** Leave `cache:` off the setup step — setup-java and
setup-node fail when the file they cache on is missing — and guard install
steps on the marker file. Change 001 turns caching on once the files exist.

| Stack | Steps |
|---|---|
| Java | `actions/setup-java@v4` with `java-version`, `distribution: temurin` |
| Node · npm | `actions/setup-node@v4` with `node-version`; then `npm ci` guarded on `package-lock.json` |
| Node · pnpm | `pnpm/action-setup@v4`, `actions/setup-node@v4`; then `pnpm install --frozen-lockfile` guarded on `pnpm-lock.yaml` |
| Python · uv | `astral-sh/setup-uv@v5`; then `uv sync` guarded on `uv.lock` |
| Python · Poetry / pip | Python is already installed by the verify workflow; add `pipx install poetry` or `pip install -r requirements.txt`, guarded |
| Go | `actions/setup-go@v5` with `go-version` |
| .NET | `actions/setup-dotnet@v4` with `dotnet-version` |
| Rust | `dtolnay/rust-toolchain@stable` with `components: clippy, rustfmt` |

Guarded step:

```yaml
    - name: Install dependencies
      if: hashFiles('package-lock.json') != ''
      shell: bash
      run: npm ci
```

Every `run:` step in a composite action needs `shell: bash`. Remove the
placeholder "No project toolchain configured" step once real steps exist.
