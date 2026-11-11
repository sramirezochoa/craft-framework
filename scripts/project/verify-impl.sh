#!/usr/bin/env bash
#
# PROJECT-OWNED — this is yours. The framework never overwrites it.
#
# Sourced by framework/craft.py verify. Define the three functions below
# with your project's commands. Anything you leave undefined is skipped,
# except project_test, which is required.
#
# Helpers available to you: run <label> <cmd...>, ok, bad, skip,
# have <cmd>, and $PY (resolved python interpreter).
#
# Keep this file thin — real logic belongs in your build tool.

project_lint() {
  # Examples:
  #   run "spotless"  ./mvnw -q spotless:check
  #   run "checkstyle" ./mvnw -q checkstyle:check
  #   run "eslint"    npm run --silent lint
  #   run "ruff"      ruff check .

  if [ -f mvnw ]; then
    run "spotless" ./mvnw -q spotless:check
  elif [ -f gradlew ]; then
    run "spotless" ./gradlew --quiet spotlessCheck
  elif [ -f package.json ] && have npm && grep -q '"lint"' package.json; then
    run "npm run lint" npm run --silent lint
  else
    skip "no linter configured — edit scripts/project/verify-impl.sh"
  fi
}

project_test() {
  # Examples:
  #   run "unit + integration" ./mvnw -q verify
  #   run "tests"              ./gradlew --quiet test
  #   run "tests"              npm test --silent
  #   run "pytest"             pytest -q

  if [ -f mvnw ]; then
    run "mvnw verify" ./mvnw -q verify
  elif [ -f gradlew ]; then
    run "gradlew test" ./gradlew --quiet test
  elif [ -f package.json ] && have npm; then
    run "npm test" npm test --silent
  elif have pytest && { [ -d tests ] || [ -d test ]; }; then
    run "pytest" pytest -q
  else
    skip "no test command configured — edit scripts/project/verify-impl.sh"
  fi
}

project_evals() {
  # Only called when evals/ contains cases and --fast was not passed.
  # Examples:
  #   run "eval suite" "$PY" -I evals/run.py
  #   run "eval suite" ./mvnw -q -Pevals test

  if [ -f evals/run.py ] && [ -n "$PY" ]; then
    run "eval suite" "$PY" -I evals/run.py
  else
    skip "no eval runner — edit scripts/project/verify-impl.sh"
  fi
}
