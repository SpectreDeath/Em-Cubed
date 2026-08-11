"""GEXF (Graph Exchange XML Format) Exporter for Gephi Visualization."""

from pathlib import Path
from typing import Union
import xml.etree.ElementTree as ET  # nosec B405
from xml.dom import minidom  # nosec B408

from em_cubed.hypergraph.causal_dag import CausalDAG
from em_cubed.hypergraph.store import HypergraphStore


def _pretty_xml_str(elem: ET.Element) -> str:
    """Format ElementTree element into clean, indented XML string."""
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)  # nosec B318
    return reparsed.toprettyxml(indent="  ")


def export_store_to_gexf(
    store: HypergraphStore,
    filepath: Union[str, Path],
    mode: str = "bipartite",
) -> str:
    """Export HypergraphStore to GEXF 1.2 XML for visual audit in Gephi.

    Modes:
      - "bipartite": Creates Entity nodes and Hyperedge nodes, connected by bipartite edges.
      - "clique": Creates Entity nodes with direct pairwise edges between member entities.
    """
    gexf = ET.Element(
        "gexf",
        xmlns="http://www.gexf.net/1.2draft",
        version="1.2",
    )
    meta = ET.SubElement(gexf, "meta")
    ET.SubElement(meta, "creator").text = "Em-Cubed Hypergraph Engine"
    ET.SubElement(meta, "description").text = f"Hypergraph export (mode={mode})"

    graph_type = "undirected"
    graph = ET.SubElement(gexf, "graph", mode="static", defaultedgetype=graph_type)
    nodes_elem = ET.SubElement(graph, "nodes")
    edges_elem = ET.SubElement(graph, "edges")

    edge_counter = 0

    if mode == "clique":
        # Entity nodes only
        for entity_id in store.all_entities():
            node_el = ET.SubElement(nodes_elem, "node", id=entity_id, label=entity_id)
            viz_attr = ET.SubElement(node_el, "attvalues")
            ET.SubElement(viz_attr, "attvalue", for_="type", value="entity")

        # Clique pairwise edges
        added_pairs = set()
        for hyperedge in store.all_edges():
            members = sorted(list(hyperedge.member_entities))
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    pair = (members[i], members[j])
                    if pair not in added_pairs:
                        added_pairs.add(pair)
                        edge_counter += 1
                        ET.SubElement(
                            edges_elem,
                            "edge",
                            id=f"e_{edge_counter}",
                            source=members[i],
                            target=members[j],
                            weight="1.0",
                        )

    else:  # bipartite mode
        # Entity nodes
        for entity_id in store.all_entities():
            node_el = ET.SubElement(nodes_elem, "node", id=f"ent_{entity_id}", label=entity_id)
            viz_attr = ET.SubElement(node_el, "attvalues")
            ET.SubElement(viz_attr, "attvalue", for_="node_type", value="entity")

        # Hyperedge nodes & connections
        for hyperedge in store.all_edges():
            edge_node_id = f"hedge_{hyperedge.edge_id}"
            node_el = ET.SubElement(
                nodes_elem, "node", id=edge_node_id, label=f"Hyperedge:{hyperedge.edge_id}"
            )
            viz_attr = ET.SubElement(node_el, "attvalues")
            ET.SubElement(viz_attr, "attvalue", for_="node_type", value="hyperedge")

            for member in hyperedge.member_entities:
                edge_counter += 1
                ET.SubElement(
                    edges_elem,
                    "edge",
                    id=f"e_{edge_counter}",
                    source=f"ent_{member}",
                    target=edge_node_id,
                )

    xml_str = _pretty_xml_str(gexf)
    out_path = Path(filepath)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(xml_str, encoding="utf-8")
    return xml_str


def export_dag_to_gexf(dag: CausalDAG, filepath: Union[str, Path]) -> str:
    """Export CausalDAG to GEXF 1.2 XML format for lineage visualization in Gephi."""
    gexf = ET.Element(
        "gexf",
        xmlns="http://www.gexf.net/1.2draft",
        version="1.2",
    )
    meta = ET.SubElement(gexf, "meta")
    ET.SubElement(meta, "creator").text = "Em-Cubed Causal DAG Ledger"

    graph = ET.SubElement(gexf, "graph", mode="static", defaultedgetype="directed")
    nodes_elem = ET.SubElement(graph, "nodes")
    edges_elem = ET.SubElement(graph, "edges")

    edge_counter = 0

    for node in dag.all_nodes():
        node_el = ET.SubElement(
            nodes_elem,
            "node",
            id=node.node_id,
            label=f"{node.mutation_type}:{node.node_id}",
        )
        attvalues = ET.SubElement(node_el, "attvalues")
        ET.SubElement(attvalues, "attvalue", for_="mutation_type", value=node.mutation_type)
        ET.SubElement(attvalues, "attvalue", for_="state_hash", value=node.state_hash)

        for pid in node.parent_ids:
            edge_counter += 1
            ET.SubElement(
                edges_elem,
                "edge",
                id=f"dag_e_{edge_counter}",
                source=pid,
                target=node.node_id,
            )

    xml_str = _pretty_xml_str(gexf)
    out_path = Path(filepath)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(xml_str, encoding="utf-8")
    return xml_str
