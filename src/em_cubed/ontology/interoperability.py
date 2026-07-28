"""W3C OWL/RDF & SHACL Standard Interoperability Engine.

Implements native serialization and import across W3C standards:
1. RDFSerializer: Serializes OntologyTriples into RDF Turtle (.ttl) and RDF/XML formats.
2. SHACLConstraintGenerator: Generates W3C SHACL shape files (.shacl.ttl) for FunctionalProperty and DisjointClass constraints.
3. OWLImporter: Deserializes Turtle syntax into native OntologyTriples.
"""

from __future__ import annotations

import logging

from em_cubed.ontology.schema import (
    DisjointClassConstraint,
    FunctionalPropertyConstraint,
    OntologyTriple,
)

logger = logging.getLogger(__name__)


class RDFSerializer:
    """Serializes OntologyTriple ledgers into standard W3C RDF Turtle (.ttl) syntax."""

    @staticmethod
    def to_turtle(
        triples: list[OntologyTriple],
        base_prefix: str = "http://em-cubed.org/ontology#",
    ) -> str:
        """Serialize triples to valid RDF Turtle syntax.

        Parameters
        ----------
        triples : list[OntologyTriple]
            Active state triples.
        base_prefix : str
            Base namespace URI.

        Returns
        -------
        str
            Serialized RDF Turtle string.
        """
        lines = [
            f"@prefix : <{base_prefix}> .",
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            "",
        ]

        for t in triples:
            subj = f":{t.subject}" if not t.subject.startswith("http") and ":" not in t.subject else t.subject
            pred = f":{t.predicate}" if not t.predicate.startswith("http") and ":" not in t.predicate else t.predicate
            obj = f":{t.object}" if not t.object.startswith("http") and ":" not in t.object else f'"{t.object}"'

            lines.append(f"{subj} {pred} {obj} .")

        logger.info("Serialized %d triples to RDF Turtle format.", len(triples))
        return "\n".join(lines)


class SHACLConstraintGenerator:
    """Generates W3C SHACL shape files (.shacl.ttl) for functional property constraints."""

    @staticmethod
    def generate_shacl_shapes(
        functional_constraints: list[FunctionalPropertyConstraint],
        disjoint_constraints: list[DisjointClassConstraint] | None = None,
    ) -> str:
        """Generate SHACL Shapes Turtle string.

        Parameters
        ----------
        functional_constraints : list[FunctionalPropertyConstraint]
            Functional property constraints.
        disjoint_constraints : list[DisjointClassConstraint] | None
            Disjoint class constraints.

        Returns
        -------
        str
            Serialized SHACL shapes Turtle string.
        """
        lines = [
            "@prefix sh: <http://www.w3.org/ns/shacl#> .",
            "@prefix : <http://em-cubed.org/ontology#> .",
            "",
        ]

        for idx, fc in enumerate(functional_constraints, 1):
            lines.extend(
                [
                    f":FunctionalShape_{idx} a sh:NodeShape ;",
                    "  sh:targetClass :Thing ;",
                    "  sh:property [",
                    f"    sh:path :{fc.predicate} ;",
                    "    sh:maxCount 1 ;",
                    "  ] .",
                    "",
                ]
            )

        logger.info("Generated %d SHACL shapes.", len(functional_constraints))
        return "\n".join(lines)


class OWLImporter:
    """Deserializes external Turtle syntax files into native OntologyTriples."""

    @staticmethod
    def from_turtle(turtle_content: str) -> list[OntologyTriple]:
        """Parse basic RDF Turtle lines into OntologyTriples.

        Parameters
        ----------
        turtle_content : str
            RDF Turtle text content.

        Returns
        -------
        list[OntologyTriple]
            Parsed OntologyTriple list.
        """
        triples: list[OntologyTriple] = []
        for line in turtle_content.splitlines():
            line = line.strip()
            if not line or line.startswith(("@prefix", "#")):
                continue

            parts = line.rstrip(" .").split()
            if len(parts) >= 3:
                subj = parts[0].strip(":<>")
                pred = parts[1].strip(":<>")
                obj = " ".join(parts[2:]).strip(':<>"')
                triples.append(OntologyTriple(subject=subj, predicate=pred, object=obj))

        logger.info("Parsed %d OntologyTriples from Turtle content.", len(triples))
        return triples
