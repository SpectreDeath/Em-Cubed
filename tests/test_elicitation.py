"""Unit tests for KnowledgeElicitationPipeline (PMEST, OntoClean, CQs, Common Logic Echoes)."""

from em_cubed.ontology.elicitation import EntityType, KnowledgeElicitationPipeline


def test_knowledge_elicitation_pipeline_full_workflow():
    pipeline = KnowledgeElicitationPipeline(prefix="USO")

    # Stage 1: DSQ
    dsq = pipeline.add_dsq(
        vague_concern="Supply Chain Compliance",
        granular_dsq="What is the compliance status of each primary manufacturer in the global supply chain?",
    )
    assert dsq.vague_business_concern == "Supply Chain Compliance"
    assert len(pipeline.dsqs) == 1

    # Stage 2: PMEST Analysis
    pmest = pipeline.analyze_pmest(
        personality=["Folic Acid", "Rice Plant"],
        matter=["Nitrogen", "Molecular Weight"],
        energy=["Manufacturing", "Diagnostic Testing"],
        space=["Uruguay", "China"],
        time=["2024 Rainy Season"],
    )
    assert len(pmest.personality) == 2
    assert len(pmest.matter) == 2

    # Stage 3: CQ Derivation
    cq = pipeline.derive_cq(
        cq_id="CQ_01",
        question="Does origin refer to harvest location or chemical synthesis location?",
        classes=["HarvestOrigin", "SynthesisLocation"],
    )
    assert cq.cq_id == "CQ_01"
    assert cq.sme_validated is True

    # Stage 4: OntoClean Partition
    p_ind = pipeline.partition_entity(
        name="Folic Acid",
        entity_type=EntityType.INDEPENDENT_CONTINUANT,
        definition="A synthetic B vitamin.",
    )
    p_role = pipeline.partition_entity(
        name="Regulated Product",
        entity_type=EntityType.RELATIVE_ROLE,
        definition="A product under regulatory oversight.",
        role="Uruguayan Regulatory Framework",
    )

    assert p_ind.opaque_iri.startswith("USO_")
    assert p_role.entity_type == EntityType.RELATIVE_ROLE

    # Stage 5: Common Logic Echo Dialogue
    echo_ind = pipeline.generate_echo_dialogue(p_ind)
    echo_role = pipeline.generate_echo_dialogue(p_role)

    assert "independent entity" in echo_ind.natural_language_echo
    assert "extrinsic role" in echo_role.natural_language_echo

    # Stage 6: Extraction of Formal Triples
    triples = pipeline.extract_formal_triples()
    assert len(triples) == 6  # 3 triples per partition (type, label, definition)
    assert any(t.predicate == "rdf:type" and "bfo:IndependentContinuant" in t.object for t in triples)
