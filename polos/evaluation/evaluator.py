"""Deterministic Evaluator scaffold for measured, authority-preserving improvements."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EpisodeResult:
    episode_id: str
    baseline_failed: bool
    candidate_failed: bool
    regression: bool = False


@dataclass(frozen=True, slots=True)
class ImprovementProposal:
    proposal_id: str
    target_failure: str
    hypothesis: str
    kind: str
    authority_change: bool = False


@dataclass(slots=True)
class EvaluationResult:
    proposal_id: str
    accepted: bool
    measured_benefit: float
    regressions: list[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "accepted": self.accepted,
            "measured_benefit": self.measured_benefit,
            "regressions": list(self.regressions),
            "reason": self.reason,
        }


def evaluate_proposal(
    proposal: ImprovementProposal,
    episodes: list[EpisodeResult],
    min_measured_benefit: float = 0.05,
    max_regressions: int = 0,
) -> EvaluationResult:
    if proposal.authority_change:
        return EvaluationResult(proposal.proposal_id, False, 0.0, reason="improvements cannot expand authority")
    if not episodes:
        return EvaluationResult(proposal.proposal_id, False, 0.0, reason="no held-out episodes supplied")
    baseline_failures = sum(1 for episode in episodes if episode.baseline_failed)
    candidate_failures = sum(1 for episode in episodes if episode.candidate_failed)
    measured_benefit = (baseline_failures - candidate_failures) / len(episodes)
    regressions = [episode.episode_id for episode in episodes if episode.regression]
    accepted = measured_benefit >= min_measured_benefit and len(regressions) <= max_regressions
    reason = "accepted" if accepted else "benefit threshold or regression gate failed"
    return EvaluationResult(proposal.proposal_id, accepted, measured_benefit, regressions, reason)
