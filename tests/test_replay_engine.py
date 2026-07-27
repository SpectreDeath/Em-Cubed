"""Unit test suite for Verifiable Replay Engine."""

from em_cubed.ontology.replay_engine import EpistemicReplayEngine


def test_replay_engine_recording_and_integrity():
    engine = EpistemicReplayEngine()

    f1 = engine.record_frame(0, 0.89, "Necessary", {"actors": 10})
    f2 = engine.record_frame(1, 0.92, "Necessary", {"actors": 12})

    assert len(engine.frames) == 2
    assert f2.previous_hash == f1.frame_hash
    assert engine.verify_integrity() is True


def test_replay_step_lookup():
    engine = EpistemicReplayEngine()
    engine.record_frame(0, 0.89, "Necessary", {"actors": 10})
    engine.record_frame(1, 0.95, "Necessary", {"actors": 15})

    replayed = engine.replay_step(1)
    assert replayed is not None
    assert replayed.strategify_actor_state["actors"] == 15


def test_replay_tamper_detection():
    engine = EpistemicReplayEngine()
    engine.record_frame(0, 0.89, "Necessary", {"actors": 10})
    engine.record_frame(1, 0.95, "Necessary", {"actors": 15})

    # Tamper with frame 0 state
    engine.frames[0].sme_trust_score = 0.10
    assert engine.verify_integrity() is False
