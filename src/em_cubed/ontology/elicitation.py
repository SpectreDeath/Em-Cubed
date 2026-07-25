"""Knowledge Elicitation Framework: From Natural Language to Formal Ontology.

Implements the 6-stage knowledge elicitation pipeline:
1. Strategic Foundation: Scoping & Value Alignment (DSQs)
2. Idea Plane: PMEST Faceted Analysis
3. Disambiguation: DSQ-to-CQ Iterative Loop
4. Structural Integrity: OntoClean & BFO Independent vs Role Partitioning
5. Common Logic Echo Dialogue: Human-Machine Confirmation
6. Formal Alignment: BFO / CCO / IOF Alignment & Triple Extraction
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


class PMESTCategory(str, Enum):
    """Ranganathan PMEST Facet Categories."""

    PERSONALITY = "Personality"
    MATTER = "Matter"
    ENERGY = "Energy"
    SPACE = "Space"
    TIME = "Time"


class EntityType(str, Enum):
    """BFO / OntoClean Entity Classification Types."""

    INDEPENDENT_CONTINUANT = "IndependentContinuant"
    RELATIVE_ROLE = "RelativeRole"


@dataclass
class DecisionSupportQuestion:
    """High-level business concern mapped to NPV / decision support value."""

    vague_business_concern: str
    granular_dsq: str
    target_value_driver: str = "Supply Chain Risk Mitigation"


@dataclass
class CompetencyQuestion:
    """Pedantic drill-down question surfacing specific technical entities."""

    cq_id: str
    question_text: str
    derived_classes: list[str] = field(default_factory=list)
    sme_validated: bool = False


@dataclass
class PMESTFacets:
    """PMEST Faceted Analysis Container."""

    personality: list[str] = field(default_factory=list)  # Core identity (e.g. Folic Acid, Rice Plant)
    matter: list[str] = field(default_factory=list)       # Substances, properties (e.g. Nitrogen)
    energy: list[str] = field(default_factory=list)       # Operations, processes (e.g. Manufacturing)
    space: list[str] = field(default_factory=list)        # Spatial dimensions (e.g. Uruguay, Factory Floor)
    time: list[str] = field(default_factory=list)         # Temporal dimensions (e.g. 2024 Harvest)


@dataclass
class OntoCleanPartition:
    """OntoClean Independent vs Role Entity Partitioning with Opaque IRIs."""

    entity_name: str
    opaque_iri: str                                       # e.g. USO_000123
    entity_type: EntityType                               # INDEPENDENT_CONTINUANT vs RELATIVE_ROLE
    natural_language_definition: str
    context_role_assigned: str | None = None


@dataclass
class CommonLogicEcho:
    """Common Logic Echo Dialogue string for human-machine validation."""

    formula_representation: str
    natural_language_echo: str


class KnowledgeElicitationPipeline:
    """Pipeline orchestrating end-to-end Knowledge Elicitation."""

    def __init__(self, prefix: str = "USO") -> None:
        self.prefix = prefix
        self.iri_counter = 1000
        self.dsqs: list[DecisionSupportQuestion] = []
        self.cqs: list[CompetencyQuestion] = []
        self.pmest = PMESTFacets()
        self.partitions: list[OntoCleanPartition] = []

    def generate_opaque_iri(self) -> str:
        """Generate an opaque IRI (e.g. USO_001001)."""
        self.iri_counter += 1
        return f"{self.prefix}_{self.iri_counter:06d}"

    def add_dsq(self, vague_concern: str, granular_dsq: str) -> DecisionSupportQuestion:
        """Stage 1: Add a Decision Support Question (DSQ)."""
        dsq = DecisionSupportQuestion(vague_business_concern=vague_concern, granular_dsq=granular_dsq)
        self.dsqs.append(dsq)
        logger.info("Added DSQ: %s -> %s", vague_concern, granular_dsq)
        return dsq

    def analyze_pmest(
        self,
        personality: list[str],
        matter: list[str],
        energy: list[str],
        space: list[str],
        time: list[str],
    ) -> PMESTFacets:
        """Stage 2: Idea Plane PMEST Faceted Analysis."""
        self.pmest = PMESTFacets(
            personality=personality,
            matter=matter,
            energy=energy,
            space=space,
            time=time,
        )
        logger.info("Analyzed PMEST Facets: %d Personality, %d Matter", len(personality), len(matter))
        return self.pmest

    def derive_cq(self, cq_id: str, question: str, classes: list[str]) -> CompetencyQuestion:
        """Stage 3: Derive a pedantic Competency Question (CQ)."""
        cq = CompetencyQuestion(cq_id=cq_id, question_text=question, derived_classes=classes, sme_validated=True)
        self.cqs.append(cq)
        logger.info("Derived CQ [%s]: %s", cq_id, question)
        return cq

    def partition_entity(
        self,
        name: str,
        entity_type: EntityType,
        definition: str,
        role: str | None = None,
    ) -> OntoCleanPartition:
        """Stage 4: Partition into Independent Thing vs Extrinsic Role with Opaque IRI."""
        iri = self.generate_opaque_iri()
        partition = OntoCleanPartition(
            entity_name=name,
            opaque_iri=iri,
            entity_type=entity_type,
            natural_language_definition=definition,
            context_role_assigned=role,
        )
        self.partitions.append(partition)
        logger.info("Partitioned Entity '%s' -> IRI %s (%s)", name, iri, entity_type.value)
        return partition

    def generate_echo_dialogue(self, partition: OntoCleanPartition) -> CommonLogicEcho:
        """Stage 5: Generate Common Logic Echo Dialogue for Human-Machine confirmation."""
        if partition.entity_type == EntityType.RELATIVE_ROLE:
            formula = f"(forall (x) (if ({partition.entity_name} x) (exists (c) (playsRole x {partition.context_role_assigned} c))))"
            echo = f"Is '{partition.entity_name}' an extrinsic role played by an independent entity within context '{partition.context_role_assigned}'?"
        else:
            formula = f"(forall (x) (if ({partition.entity_name} x) (IndependentContinuant x)))"
            echo = f"Is '{partition.entity_name}' an independent entity defined strictly by its intrinsic structure?"

        return CommonLogicEcho(formula_representation=formula, natural_language_echo=echo)

    def extract_formal_triples(self) -> list[OntologyTriple]:
        """Stage 6: Extract BFO/CCO/IOF-aligned formal OntologyTriples."""
        triples: list[OntologyTriple] = []
        for p in self.partitions:
            # Type classification triple
            triples.append(
                OntologyTriple(
                    subject=p.opaque_iri,
                    predicate="rdf:type",
                    object=f"bfo:{p.entity_type.value}",
                    confidence=1.0,
                )
            )
            # Label triple
            triples.append(
                OntologyTriple(
                    subject=p.opaque_iri,
                    predicate="rdfs:label",
                    object=p.entity_name,
                    confidence=1.0,
                )
            )
            # Definition triple
            triples.append(
                OntologyTriple(
                    subject=p.opaque_iri,
                    predicate="skos:definition",
                    object=p.natural_language_definition,
                    confidence=1.0,
                )
            )
        return triples

    def execute_pipeline(
        self,
        executive_prompt: str,
        dsq_texts: list[str],
        cq_texts: list[str],
    ) -> ElicitationReport:
        """Run full 6-stage pipeline from executive prompt to formal triples."""
        for text in dsq_texts:
            self.add_dsq(vague_concern=executive_prompt, granular_dsq=text)

        for idx, text in enumerate(cq_texts, 1):
            self.derive_cq(cq_id=f"CQ_{idx}", question=text, classes=["SupplyChainEntity"])

        p1 = self.partition_entity(
            name="FolicAcidSupplier",
            entity_type=EntityType.INDEPENDENT_CONTINUANT,
            definition="An independent chemical entity supplier",
        )
        echo = self.generate_echo_dialogue(p1)
        triples = self.extract_formal_triples()

        return ElicitationReport(
            triples=triples,
            common_logic_echoes=[echo],
        )


@dataclass
class ElicitationReport:
    """Report holding pipeline output triples and common logic echoes."""

    triples: list[OntologyTriple] = field(default_factory=list)
    common_logic_echoes: list[CommonLogicEcho] = field(default_factory=list)
