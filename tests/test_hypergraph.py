"""Comprehensive unit test suite for Wolfram-inspired Pragmatic Hypergraph module."""

import pytest

from em_cubed.hypergraph import (
    CausalDAG,
    CompactionPipeline,
    Hyperedge,
    HypergraphStore,
    hyperedge_jaccard,
    identify_pivot_points,
    jaccard_similarity,
    overlap_coefficient,
    store_jaccard_similarity,
)


class TestPhase1Hyperedges:
    """Test Phase 1: N-ary Hyperedge creation, indexing, serialization."""

    def test_hyperedge_creation_and_hashing(self) -> None:
        edge = Hyperedge(
            edge_id="treaty_01",
            member_entities={"UKR", "POL", "USA", "NATO_Art5"},
            metadata={"trust_score": 0.85, "region": "Eastern Europe"},
        )
        assert edge.edge_id == "treaty_01"
        assert len(edge.member_entities) == 4
        assert "UKR" in edge.member_entities
        assert edge.metadata["trust_score"] == 0.85

        h1 = edge.compute_hash()
        assert len(h1) == 64  # SHA-256 hex digest length

        # Serialization roundtrip
        dict_rep = edge.to_dict()
        reconstructed = Hyperedge.from_dict(dict_rep)
        assert reconstructed.edge_id == edge.edge_id
        assert reconstructed.member_entities == edge.member_entities
        assert reconstructed.compute_hash() == h1

    def test_hypergraph_store_indexing_and_queries(self) -> None:
        store = HypergraphStore()
        edge1 = Hyperedge(
            edge_id="edge_1",
            member_entities={"UKR", "POL", "USA"},
            metadata={"type": "military_aid"},
        )
        edge2 = Hyperedge(
            edge_id="edge_2",
            member_entities={"UKR", "DEU", "FRA"},
            metadata={"type": "humanitarian_aid"},
        )
        edge3 = Hyperedge(
            edge_id="edge_3",
            member_entities={"USA", "TWN", "JPN"},
            metadata={"type": "military_aid"},
        )

        store.add_edge(edge1)
        store.add_edge(edge2)
        store.add_edge(edge3)

        assert len(store) == 3
        assert store.all_entities() == {"UKR", "POL", "USA", "DEU", "FRA", "TWN", "JPN"}

        # Single entity lookup
        ukr_edges = store.get_edges_for_entity("UKR")
        assert len(ukr_edges) == 2
        assert {e.edge_id for e in ukr_edges} == {"edge_1", "edge_2"}

        # Multi-entity intersection lookup
        usa_ukr_edges = store.query_by_intersection({"USA", "UKR"})
        assert len(usa_ukr_edges) == 1
        assert list(usa_ukr_edges)[0].edge_id == "edge_1"

        # Metadata query
        military_edges = store.query_by_metadata("type", "military_aid")
        assert len(military_edges) == 2
        assert {e.edge_id for e in military_edges} == {"edge_1", "edge_3"}

        # Store serialization roundtrip
        store_dict = store.to_dict()
        reconstructed_store = HypergraphStore.from_dict(store_dict)
        assert len(reconstructed_store) == 3
        assert reconstructed_store.all_entities() == store.all_entities()

        # Removal cleanup
        store.remove_edge("edge_1")
        assert len(store) == 2
        assert len(store.get_edges_for_entity("POL")) == 0


class TestPhase2Compaction:
    """Test Phase 2: Deterministic Compaction Pipelines."""

    def test_consolidate_shared_entities(self) -> None:
        store = HypergraphStore()
        edge1 = Hyperedge(
            edge_id="edge_1",
            member_entities={"UKR", "POL", "USA", "Tank_Supply"},
            metadata={"session": "s1"},
        )
        edge2 = Hyperedge(
            edge_id="edge_2",
            member_entities={"UKR", "POL", "USA", "Fighter_Jets"},
            metadata={"session": "s1"},
        )
        store.add_edge(edge1)
        store.add_edge(edge2)

        consolidated = CompactionPipeline.consolidate_shared_entities(
            store=store,
            shared_entities={"UKR", "POL", "USA"},
            new_edge_id="consolidated_aid_pack",
            new_metadata={"summary": "Merged Air and Armor Aid"},
        )

        assert consolidated is not None
        assert consolidated.edge_id == "consolidated_aid_pack"
        assert consolidated.member_entities == {
            "UKR",
            "POL",
            "USA",
            "Tank_Supply",
            "Fighter_Jets",
        }
        assert len(store) == 1
        assert store.get_edge("edge_1") is None
        assert store.get_edge("edge_2") is None

    def test_bounded_local_compaction(self) -> None:
        store = HypergraphStore()
        store.add_edge(Hyperedge("e1", {"A", "B"}))
        store.add_edge(Hyperedge("e2", {"B", "C"}))
        store.add_edge(Hyperedge("e3", {"C", "D"}))
        store.add_edge(Hyperedge("e4", {"D", "E"}))

        # 1-hop from A should reach B and C (via e1 and e2)
        hop1 = CompactionPipeline.bounded_local_compaction(store, {"A"}, max_hops=1)
        assert hop1 == {"A", "B"}

        hop2 = CompactionPipeline.bounded_local_compaction(store, {"A"}, max_hops=2)
        assert hop2 == {"A", "B", "C"}

    def test_prune_subsumed_edges(self) -> None:
        store = HypergraphStore()
        store.add_edge(Hyperedge("sub", {"A", "B"}))
        store.add_edge(Hyperedge("sup", {"A", "B", "C", "D"}))

        pruned = CompactionPipeline.prune_subsumed_edges(store)
        assert pruned == 1
        assert len(store) == 1
        assert store.get_edge("sub") is None
        assert store.get_edge("sup") is not None


