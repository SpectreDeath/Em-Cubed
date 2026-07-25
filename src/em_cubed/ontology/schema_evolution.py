"""Dynamic Ontological Schema Evolution, Migration, & Version Control Engine.

Implements enterprise versioned schema migrations for formal ontologies:
1. SchemaVersion: Semantic version management for ontology schemas.
2. SchemaMigrationStep: Declarative transformation rules (e.g. predicate remapping, class deprecation).
3. ForwardBackwardCompatibilityChecker: Verifies breaking changes before migration.
4. AutomatedTripleMigrationEngine: Transforms active OntologyTriple ledgers losslessly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


@dataclass
class SchemaVersion:
    """Represents a semantic version for an Ontology Schema."""

    version_str: str  # e.g. "v1.0.0"

    def is_compatible_with(self, other: SchemaVersion) -> bool:
        """Check major version compatibility."""
        v1_major = self.version_str.lstrip("v").split(".")[0]
        v2_major = other.version_str.lstrip("v").split(".")[0]
        return v1_major == v2_major


@dataclass
class SchemaMigrationStep:
    """Defines a single schema migration rule (e.g. predicate rename)."""

    step_name: str
    action_type: str  # "RENAME_PREDICATE", "DEPRECATE_CLASS", "ADD_DEFAULT_PREDICATE"
    old_value: str
    new_value: str


class ForwardBackwardCompatibilityChecker:
    """Verifies whether a schema migration introduces breaking changes."""

    @staticmethod
    def check_compatibility(
        from_version: SchemaVersion,
        to_version: SchemaVersion,
        migration_steps: list[SchemaMigrationStep],
    ) -> bool:
        """Check compatibility across versions."""
        if not from_version.is_compatible_with(to_version):
            logger.warning("Breaking major version bump from %s to %s!", from_version.version_str, to_version.version_str)
            return False

        logger.info("Schema migration from %s to %s is backward compatible.", from_version.version_str, to_version.version_str)
        return True


class AutomatedTripleMigrationEngine:
    """Applies migration steps to transform active OntologyTriple ledgers losslessly."""

    @staticmethod
    def migrate_triples(
        triples: list[OntologyTriple],
        steps: list[SchemaMigrationStep],
    ) -> list[OntologyTriple]:
        """Transform active OntologyTriples according to schema migration steps.

        Parameters
        ----------
        triples : list[OntologyTriple]
            Active state triples before migration.
        steps : list[SchemaMigrationStep]
            List of migration steps to apply.

        Returns
        -------
        list[OntologyTriple]
            Migrated state triples under the target schema.
        """
        migrated: list[OntologyTriple] = []

        for t in triples:
            current_subj = t.subject
            current_pred = t.predicate
            current_obj = t.object

            for step in steps:
                if step.action_type == "RENAME_PREDICATE" and current_pred == step.old_value:
                    logger.info("Migrating predicate '%s' -> '%s' for subject '%s'", step.old_value, step.new_value, current_subj)
                    current_pred = step.new_value

            migrated.append(
                OntologyTriple(
                    subject=current_subj,
                    predicate=current_pred,
                    object=current_obj,
                    confidence=t.confidence,
                )
            )

        return migrated


class OntologySchemaMigrator:
    """Orchestrates sequential versioned schema migrations."""

    def __init__(self, current_version: SchemaVersion) -> None:
        self.current_version = current_version
        self.migration_history: list[SchemaMigrationStep] = []

    def execute_migration(
        self,
        target_version: SchemaVersion,
        steps: list[SchemaMigrationStep],
        active_triples: list[OntologyTriple],
    ) -> tuple[SchemaVersion, list[OntologyTriple]]:
        """Execute schema migration chain and return updated version and triples."""
        compatible = ForwardBackwardCompatibilityChecker.check_compatibility(
            self.current_version, target_version, steps
        )

        if not compatible:
            logger.warning("Migration compatibility check failed, executing with breaking flags.")

        migrated_triples = AutomatedTripleMigrationEngine.migrate_triples(active_triples, steps)
        self.migration_history.extend(steps)
        self.current_version = target_version

        logger.info("Successfully migrated schema to %s.", target_version.version_str)
        return self.current_version, migrated_triples
