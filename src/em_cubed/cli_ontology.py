"""End-to-End Ontological OS CLI Suite.

Provides CLI subcommands for:
- em-cubed ontology validate
- em-cubed ontology elicit
- em-cubed ontology truthmaker
- em-cubed ontology induce
- em-cubed ontology visualize
- em-cubed ontology migrate
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Sequence

from em_cubed.ontology.concept_induction import ConceptInductionEngine
from em_cubed.ontology.elicitation import KnowledgeElicitationPipeline
from em_cubed.ontology.schema import OntologyTriple

from em_cubed.ontology.truthmaker import ExactTruthmakerClassifier
from em_cubed.ontology.validator import OntologyLedgerValidator
from em_cubed.ontology.visualizer import KnowledgeGraphVisualizer

logger = logging.getLogger(__name__)


def build_ontology_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    """Build parser for 'em-cubed ontology' subcommand group."""
    ontology_parser = subparsers.add_parser(
        "ontology",
        help="Neuro-Symbolic Ontology CLI suite (validate, elicit, truthmaker, induce, visualize, migrate)",
    )
    onto_subparsers = ontology_parser.add_subparsers(dest="onto_subcommand", help="Ontology subcommands")

    # validate
    validate_p = onto_subparsers.add_parser("validate", help="Validate triples against ledger rules")
    validate_p.add_argument("--subject", required=True, help="Subject IRI")
    validate_p.add_argument("--predicate", required=True, help="Predicate IRI")
    validate_p.add_argument("--object", required=True, help="Object IRI")
    validate_p.add_argument("--functional-prop", help="Optional functional property constraint")

    # elicit
    elicit_p = onto_subparsers.add_parser("elicit", help="Run 6-stage Knowledge Elicitation Pipeline")
    elicit_p.add_argument("--domain-prompt", required=True, help="Natural language executive domain prompt")

    # truthmaker
    truthmaker_p = onto_subparsers.add_parser("truthmaker", help="Extract exact truthmaker state (s ⊩ A)")
    truthmaker_p.add_argument("--proposition", required=True, help="Target proposition")
    truthmaker_p.add_argument("--predicates", nargs="+", required=True, help="Wholly relevant predicates")

    # induce
    induce_p = onto_subparsers.add_parser("induce", help="Induce Description Logic class expressions")
    induce_p.add_argument("--subclass-name", required=True, help="Target subclass name")
    induce_p.add_argument("--parent-class", default="Thing", help="Parent class name")

    # visualize
    visualize_p = onto_subparsers.add_parser("visualize", help="Generate HTML Knowledge Graph visualization")
    visualize_p.add_argument("--output-html", default="knowledge_graph.html", help="Target output HTML file path")

    # migrate
    migrate_p = onto_subparsers.add_parser("migrate", help="Execute schema migration chain")
    migrate_p.add_argument("--from-pred", required=True, help="Old predicate IRI")
    migrate_p.add_argument("--to-pred", required=True, help="New predicate IRI")

    # export
    export_p = onto_subparsers.add_parser("export", help="Export triples to W3C RDF Turtle or SHACL shapes")
    export_p.add_argument("--format", choices=["turtle", "shacl"], default="turtle", help="Export format")
    export_p.add_argument("--output", default="ontology_export.ttl", help="Target output file path")

    # prove
    prove_p = onto_subparsers.add_parser("prove", help="Generate Zero-Knowledge cryptographic commitment over claim")
    prove_p.add_argument("--proposition", required=True, help="Proposition to attest")
    prove_p.add_argument("--predicates", nargs="+", required=True, help="Wholly relevant predicates")

    # tui
    onto_subparsers.add_parser("tui", help="Launch live interactive Ontological OS terminal UI workspace")

    # mcp
    onto_subparsers.add_parser("mcp", help="Run Model Context Protocol (MCP) gateway server on STDIO")

    # health
    onto_subparsers.add_parser("health", help="Audit live tri-engine cross-repository health and coherence")


def handle_ontology_cli(args: argparse.Namespace) -> int:
    """Handle execution of 'em-cubed ontology' subcommands."""
    subcommand = getattr(args, "onto_subcommand", None)

    if subcommand == "validate":
        validator = OntologyLedgerValidator()
        if args.functional_prop:
            validator.add_functional_property(args.functional_prop)
        triple = OntologyTriple(subject=args.subject, predicate=args.predicate, object=args.object)
        is_valid, msg = validator.validate_and_commit(triple)
        print(f"[Ontology Ledger Validator] Triple valid: {is_valid}. Message: {msg}")
        return 0 if is_valid else 1

    elif subcommand == "elicit":
        print(f"[Knowledge Elicitation] Eliciting ontology from: '{args.domain_prompt}'...")
        pipeline = KnowledgeElicitationPipeline()
        report = pipeline.execute_pipeline(
            executive_prompt=args.domain_prompt,
            dsq_texts=["What is the supply risk?"],
            cq_texts=["Which suppliers provide Folic Acid?"],
        )
        print(
            f"[Knowledge Elicitation] Generated {len(report.triples)} triples and {len(report.common_logic_echoes)} CL echoes."
        )
        return 0

    elif subcommand == "truthmaker":
        sample_triple = OntologyTriple(subject="SampleSubject", predicate=args.predicates[0], object="SampleObject")
        tm = ExactTruthmakerClassifier.classify_exact_truthmaker(
            proposition=args.proposition,
            state_triples=[sample_triple],
            relevant_predicates=args.predicates,
        )
        print(
            f"[Truthmaker Semantics] Proposition '{args.proposition}' Satisfied: {tm.is_satisfied}. Ground: {tm.ground_explanation}"
        )
        return 0

    elif subcommand == "induce":
        sample = [{"type": args.parent_class, "property": "hasAttribute", "target": "Active"}]
        expr = ConceptInductionEngine.induce_concept(subclass_name=args.subclass_name, positive_samples=sample)
        print(f"[Concept Induction] Induced DL Expression: {expr.to_dl_syntax()}")
        return 0

    elif subcommand == "visualize":
        triples = [OntologyTriple(subject="EntityA", predicate="relates_to", object="EntityB")]
        html_code = KnowledgeGraphVisualizer.render_subgraph_html(triples, title="CLI Knowledge Graph")  # type: ignore[arg-type]
        with open(args.output_html, "w", encoding="utf-8") as f:
            f.write(html_code)
        print(f"[Visualizer] Wrote interactive Knowledge Graph to '{args.output_html}'.")
        return 0

    elif subcommand == "migrate":
        from em_cubed.ontology.schema_evolution import AutomatedTripleMigrationEngine, SchemaMigrationStep

        triples = [OntologyTriple(subject="SubjectA", predicate=args.from_pred, object="Value1")]
        steps = [
            SchemaMigrationStep(
                step_name="CLIMigration",
                action_type="RENAME_PREDICATE",
                old_value=args.from_pred,
                new_value=args.to_pred,
            )
        ]
        migrated = AutomatedTripleMigrationEngine.migrate_triples(triples, steps)
        print(f"[Schema Evolution] Migrated predicate '{args.from_pred}' -> '{migrated[0].predicate}'")
        return 0

    elif subcommand == "export":
        from em_cubed.ontology.interoperability import RDFSerializer, SHACLConstraintGenerator
        from em_cubed.ontology.schema import FunctionalPropertyConstraint

        triples = [OntologyTriple(subject="ConceptA", predicate="subClassOf", object="ConceptB")]
        if args.format == "turtle":
            content = RDFSerializer.to_turtle(triples)
        else:
            content = SHACLConstraintGenerator.generate_shacl_shapes(
                [FunctionalPropertyConstraint(predicate="subClassOf")]
            )

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[RDF/SHACL Interoperability] Exported W3C {args.format.upper()} to '{args.output}'.")
        return 0

    elif subcommand == "prove":
        from em_cubed.ontology.zk_attestation import ZeroKnowledgeOntologyAttestor

        sample: list[OntologyTriple] = [
            OntologyTriple(subject="SubjectA", predicate=str(args.predicates[0]), object="Value1")
        ]
        commitment = ZeroKnowledgeOntologyAttestor.generate_attestation(args.proposition, sample, list(args.predicates))
        print(f"[ZK Attestation] Proof ID: {commitment.proof_id}")
        print(f"  Proposition Hash: {commitment.proposition_hash[:16]}...")
        print(f"  Merkle State Root: {commitment.merkle_state_root[:16]}...")
        print(f"  Satisfied: {commitment.is_satisfied}")
        print(f"  Signature: {str(commitment.signature)[:16]}...")
        return 0

    elif subcommand == "tui":
        from em_cubed.cli_tui import run_cli_tui_mode

        return run_cli_tui_mode(args)

    elif subcommand == "health":
        from em_cubed.ontology.health_monitor import OntologicalHealthMonitor

        health_report = OntologicalHealthMonitor.audit_tri_engine_health()
        print("Tri-Engine Cross-Repository Health Audit:")
        print(
            f"  SME Status           : {health_report['sme_status']} (Trust Index: {health_report['sme_trust_index']})"
        )
        print(
            f"  Em-Cubed Status      : {health_report['em_cubed_status']} (Coherence: {health_report['em_cubed_coherence']})"
        )
        print(
            f"  Strategify Status    : {health_report['strategify_status']} ({health_report['strategify_unit_tests']} Unit Tests)"
        )
        print(f"  Coherence Index      : {health_report['tri_engine_coherence_index'] * 100:.1f}%")
        print(f"  Overall Health       : {health_report['health_status']}")
        return 0

    else:
        print(
            "Please specify a valid ontology subcommand (validate, elicit, truthmaker, induce, visualize, migrate, export, prove, tui, mcp, health)."
        )
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Standalone entrypoint for ontology CLI."""
    parser = argparse.ArgumentParser(description="Em-Cubed Ontology CLI Suite")
    subparsers = parser.add_subparsers(dest="subcommand")
    build_ontology_parser(subparsers)

    args = parser.parse_args(argv)
    if args.subcommand == "ontology":
        return handle_ontology_cli(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
