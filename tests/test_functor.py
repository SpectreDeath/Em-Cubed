"""Unit tests for Category-Theoretic Monadic Workflow Coprocessor & Surface Functor Engine."""

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.surfaces.functor import OntologyMonad, SurfaceFunctor


def test_surface_functor_mappings():
    t1 = OntologyTriple(subject="Agent_X", predicate="hasRole", object="Auditor")
    t2 = OntologyTriple(subject="Agent_X", predicate="hasAccess", object="Level5")

    # Functor F: Python -> Prolog
    prolog_str = SurfaceFunctor.python_to_prolog([t1, t2])
    assert "hasRole('Agent_X', 'Auditor')." in prolog_str
    assert "hasAccess('Agent_X', 'Level5')." in prolog_str

    # Functor F: Prolog -> Z3 SMT
    z3_str = SurfaceFunctor.prolog_to_z3(prolog_str)
    assert "(declare-fun hasRole (String String) Bool)" in z3_str
    assert '(assert (hasRole "Agent_X" "Auditor"))' in z3_str
    assert "(check-sat)" in z3_str


def test_ontology_monad_unit_map_and_bind():
    # Unit (η)
    initial_triples = [OntologyTriple(subject="Node_A", predicate="connects_to", object="Node_B")]
    m1 = OntologyMonad.unit(initial_triples)
    assert m1.extract() == initial_triples
    assert "unit(initial_state)" in m1.trace

    # Map (Functor mapping)
    m2 = m1.map(lambda state: SurfaceFunctor.python_to_prolog(state))
    assert "connects_to('Node_A', 'Node_B')." in m2.extract()

    # Monadic Bind (>>=)
    def to_z3_monad(prolog_str: str) -> OntologyMonad[str]:
        z3_code = SurfaceFunctor.prolog_to_z3(prolog_str)
        return OntologyMonad(z3_code, trace=["prolog_to_z3_bind"])

    m3 = m2.bind(to_z3_monad)
    assert "(check-sat)" in m3.extract()
    assert "unit(initial_state)" in m3.trace
    assert "prolog_to_z3_bind" in m3.trace
