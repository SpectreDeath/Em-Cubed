"""Unit test suite for Autonomous Agent Gateway & Policy Steering Protocol."""

from em_cubed.gateway.policy_steering import AutonomousPolicySteeringGateway


def test_compile_steering_directive_success():
    payload = AutonomousPolicySteeringGateway.compile_steering_directive(
        user_prompt="Mobilize peacekeeping forces along border",
        confidence_score=0.92,
    )
    assert payload.is_compliant is True
    assert payload.topos_modal_type == "Necessary"
    assert "[FORMAL ONTOLOGICAL POLICY STEERING DIRECTIVE]" in payload.system_steering_directive
    assert "[AGENT PROMPT]: Mobilize peacekeeping forces" in payload.steered_prompt


def test_compile_steering_directive_low_confidence():
    payload = AutonomousPolicySteeringGateway.compile_steering_directive(
        user_prompt="Unsanctioned cyber assault",
        confidence_score=0.20,
    )
    assert payload.is_compliant is False
    assert payload.topos_modal_type == "Assertion"
