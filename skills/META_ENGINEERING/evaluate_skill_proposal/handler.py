"""
evaluate_skill_proposal.py — Python Extraction Engine (META_ENGINEERING)

Consumes a skill proposal and emits a structured blueprint by querying
the Prolog taxonomy ontology.  Falls back to a built-in mapping when
PySWIP / SWI-Prolog is not available at runtime so the skill never fails.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ==========================================================================
#  Built-in fallback ontology (mirrors skill_taxonomy.pl)
#  Used only when Prolog surface is unavailable.
# ==========================================================================

_FALLBACK_TAXONOMY: Dict[str, Any] = {
    "professions": [
        "data_scientist", "medical_entomologist", "software_engineer",
        "epidemiologist", "statistician", "quantitative_analyst",
        "financial_modeler", "ml_researcher", "nlp_engineer",
        "operations_researcher", "clinical_researcher", "biostatistician",
        "forensic_economist", "research_scientist",
    ],
    "domains": [
        "statistics", "stochastic_processes", "optimization",
        "machine_learning", "ensemble_methods", "feature_engineering",
        "model_validation", "distributed_systems", "general_tooling",
        "epidemiology", "clinical_trials", "forensic_economics",
        "technical_analysis", "time_series", "nlp", "knowledge_graph",
        "simulation", "resource_management", "ml_operations", "risk_modeling",
    ],
    "domain_references": {
        "statistics": [
            "Wackerly - Mathematical Statistics with Applications",
            "Ross - Introduction to Probability Models",
        ],
        "stochastic_processes": [
            "Ross - Introduction to Probability Models",
            "Norris - Markov Chains",
        ],
        "optimization": [
            "Nocedal & Wright - Numerical Optimization",
            "Glover & Laguna - Tabu Search",
        ],
        "machine_learning": [
            "Hastie, Tibshirani & Friedman - The Elements of Statistical Learning",
            "Bishop - Pattern Recognition and Machine Learning",
            "Sutton & Barto - Reinforcement Learning: An Introduction",
        ],
        "distributed_systems": [
            "Lamport - Time, Clocks, and the Ordering of Events",
            "Kleppmann - Designing Data-Intensive Applications",
        ],
        "epidemiology": [
            "Keeling & Rohani - Modeling Infectious Diseases in Humans and Animals",
        ],
        "clinical_trials": [
            "ICH E9 - Statistical Principles for Clinical Trials",
            "FDA 21 CFR 50 - Informed Consent",
        ],
        "technical_analysis": [
            "Murphy - Technical Analysis of the Financial Markets",
        ],
        "time_series": [
            "Brockwell & Davis - Time Series: Theory and Methods",
        ],
        "nlp": [
            "Manning & Schütze - Foundations of Statistical NLP",
        ],
        "knowledge_graph": [
            "Hogan et al. - Knowledge Graphs (ACM Computing Surveys)",
        ],
        "simulation": [
            "Law & Kelton - Simulation Modeling and Analysis",
        ],
        "resource_management": [
            "Hillier & Lieberman - Introduction to Operations Research",
        ],
        "forensic_economics": [
            "Fisher & Waters - Regression Analysis with IBM SPSS",
        ],
    },
    "keyword_profession_map": {
        "data_scientist": [
            "data", "science", "statistics", "stochastic", "model", "ml",
            "machine_learning", "regression", "classification", "bayesian",
            "inference",
        ],
        "statistician": [
            "statistician", "hypothesis", "p_value", "confidence_interval",
            "chi_square", "anova", "test", "sampling", "distribution",
        ],
        "software_engineer": [
            "software", "engineering", "distributed", "system", "api",
            "lsp", "wasm", "compile", "deploy", "orchestrate",
        ],
        "medical_entomologist": [
            "entomology", "insect", "vector", "mosquito", "habitat",
            "incidence", "field_surveillance",
        ],
        "ml_researcher": [
            "neural", "deep_learning", "gnn", "transformer", "reinforcement",
            "q_learning", "random_forest", "decision_tree", "svm", "ensemble",
        ],
        "nlp_engineer": [
            "nlp", "language", "sentiment", "text", "token", "ngram",
            "rag", "embedding", "llm",
        ],
        "operations_researcher": [
            "optimize", "scheduling", "resource", "allocation", "lp",
            "constraint", "evolutionary", "optimizer", "search",
        ],
        "clinical_researcher": [
            "clinical", "trial", "endpoint", "dmc", "sae", "icf",
            "non_inferiority", "ctcae", "meddra",
        ],
        "epidemiologist": [
            "epidemiology", "infectious", "seir", "disease", "transmission",
            "outbreak",
        ],
        "quantitative_analyst": [
            "quantitative", "trading", "candlestick", "arfima", "hurst",
            "technical", "market", "forensics",
        ],
        "forensic_economist": [
            "forensic", "damages", "earnings", "counterfactual",
            "econometric", "regression",
        ],
        "research_scientist": [
            "research", "science", "simulation", "knowledge_graph",
            "markov", "monte_carlo", "discovery",
        ],
    },
    "subskill_trees": {
        "calculating_descriptive_stats": [
            "calculate_central_tendency", "calculate_dispersion",
        ],
        "assert_test_constraints": [
            "evaluate_p_value", "execute_chi_square_independence",
        ],
        "modelling_stochastic_processes": [
            "evaluate_stationarity", "generate_transition_matrix",
            "execute_monte_carlo_walk", "calculate_pagerank_vector",
            "compile_simulation_histogram",
        ],
        "running_optimizers": [
            "cma_es_optimizer", "differential_evolution_solver",
            "chaos_optimization", "dialectic_search",
        ],
        "building_classifiers": [
            "logistic_regression_classifier", "svm_classifier",
            "naive_bayes_classifier", "decision_tree_splits",
            "random_forest_ensemble",
        ],
        "building_distributed_infrastructure": [
            "dag_task_scheduler", "durable_execution_engine",
            "wasm_execution_sandbox", "observability_dashboard",
        ],
        "managing_clinical_trials": [
            "icf_clause_validator", "sae_reporting_threshold_tester",
            "non_inferiority_margin_checker",
        ],
        "processing_natural_language": [
            "js_text_transformer", "sentiment_intelligence_engine",
            "natural_language_generator",
        ],
    },
    "meta_wrappers": {
        "evaluate_p_value":             "assert_test_constraints",
        "execute_chi_square_independence": "assert_test_constraints",
        "calculate_central_tendency":  "validate_measurement_level",
        "calculate_dispersion":        "validate_measurement_level",
        "k_means_clustering":          "sap_endpoint_consistency_checker",
        "durable_execution_engine":    "dag_task_scheduler",
        "time_series_forecaster":      "forecasting_monitor",
        "wasm_execution_sandbox":      "container_executor",
    },
}


# ==========================================================================
#  Input / Output dataclasses
# ==========================================================================

@dataclass
class SkillBlueprint:
    """Structured output of evaluate_skill_proposal."""
    proposed_name: str
    proposed_description: str
    professions: List[str] = field(default_factory=list)
    core_domains: List[str] = field(default_factory=list)
    core_references: List[str] = field(default_factory=list)
    meta_skills_required: List[str] = field(default_factory=list)
    suggested_subskills: List[str] = field(default_factory=list)
    skill_ancestry: List[str] = field(default_factory=list)
    confidence: str = "low"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ==========================================================================
#  Prolog interface
# ==========================================================================

class PrologTaxonomyEngine:
    """Queries the Prolog ontology file for taxonomy lookups.

    Requires SWI-Prolog and PySWIP to be installed.  Falls back silently
    to the built-in taxonomy so callers never need to branch.
    """

    ONTOLOGY_PATH = str(
        Path(__file__).resolve().parent.parent.parent
        / "META_ENGINEERING"
        / "skill-taxonomy"
        / "skill_taxonomy.pl"
    )

    def __init__(self) -> None:
        self._available: bool = False
        self._prolog: Any = None
        self._try_connect()

    def _try_connect(self) -> None:
        try:
            from pyswip import Prolog  # type: ignore[import]
            self._prolog = Prolog()
            self._available = True
            logger.info("PrologTaxonomyEngine connected to PySWIP")
        except (ImportError, Exception) as exc:
            logger.warning("PrologTaxonomyEngine unavailable: %s", exc)
            self._available = False

    def consult_ontology(self) -> bool:
        if not self._available or self._prolog is None:
            return False
        try:
            if not Path(self.ONTOLOGY_PATH).exists():
                logger.error("Ontology file not found: %s", self.ONTOLOGY_PATH)
                return False
            self._prolog.consult(self.ONTOLOGY_PATH)
            logger.info("Ontology loaded: %s", self.ONTOLOGY_PATH)
            return True
        except Exception as exc:
            logger.error("Failed to consult ontology: %s", exc)
            self._available = False
            return False

    def query(self, prolog_goal: str) -> List[Dict[str, Any]]:
        if not self._available or self._prolog is None:
            return []
        try:
            return list(self._prolog.query(prolog_goal))
        except Exception as exc:
            logger.debug("Prolog query failed: %s — %s", prolog_goal, exc)
            return []

    def single(self, prolog_goal: str) -> Optional[Dict[str, Any]]:
        results = self.query(prolog_goal)
        return results[0] if results else None


# ==========================================================================
#  Extraction engine
# ==========================================================================

class SkillExtractionEngine:
    """Maps a raw skill proposal to a validated SkillBlueprint.

    Query order:
      1. Normalise and tokenise the proposal.
      2. Infer candidate professions via keyword heuristic.
      3. Ground professions in Prolog ontology (or fallback).
      4. Resolve subskills, meta-wrappers, and references.
      5. Assemble and return the blueprint.
    """

    def __init__(self, prolog_engine: Optional[PrologTaxonomyEngine] = None) -> None:
        self.prolog = prolog_engine or PrologTaxonomyEngine()
        self._ontology_loaded = self.prolog.consult_ontology()

    # ------------------------------------------------------------------
    #  Public entry point
    # ------------------------------------------------------------------

    def evaluate(self, proposed_name: str, proposed_description: str) -> SkillBlueprint:
        name = proposed_name.strip()
        desc = proposed_description.strip().lower()
        tokens = self._tokenise(desc)

        professions = self._infer_professions(tokens)
        domains = self._resolve_domains(professions)
        references = self._resolve_references(professions, domains)
        subskills = self._infer_subskills(name, desc, professions)
        meta_wrappers = self._resolve_meta_wrappers(subskills)
        ancestry = self._build_ancestry(name, subskills, professions)
        confidence = self._confidence_level(professions, references, meta_wrappers)

        return SkillBlueprint(
            proposed_name=name,
            proposed_description=proposed_description,
            professions=professions,
            core_domains=domains,
            core_references=references,
            meta_skills_required=meta_wrappers,
            suggested_subskills=subskills,
            skill_ancestry=ancestry,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    #  Tokenisation
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenise(text: str) -> List[str]:
        return [t for t in re.split(r"[\s_,;:./()-]+", text.lower()) if t]

    # ------------------------------------------------------------------
    #  Profession inference
    # ------------------------------------------------------------------

    def _infer_professions(self, tokens: List[str]) -> List[str]:
        if self._ontology_loaded:
            token_str = "[" + ",".join(tokens) + "]"
            result = self.prolog.query(
                f"infer_professions_from_keywords({token_str}, Professions)"
            )
            if result and "Professions" in result[0]:
                raw = result[0]["Professions"]
                if isinstance(raw, list):
                    return [str(p) for p in raw]

        matched: List[str] = []
        seen: set = set()
        for prof, keywords in _FALLBACK_TAXONOMY["keyword_profession_map"].items():
            for tok in tokens:
                if tok in keywords and prof not in seen:
                    matched.append(prof)
                    seen.add(prof)
                    break
        return matched

    # ------------------------------------------------------------------
    #  Domain resolution
    # ------------------------------------------------------------------

    def _resolve_domains(self, professions: List[str]) -> List[str]:
        if not professions:
            return []

        if self._ontology_loaded:
            domains: List[str] = []
            seen: set = set()
            for prof in professions:
                result = self.prolog.query(f"profession_domain({prof}, D)")
                for row in result:
                    d = str(row.get("D", ""))
                    if d and d not in seen:
                        domains.append(d)
                        seen.add(d)
            return domains

        _FALLBACK_DOMAINS = {
            "data_scientist":     ["statistics", "stochastic_processes", "optimization"],
            "statistician":       ["statistics"],
            "software_engineer":  ["distributed_systems", "general_tooling"],
            "epidemiologist":     ["epidemiology"],
            "clinical_researcher":["clinical_trials", "statistics"],
            "biostatistician":    ["clinical_trials", "statistics"],
            "ml_researcher":      ["machine_learning", "ensemble_methods",
                                   "feature_engineering", "model_validation"],
            "nlp_engineer":       ["nlp"],
            "operations_researcher": ["optimization", "resource_management"],
            "medical_entomologist":  ["epidemiology", "stochastic_processes"],
            "quantitative_analyst":  ["technical_analysis", "statistics", "time_series"],
            "financial_modeler":     ["technical_analysis", "risk_modeling"],
            "forensic_economist":    ["forensic_economics"],
            "research_scientist":    ["knowledge_graph", "simulation"],
        }
        domains = []
        seen = set()
        for prof in professions:
            for d in _FALLBACK_DOMAINS.get(prof, []):
                if d not in seen:
                    domains.append(d)
                    seen.add(d)
        return domains

    # ------------------------------------------------------------------
    #  Reference resolution
    # ------------------------------------------------------------------

    def _resolve_references(
        self, professions: List[str], domains: List[str]
    ) -> List[str]:
        seen: set = set()
        refs: List[str] = []

        if self._ontology_loaded:
            for domain in domains:
                result = self.prolog.query(
                    f"domain_reference({domain}, Ref)"
                )
                for row in result:
                    r = str(row.get("Ref", "")).strip('"')
                    if r and r not in seen:
                        refs.append(r)
                        seen.add(r)
            return refs

        for domain in domains:
            for r in _FALLBACK_TAXONOMY["domain_references"].get(domain, []):
                if r not in seen:
                    refs.append(r)
                    seen.add(r)
        return refs

    # ------------------------------------------------------------------
    #  Subskill inference
    # ------------------------------------------------------------------

    def _infer_subskills(
        self, name: str, desc: str, professions: List[str]
    ) -> List[str]:
        subskills: List[str] = []
        seen: set = set()

        if self._ontology_loaded:
            result = self.prolog.query(
                f"resolve_skill_ancestry({name}, Ancestry)"
            )
            for row in result:
                a = str(row.get("Ancestry", ""))
                if a and a not in seen:
                    subskills.append(a)
                    seen.add(a)

        tokens = set(self._tokenise(desc + " " + name))
        for tree, children in _FALLBACK_TAXONOMY["subskill_trees"].items():
            tree_tokens = set(tree.replace("_", " ").split())
            if tokens & tree_tokens:
                for child in children:
                    if child not in seen:
                        subskills.append(child)
                        seen.add(child)
        return subskills

    # ------------------------------------------------------------------
    #  Meta-wrapper resolution
    # ------------------------------------------------------------------

    def _resolve_meta_wrappers(self, subskills: List[str]) -> List[str]:
        wrappers: List[str] = []
        seen: set = set()

        if self._ontology_loaded:
            for sk in subskills:
                result = self.prolog.query(
                    f"requires_meta_wrapper({sk}, Meta)"
                )
                for row in result:
                    m = str(row.get("Meta", ""))
                    if m and m not in seen:
                        wrappers.append(m)
                        seen.add(m)
            return wrappers

        for sk in subskills:
            m = _FALLBACK_TAXONOMY["meta_wrappers"].get(sk)
            if m and m not in seen:
                wrappers.append(m)
                seen.add(m)
        return wrappers

    # ------------------------------------------------------------------
    #  Ancestry chain
    # ------------------------------------------------------------------

    def _build_ancestry(
        self,
        name: str,
        subskills: List[str],
        professions: List[str],
    ) -> List[str]:
        chain: List[str] = []
        if professions:
            chain.append(f"profession:{professions[0]}")
        for sk in subskills[:5]:
            chain.append(f"subskill:{sk}")
        chain.append(f"root:{name}")
        return chain

    # ------------------------------------------------------------------
    #  Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def _confidence_level(
        professions: List[str],
        references: List[str],
        meta_wrappers: List[str],
    ) -> str:
        score = 0
        if professions:
            score += 1
        if references:
            score += 1
        if meta_wrappers:
            score += 1
        if score >= 3:
            return "high"
        if score >= 2:
            return "medium"
        return "low"


# ==========================================================================
#  Entry-point function
# ==========================================================================

def evaluate_skill_proposal(
    proposed_name: str,
    proposed_description: str,
    *,
    prolog_engine: Optional[PrologTaxonomyEngine] = None,
) -> Dict[str, Any]:
    """Evaluate a skill proposal and return the blueprint as a plain dict."""
    engine = SkillExtractionEngine(prolog_engine=prolog_engine)
    blueprint = engine.evaluate(proposed_name, proposed_description)
    return blueprint.to_dict()


# ==========================================================================
#  CLI shim
# ==========================================================================

if __name__ == "__main__":
    import sys

    name = sys.argv[1] if len(sys.argv) > 1 else "unknown_skill"
    desc = sys.argv[2] if len(sys.argv) > 2 else ""

    result = evaluate_skill_proposal(name, desc)
    print(json.dumps(result, indent=2))
