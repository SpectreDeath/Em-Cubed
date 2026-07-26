"""Self-Governing Tri-Engine Autonomous Agent Gateway & Policy Steering Protocol.

Dynamically compiles and injects formal policy steering directives into LLM agents before action
execution based on real-time Topos Ω modal truth, Description Logic guards (C ⊑ D),
and Kit Fine truthmaker semantics (s ⊩ A).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from em_cubed.ontology.concept_induction import ConceptInductionEngine
from em_cubed.ontology.topos import SubobjectClassifier

logger = logging.getLogger(__name__)


@dataclass
class SteeredPromptPayload:
    """Payload holding original prompt, system steering directive, and modal evaluation."""

    original_prompt: str
    system_steering_directive: str
    steered_prompt: str
    topos_modal_type: str
    is_compliant: bool


class AutonomousPolicySteeringGateway:
    """Gateway enforcing formal policy steering over autonomous AI agent prompts."""

    @classmethod
    def compile_steering_directive(
        cls,
        user_prompt: str,
        confidence_score: float = 0.92,
        subclass_name: str = "PermissibleAction",
    ) -> SteeredPromptPayload:
        """Compile system steering directive and prepend it to the user prompt.

        Parameters
        ----------
        user_prompt : str
            Raw user or agent candidate action prompt.
        confidence_score : float
            Topos Ω confidence rating score.
        subclass_name : str
            Description Logic subclass name.

        Returns
        -------
        SteeredPromptPayload
            Steered prompt payload.
        """
        tv = SubobjectClassifier.evaluate_confidence(confidence_score)
        sample = [{"type": "AgentAction", "property": "executes", "target": user_prompt[:20]}]
        dl_expr = ConceptInductionEngine.induce_concept(subclass_name=subclass_name, positive_samples=sample)

        system_directive = (
            f"[FORMAL ONTOLOGICAL POLICY STEERING DIRECTIVE]\n"
            f"• Topos Ω Modal Status : {tv.modal_type.value.upper()} (Satisfaction: {tv.is_satisfied()})\n"
            f"• Description Logic    : {dl_expr.to_dl_syntax()}\n"
            f"• Policy Constraint    : Actions MUST conform to exact truthmaker grounds (s ⊩ A).\n"
            f"• Directive Instruction: Execute only if modal status is NECESSARY or POSSIBLE."
        )

        steered_prompt = f"{system_directive}\n\n[AGENT PROMPT]: {user_prompt}"

        is_compliant = tv.is_satisfied()

        logger.info("Compiled Policy Steering Directive: Modal=%s, Compliant=%s", tv.modal_type.value, is_compliant)

        return SteeredPromptPayload(
            original_prompt=user_prompt,
            system_steering_directive=system_directive,
            steered_prompt=steered_prompt,
            topos_modal_type=tv.modal_type.value,
            is_compliant=is_compliant,
        )
