from pathlib import Path

from polos.adapters.github import GitHubAdapter, GitHubIssueInput
from polos.models.router import ModelRouter


def write_models(root: Path) -> None:
    (root / "models.yaml").write_text(
        """
profile: balanced
profiles:
  balanced:
    decider: openrouter/qwen/qwen-3.7-plus
    worker: openrouter/zai/glm-5.2
    fast: openrouter/google/gemma-4
    oversight: openrouter/xai/grok-4.3
roles:
  taskmaster: { class: decider }
  execution-worker: { class: worker }
  monitor: { class: oversight }
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_model_router_resolves_yaml_and_dry_runs(tmp_path: Path) -> None:
    write_models(tmp_path)
    router = ModelRouter(tmp_path, dry_run=True)

    binding = router.binding_for("taskmaster")
    response = router.complete("taskmaster", [{"role": "user", "content": "plan"}])

    assert binding.model == "openrouter/qwen/qwen-3.7-plus"
    assert response.dry_run
    assert router.oversight_lineage_ok()


def test_github_adapter_documents_external_write_denial() -> None:
    capabilities = GitHubAdapter().describe()

    assert capabilities.name == "github"
    assert "denied" in capabilities.denial
    assert capabilities.supports_network


def test_github_adapter_plans_issue_without_write_access() -> None:
    plan = GitHubAdapter().plan_issue(GitHubIssueInput(12, "Add runtime audit", "Need audit events", ("runtime",)))

    assert plan.branch_name == "polos/issue-12-add-runtime-audit"
    assert not plan.requires_write_access
    assert "external-write approval" in plan.steps[-1]
