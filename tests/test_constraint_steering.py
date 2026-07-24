"""Unit tests for ConstraintSteeringCompiler."""

from em_cubed.ontology.schema import (
    DisjointClassConstraint,
    DomainRangeInference,
    FunctionalPropertyConstraint,
)
from em_cubed.ontology.steering import ConstraintSteeringCompiler


def test_constraint_steering_compiler():
    fc = [FunctionalPropertyConstraint(predicate="has_unique_tax_id")]
    dc = [DisjointClassConstraint(class_a="Vendor", class_b="Employee")]
    dr = [DomainRangeInference(predicate="issues_invoice", domain_class="Vendor", range_class="Company")]

    compiler = ConstraintSteeringCompiler(
        functional_constraints=fc,
        disjoint_constraints=dc,
        domain_range_inferences=dr,
    )

    instructions = compiler.compile_system_instructions()
    assert "CRITICAL ONTOLOGY CONSTRAINT DIRECTIVES" in instructions
    assert "has_unique_tax_id" in instructions
    assert "Vendor" in instructions
    assert "Employee" in instructions
    assert "issues_invoice" in instructions
