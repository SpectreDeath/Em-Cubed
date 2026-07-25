# Architectural Specification: Ontological Core Engine (`Em-Cubed`)

## Executive Summary

`Em-Cubed` is a production-grade **Neuro-Symbolic Ontological Operating System & Polyglot Skill Engine**. 

While AI agent architectures often treat memory as a loose collection of unstructured vector embeddings or Pydantic JSON schemas, `Em-Cubed` grounds agent behavior in a formal **Neuro-Symbolic Ontology Ledger**. 

The fundamental thesis of the platform is: **"Pydantic at the door, Ontology at the ledger."**

---

## Architectural Taxonomy & Core Subsystems

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             EM-CUBED ONTOLOGICAL OS                              │
├──────────────────────────┬──────────────────────────┬────────────────────────────┤
│ 1. KNOWLEDGE ELICITATION │ 2. ONTOLOGY LEDGER       │ 3. REASONING COPROCESSORS  │
│    PIPELINE              │    & TRUTH CLASSIFIER    │    & LOOPY SKILLS          │
├──────────────────────────┼──────────────────────────┼────────────────────────────┤
│ • DSQ Value Scoping      │ • OntologyLedgerValidator│ • SurfaceMorphism          │
│ • PMEST Faceted Analysis │ • Topos Subobject        │   (Pydantic/Prolog/Z3/Datalog)│
│ • DSQ-to-CQ Loop         │   Classifier (Omega)     │ • BaseLoopySkill Engine    │
│ • OntoClean BFO          │ • GraphPathRAG           │ • SkillEvolutionEngine     │
│   Independent vs Role    │ • Multi-Agent Consensus  │ • TrajectoryAuditor        │
└──────────────────────────┴──────────────────────────┴────────────────────────────┘
```

---

## 1. The Knowledge Elicitation Pipeline (`em_cubed.ontology.elicitation`)

Transforms expert natural language and transcripts into formal BFO/OntoClean ontologies:
- **Decision Support Questions (DSQs)**: Connect executive business concerns directly to NPV optimization and risk mitigation.
- **PMEST Faceted Analysis**: Ranganathan multi-dimensional classification separating **[P]ersonality**, **[M]atter**, **[E]nergy**, **[S]pace**, and **[T]ime**.
- **Competency Questions (CQs)**: Pedantic drill-down questions eliminating logical debt.
- **OntoClean & BFO Partitioning**: Distinguishes **Independent Continuants** (intrinsic structure) from **Relative Roles** (extrinsic context), assigning machine-readable opaque IRIs (`USO_001001`).
- **Common Logic Echoes**: Human-machine dialogue confirmation strings.

---

## 2. The Ontology Ledger & Truth Classifier (`em_cubed.ontology`)

- **`OntologyLedgerValidator`**: Blocks illegal state mutations by enforcing OWL functional property uniqueness, class disjointness, and domain/range inferences.
- **`SubobjectClassifier` & `TruthValue` ($\Omega$)**: Topos Category Theory classifier extending truth evaluation from binary $\{0, 1\}$ to continuous confidence $[0.0 \dots 1.0]$, modal necessity ($\Box$), and temporal step windows.
- **`GraphPathRAG`**: Multi-hop semantic triple traversal $(S \xrightarrow{P} O \xrightarrow{P'} O')$, replacing hallucination-prone vector search with 100% auditable knowledge paths.
- **`ConstraintSteeringCompiler`**: Compiles formal OWL constraints into prompt steering masks and Pydantic validators for LLMs.

---

## 3. Polyglot Coprocessors & Loopy Skill Engine (`em_cubed.surfaces` & `em_cubed.loopy`)

- **`SurfaceMorphism`**: Lossless categorical mappings translating schemas across Python, Prolog facts, Z3 SMT assertions, and Datalog rules.
- **`BaseLoopySkill`**: Stateful, self-correcting sub-routines with trajectory logging and default `OntologyLedgerValidator` integration.
- **`SkillEvolutionEngine`**: Analyzes historical `AuditReport` proof traces to synthesize preventative prompt steering rules and eliminate retries on subsequent runs.
- **`FederatedOntologyRegistry`**: Synchronizes semantic triples across multi-agent swarms with SHA-256 state integrity verification.

---

## Conclusion

By anchoring all reasoning surfaces, loopy skills, and agent swarms to a formal ontological ledger, `Em-Cubed` provides unmatched determinism, auditability, and safety for enterprise neuro-symbolic AI applications.
