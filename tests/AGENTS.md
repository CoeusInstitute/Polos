# AGENTS.md — tests/

## Purpose
Runtime tests for the installable Polos Python package.

## Ownership
- Tests in this subtree cover package behavior, especially task contracts, fail-closed policy,
  grant enforcement, governed tool gateway behavior, and loop budget/stop-condition enforcement.

## Local Contracts
- Tests must not require live model providers, network access, provider credentials, or external
  service writes.
- Use temporary directories for generated `.agent/` task state.
- Negative tests are first-class: blocked actions should assert explicit denial, not silent success.

## Work Guidance
- Keep tests focused on runtime authority boundaries and observable artifacts.
- Add regression tests when a policy, grant, or verification edge case is fixed.

## Verification
- `python -m pytest`

## Child DOX Index
No child DOX docs are currently defined for this subtree.
