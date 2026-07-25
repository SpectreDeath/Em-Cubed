"""Unit tests for Dynamic Ontological Schema Evolution & Migration Engine."""

from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.schema_evolution import (
    AutomatedTripleMigrationEngine,
    ForwardBackwardCompatibilityChecker,
    OntologySchemaMigrator,
    SchemaMigrationStep,
    SchemaVersion,
)


def test_schema_version_compatibility():
    v1 = SchemaVersion("v1.0.0")
    v1_1 = SchemaVersion("v1.1.0")
    v2 = SchemaVersion("v2.0.0")

    assert v1.is_compatible_with(v1_1) is True
    assert v1.is_compatible_with(v2) is False

    step = SchemaMigrationStep(
        step_name="RenameOrigin",
        action_type="RENAME_PREDICATE",
        old_value="has_origin",
        new_value="has_country_of_origin",
    )
    compat = ForwardBackwardCompatibilityChecker.check_compatibility(v1, v1_1, [step])
    assert compat is True


def test_automated_triple_migration_engine():
    triples = [
        OntologyTriple(subject="USO_100", predicate="has_origin", object="Uruguay"),
        OntologyTriple(subject="USO_100", predicate="has_weight", object="500kg"),
    ]

    steps = [
        SchemaMigrationStep(
            step_name="RenameOrigin",
            action_type="RENAME_PREDICATE",
            old_value="has_origin",
            new_value="has_country_of_origin",
        )
    ]

    migrated = AutomatedTripleMigrationEngine.migrate_triples(triples, steps)
    assert len(migrated) == 2
    assert migrated[0].predicate == "has_country_of_origin"
    assert migrated[0].object == "Uruguay"
    assert migrated[1].predicate == "has_weight"


def test_ontology_schema_migrator_orchestration():
    v1 = SchemaVersion("v1.0.0")
    target_v = SchemaVersion("v1.1.0")

    migrator = OntologySchemaMigrator(current_version=v1)

    triples = [
        OntologyTriple(subject="Asset_1", predicate="has_origin", object="Brazil"),
    ]

    steps = [
        SchemaMigrationStep(
            step_name="RenameOrigin",
            action_type="RENAME_PREDICATE",
            old_value="has_origin",
            new_value="has_country_of_origin",
        )
    ]

    new_ver, migrated = migrator.execute_migration(target_v, steps, triples)
    assert new_ver.version_str == "v1.1.0"
    assert migrated[0].predicate == "has_country_of_origin"
    assert len(migrator.migration_history) == 1
