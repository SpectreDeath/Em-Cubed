"""Kit Fine's Truthmaker Semantics Engine.

Implements exact truthmaker (s ⊩ A) and exact falsemaker (s ⊩f A) classification,
hyperintensional grounding, and state fragment fusion for minimal proof trails.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


@dataclass
class StateFragment:
    """Represents a minimal subset of OntologyTriples or state facts forming a fragment of reality."""

    triples: list[OntologyTriple] = field(default_factory=list)

    def fusion(self, other: StateFragment) -> StateFragment:
        """Compute the fusion (join s ⊔ t) of two state fragments."""
        combined = list(self.triples)
        for t in other.triples:
            if t not in combined:
                combined.append(t)
        return StateFragment(triples=combined)


@dataclass
class ExactTruthmaker:
    """Container storing exact truthmaker state (s ⊩ A) and exact falsemaker state (s ⊩f A)."""

    proposition: str
    exact_truthmakers: list[StateFragment] = field(default_factory=list)
    exact_falsemakers: list[StateFragment] = field(default_factory=list)
    is_satisfied: bool = True
    ground_explanation: str = ""


class ExactTruthmakerClassifier:
    """Classifier evaluating exact truthmaker and falsemaker conditions over state fragments."""

    @staticmethod
    def classify_exact_truthmaker(
        proposition: str,
        state_triples: list[OntologyTriple],
        relevant_predicates: list[str],
    ) -> ExactTruthmaker:
        """Classify a state into exact truthmaker (wholly relevant facts) and falsemaker.

        Parameters
        ----------
        proposition : str
            Target claim or proposition.
        state_triples : list[OntologyTriple]
            Full current state triples.
        relevant_predicates : list[str]
            List of predicates relevant to proposition A (stripping irrelevant junk).

        Returns
        -------
        ExactTruthmaker
            Exact truthmaker and falsemaker evaluation.
        """
        # Filter for wholly relevant state fragment s
        wholly_relevant = [t for t in state_triples if t.predicate in relevant_predicates]
        fragment = StateFragment(triples=wholly_relevant)

        if not wholly_relevant:
            logger.warning("No relevant state fragment found for proposition '%s'", proposition)
            return ExactTruthmaker(
                proposition=proposition,
                exact_falsemakers=[StateFragment(triples=state_triples)],
                is_satisfied=False,
                ground_explanation=f"Exact Falsemaker: Missing relevant facts for predicates {relevant_predicates}",
            )

        logger.info(
            "Classified Exact Truthmaker (s ⊩ A) for '%s' with %d relevant triples.", proposition, len(wholly_relevant)
        )
        return ExactTruthmaker(
            proposition=proposition,
            exact_truthmakers=[fragment],
            is_satisfied=True,
            ground_explanation=f"Exact Truthmaker: Grounded in {len(wholly_relevant)} wholly relevant triples",
        )

    @staticmethod
    def locate_counterfactual_fault(
        proposition: str,
        expected_predicates: list[str],
        actual_triples: list[OntologyTriple],
    ) -> dict[str, Any]:
        """Locate exact counterfactual sub-state fault (minimal sub-state producing falsemaker).

        Returns:
            Dict containing 'fault_detected', 'missing_predicates', 'violating_triples', and 'minimal_fault_substate'.
        """
        actual_preds = {t.predicate for t in actual_triples}
        missing_preds = [p for p in expected_predicates if p not in actual_preds]

        violating_triples = [t for t in actual_triples if t.predicate not in expected_predicates]

        fault_detected = len(missing_preds) > 0 or len(violating_triples) > 0

        return {
            "proposition": proposition,
            "fault_detected": fault_detected,
            "missing_predicates": missing_preds,
            "violating_triples": violating_triples,
            "minimal_fault_substate": StateFragment(triples=violating_triples),
            "explanation": (
                f"Counterfactual fault: missing {missing_preds}, unexpected {len(violating_triples)} triples"
                if fault_detected
                else "No counterfactual fault detected"
            ),
        }


class HyperintensionalEvaluator:
    """Evaluator distinguishing propositions by underlying subject-matter ground."""

    @staticmethod
    def are_hyperintensionally_equivalent(tm1: ExactTruthmaker, tm2: ExactTruthmaker) -> bool:
        """Check whether two propositions share identical exact truthmakers (topic ground)."""
        if tm1.proposition == tm2.proposition:
            return True

        if not tm1.exact_truthmakers or not tm2.exact_truthmakers:
            return False

        # Compare wholly relevant triple contents
        t1_set = {(t.subject, t.predicate, t.object) for f in tm1.exact_truthmakers for t in f.triples}
        t2_set = {(t.subject, t.predicate, t.object) for f in tm2.exact_truthmakers for t in f.triples}

        return t1_set == t2_set

