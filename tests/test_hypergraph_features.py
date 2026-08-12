"""Unit tests for GEXF exporter and SQLite persistence adapter."""

import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from em_cubed.hypergraph import (
    CausalDAG,
    Hyperedge,
    HypergraphStore,
    SQLiteHypergraphAdapter,
    export_dag_to_gexf,
    export_store_to_gexf,
)


def test_gexf_bipartite_and_clique_export():
    """Test GEXF XML export for hypergraph store in bipartite and clique modes."""
    store = HypergraphStore()
    store.add_edge(
        Hyperedge("nato_art5", {"USA", "UKR", "POL", "DEU"}, metadata={"type": "treaty"})
    )
    store.add_edge(
        Hyperedge("quad_pact", {"USA", "JPN", "AUS", "IND"}, metadata={"type": "pact"})
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        bipartite_file = Path(temp_dir) / "bipartite.gexf"
        clique_file = Path(temp_dir) / "clique.gexf"

        bipartite_xml = export_store_to_gexf(store, bipartite_file, mode="bipartite")
        clique_xml = export_store_to_gexf(store, clique_file, mode="clique")

        assert bipartite_file.exists()
        assert clique_file.exists()

        # Parse XML to verify valid schema
        tree_b = ET.fromstring(bipartite_xml)
        assert tree_b.tag.endswith("gexf")

        tree_c = ET.fromstring(clique_xml)
        assert tree_c.tag.endswith("gexf")


def test_gexf_dag_export():
    """Test GEXF XML export for CausalDAG."""
    dag = CausalDAG()
    dag.record_mutation("INIT", {"val": 1}, node_id="n1")
    dag.record_mutation("STEP", {"val": 2}, parent_ids=["n1"], node_id="n2")

    with tempfile.TemporaryDirectory() as temp_dir:
        dag_file = Path(temp_dir) / "dag.gexf"
        xml_content = export_dag_to_gexf(dag, dag_file)

        assert dag_file.exists()
        tree = ET.fromstring(xml_content)
        assert tree.tag.endswith("gexf")


def test_sqlite_persistence_adapter():
    """Test SQLite persistence adapter for store and CausalDAG save/load."""
    store = HypergraphStore()
    store.add_edge(Hyperedge("edge_1", {"A", "B", "C"}, metadata={"score": 0.9}))
    store.add_edge(Hyperedge("edge_2", {"B", "C", "D"}, metadata={"score": 0.8}))

    dag = CausalDAG()
    dag.record_mutation("EVENT_1", {"data": "alpha"}, node_id="node_a")
    dag.record_mutation("EVENT_2", {"data": "beta"}, parent_ids=["node_a"], node_id="node_b")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "hypergraph.db"
        adapter = SQLiteHypergraphAdapter(db_path)

        # Save store and DAG
        adapter.save_store(store)
        adapter.save_dag(dag)

        # Load store and DAG
        loaded_store = adapter.load_store()
        loaded_dag = adapter.load_dag()

        # Verify store integrity
        assert len(loaded_store) == 2
        assert loaded_store.all_entities() == {"A", "B", "C", "D"}
        e1 = loaded_store.get_edge("edge_1")
        assert e1 is not None
        assert e1.metadata["score"] == 0.9

        # Verify DAG integrity
        assert len(loaded_dag) == 2
        assert loaded_dag.verify_integrity() is True
        provenance = loaded_dag.trace_provenance("node_b")
        assert len(provenance) == 2
        assert provenance[0].node_id == "node_a"
