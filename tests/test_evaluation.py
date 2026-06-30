from polos.evaluation.evaluator import EpisodeResult, ImprovementProposal, evaluate_proposal


def test_evaluator_accepts_measured_non_regressing_improvement() -> None:
    proposal = ImprovementProposal("proposal-1", "repeated validation miss", "tighten check", "lesson")
    episodes = [
        EpisodeResult("a", baseline_failed=True, candidate_failed=False),
        EpisodeResult("b", baseline_failed=True, candidate_failed=False),
        EpisodeResult("c", baseline_failed=False, candidate_failed=False),
    ]

    result = evaluate_proposal(proposal, episodes, min_measured_benefit=0.05)

    assert result.accepted
    assert result.measured_benefit > 0


def test_evaluator_rejects_authority_expansion() -> None:
    proposal = ImprovementProposal(
        "proposal-2",
        "blocked tool use",
        "let learning grant shell",
        "policy",
        authority_change=True,
    )

    result = evaluate_proposal(proposal, [])

    assert not result.accepted
    assert result.reason == "improvements cannot expand authority"


def test_evaluator_rejects_regressions() -> None:
    proposal = ImprovementProposal("proposal-3", "miss", "change", "lesson")
    episodes = [EpisodeResult("a", baseline_failed=True, candidate_failed=False, regression=True)]

    result = evaluate_proposal(proposal, episodes)

    assert not result.accepted
    assert result.regressions == ["a"]