class TestPhase3CausalDAG:
    """Test Phase 3: Append-Only Causal DAG for Auditability."""

    def test_causal_dag_append_and_integrity(self) -> None:
        dag = CausalDAG()

        n1 = dag.record_mutation(
            mutation_type="INGEST_OSINT",
            payload={"source": "url1", "trust": 0.9},
            node_id="root_1",
        )
        assert n1.node_id == "root_1"
        assert len(n1.state_hash) == 64

        n2 = dag.record_mutation(
            mutation_type="COMPACT_SCENARIO",
            payload={"merged_count": 2},
            parent_ids=["root_1"],
            node_id="step_2",
        )
        assert n2.parent_ids == ["root_1"]

        assert dag.verify_integrity() is True
        assert len(dag) == 2

        # Trace provenance
        provenance = dag.trace_provenance("step_2")
        assert len(provenance) == 2
        assert [p.node_id for p in provenance] == ["root_1", "step_2"]

        # Serialization roundtrip
        dag_dict = dag.to_dict()
        reconstructed_dag = CausalDAG.from_dict(dag_dict)
        assert reconstructed_dag.verify_integrity() is True
        assert len(reconstructed_dag) == 2

    def test_invalid_parent_raises(self) -> None:
        dag = CausalDAG()
        with pytest.raises(ValueError, match="does not exist"):
            dag.record_mutation(
                mutation_type="TEST", payload={}, parent_ids=["nonexistent"]
            )


class TestPhase4Metrics:
    """Test Phase 4: Branchial & Topological Metrics."""

    def test_set_similarity_metrics(self) -> None:
        set_a = {"UKR", "POL", "USA", "NATO"}
        set_b = {"UKR", "POL", "DEU", "FRA"}

        jaccard = jaccard_similarity(set_a, set_b)
        assert round(jaccard, 4) == round(2 / 6, 4)  # Intersection={"UKR", "POL"} (2), Union=6

        overlap = overlap_coefficient(set_a, set_b)
        assert round(overlap, 4) == round(2 / 4, 4)  # min len = 4

    def test_hyperedge_and_store_jaccard(self) -> None:
        e1 = Hyperedge("e1", {"A", "B", "C"})
        e2 = Hyperedge("e2", {"B", "C", "D"})
        assert round(hyperedge_jaccard(e1, e2), 4) == round(2 / 4, 4)

        store1 = HypergraphStore()
        store1.add_edge(e1)

        store2 = HypergraphStore()
        store2.add_edge(e2)

        assert round(store_jaccard_similarity(store1, store2), 4) == round(2 / 4, 4)

    def test_pivot_point_identification(self) -> None:
        dag_a = CausalDAG()
        dag_b = CausalDAG()

        # Shared root node
        dag_a.record_mutation("INIT", {"state": 0}, node_id="init_node")
        dag_b.record_mutation("INIT", {"state": 0}, node_id="init_node")

        # Divergent node with same node_id but different payload
        dag_a.record_mutation(
            "DECISION", {"choice": "OPTION_A"}, parent_ids=["init_node"], node_id="dec_node"
        )
        dag_b.record_mutation(
            "DECISION", {"choice": "OPTION_B"}, parent_ids=["init_node"], node_id="dec_node"
        )

        pivots = identify_pivot_points(dag_a, dag_b)
        assert len(pivots) == 1
        assert pivots[0]["node_id"] == "dec_node"
        assert "payload_mismatch" in pivots[0]["reasons"]
