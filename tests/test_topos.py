"""Unit tests for TruthValue, ModalType, and SubobjectClassifier."""

from em_cubed.ontology.topos import ModalType, SubobjectClassifier, TruthValue


def test_truth_value_satisfaction():
    tv_pass = TruthValue(is_boolean=True, confidence=0.9, modal_type=ModalType.NECESSARY)
    assert tv_pass.is_satisfied(min_confidence=0.8) is True

    tv_fail = TruthValue(is_boolean=True, confidence=0.5, modal_type=ModalType.POSSIBLE)
    assert tv_fail.is_satisfied(min_confidence=0.8) is False


def test_subobject_classifier_methods():
    tv_bool = SubobjectClassifier.classify_boolean(True, "Boolean pass")
    assert tv_bool.is_boolean is True
    assert tv_bool.confidence == 1.0

    tv_modal = SubobjectClassifier.classify_modal(True, ModalType.NECESSARY, confidence=0.95, message="Modal pass")
    assert tv_modal.modal_type == ModalType.NECESSARY
    assert tv_modal.confidence == 0.95

    tv_temp = SubobjectClassifier.classify_temporal(True, step=5, validity_window=(1, 10), message="Step 5 in window")
    assert tv_temp.is_boolean is True

    tv_temp_out = SubobjectClassifier.classify_temporal(True, step=15, validity_window=(1, 10), message="Step 15 out of window")
    assert tv_temp_out.is_boolean is False
