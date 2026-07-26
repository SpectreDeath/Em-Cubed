"""Category-Theoretic Monadic Workflow Coprocessor & Surface Functor Engine.

Provides category-theoretic surface functors (F: C -> D) mapping state objects
across reasoning surfaces (Python -> Prolog -> Z3) and monadic containers (M[A])
encapsulating loopy skill state transformations.
"""

from __future__ import annotations

import logging
from typing import Callable, Generic, TypeVar

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.surfaces.morphism import SurfaceMorphism

logger = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")


class SurfaceFunctor:
    """Category-theoretic functor mapping state objects between heterogeneous logic surfaces."""

    @staticmethod
    def python_to_prolog(triples: list[OntologyTriple]) -> str:
        """Functor F: Python -> Prolog."""
        clauses = [SurfaceMorphism.triple_to_prolog(t) for t in triples]
        return "\n".join(clauses)

    @staticmethod
    def prolog_to_z3(prolog_clauses: str) -> str:
        """Functor F: Prolog -> Z3 SMT-LIB2."""
        z3_decls = []
        for line in prolog_clauses.splitlines():
            line = line.strip().rstrip(".")
            if not line:
                continue
            if "(" in line and ")" in line:
                pred = line.split("(")[0]
                args = line.split("(")[1].rstrip(")").split(",")
                clean_args = [a.strip().strip("'").strip('"') for a in args]
                arg_types = " ".join(["String"] * len(clean_args))
                arg_exprs = " ".join([f'"{ca}"' for ca in clean_args])
                z3_decls.append(f"(declare-fun {pred} ({arg_types}) Bool)")
                z3_decls.append(f"(assert ({pred} {arg_exprs}))")
        z3_decls.append("(check-sat)")
        return "\n".join(z3_decls)


class OntologyMonad(Generic[T]):
    """Category-theoretic Monad M[T] encapsulating state transformations with unit, bind, and map."""

    def __init__(self, value: T, trace: list[str] | None = None) -> None:
        self.value: T = value
        self.trace: list[str] = trace or ["unit(initial_state)"]

    @classmethod
    def unit(cls, value: T) -> OntologyMonad[T]:
        """Monadic unit (η): Wraps raw value into Monad M[T]."""
        return cls(value=value, trace=["unit(initial_state)"])

    def bind(self, fn: Callable[[T], OntologyMonad[U]]) -> OntologyMonad[U]:
        """Monadic bind (>>=): Chains computation returning a new Monad M[U]."""
        result_monad = fn(self.value)
        combined_trace = list(self.trace) + result_monad.trace
        logger.info("Executed Monadic Bind (>>=): %s -> %s", self.trace[-1], result_monad.trace[-1])
        return OntologyMonad(value=result_monad.value, trace=combined_trace)

    def map(self, fn: Callable[[T], U]) -> OntologyMonad[U]:
        """Functor map: Applies function fn to wrapped value."""
        new_val = fn(self.value)
        new_trace = list(self.trace) + [f"map({fn.__name__})"]
        return OntologyMonad(value=new_val, trace=new_trace)

    def extract(self) -> T:
        """Unwrap and return value."""
        return self.value
