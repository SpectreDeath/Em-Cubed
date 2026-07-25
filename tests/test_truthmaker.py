"""Unit tests for Kit Fine's Truthmaker Semantics Engine."""

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.truthmaker import (
    ExactTruthmakerClassifier,
    HyperintensionalEvaluator,
    StateFragment,
)


def test_truthmaker_classification_and_fusion():
    t1 = OntologyTriple(subject="USO_001001", predicate="has_ingredient", object="FolicAcid")
    t2 = OntologyTriple(subject="USO_001001", predicate="has_origin", object="Uruguay")
    t_junk = OntologyTriple(subject="Unrelated_Entity", predicate="has_color", object="Blue")

    state = [t1, t2, t_junk]

    # Classify Exact Truthmaker for ingredient proposition
    tm = ExactTruthmakerClassifier.classify_exact_truthmaker(
        proposition="Ingredient Check",
        state_triples=state,
        relevant_predicates=["has_ingredient", "has_origin"],
    )

    assert tm.is_satisfied is True
    assert len(tm.exact_truthmakers) == 1
    assert len(tm.exact_truthmakers[0].triples) == 2
    assert t_junk not in tm.exact_truthmakers[0].triples

    # Test fusion of state fragments
    f1 = StateFragment(triples=[t1])
    f2 = StateFragment(triples=[t2])
    f_fused = f1.fusion(f2)
    assert len(f_fused.triples) == 2


def test_hyperintensional_evaluator():
    t1 = OntologyTriple(subject="A", predicate="has_fact", object="1")
    t2 = OntologyTriple(subject="B", predicate="has_fact", object="2")

    tm1 = ExactTruthmakerClassifier.classify_exact_truthmaker("Prop_1", [t1], ["has_fact"])
    tm2 = ExactTruthmakerClassifier.classify_exact_truthmaker("Prop_2", [t2], ["has_fact"])

    # Extensionally both true, but hyperintensionally distinct (different underlying truthmaker grounds)
    is_equiv = HyperintensionalEvaluator.are_hyperintensionally_equivalent(tm1, tm2)
    assert is_equiv is False
