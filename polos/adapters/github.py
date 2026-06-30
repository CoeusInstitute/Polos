"""GitHub issue/PR adapter skeleton."""

from __future__ import annotations

from dataclasses import dataclass
import re

from polos.adapters.base import AdapterCapabilities, BaseAdapter


@dataclass(frozen=True, slots=True)
class GitHubIssueInput:
    number: int | None
    title: str
    body: str
    labels: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GitHubTaskPlan:
    title: str
    normalized_goal: str
    branch_name: str
    steps: tuple[str, ...]
    requires_write_access: bool = False


class GitHubAdapter(BaseAdapter):
    capabilities = AdapterCapabilities(
        name="github",
        grants="No GitHub write grants are active by default; future app tokens must be JIT-scoped.",
        denial="Repository writes, pushes, issue edits, and PR creation are denied until policy and approval allow them.",
        output_capture="Issue-like input is converted into task contracts and branch/PR plans.",
        approvals="External-write actions require explicit approval before credentials are activated.",
        secret_protection="Tokens are referenced by secret name only and are never written to task logs.",
        role_mapping="Router parses issue context; Taskmaster plans branch/PR work; Execution Worker performs future scoped GitHub actions.",
        supports_network=True,
    )

    def plan_issue(self, issue: GitHubIssueInput) -> GitHubTaskPlan:
        prefix = f"issue-{issue.number}" if issue.number is not None else "issue"
        slug = slugify(issue.title)
        return GitHubTaskPlan(
            title=issue.title,
            normalized_goal=normalize_issue_goal(issue),
            branch_name=f"polos/{prefix}-{slug}"[:80].rstrip("-"),
            steps=(
                "Create a local task contract from the issue context.",
                "Produce a branch and PR plan without writing to GitHub.",
                "Require external-write approval before any branch push, issue edit, or PR creation.",
            ),
            requires_write_access=False,
        )


def normalize_issue_goal(issue: GitHubIssueInput) -> str:
    body = " ".join(issue.body.split())
    labels = ", ".join(issue.labels) if issue.labels else "none"
    return f"Address GitHub issue '{issue.title}'. Labels: {labels}. Context: {body}"


def slugify(value: str) -> str:
    slug = "-".join(re.findall(r"[a-z0-9]+", value.lower()))
    return slug or "task"
