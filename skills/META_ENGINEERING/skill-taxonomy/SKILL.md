---
name: skill-taxonomy
domain: META_ENGINEERING
version: 1.0.0
surfaces:
  - prolog
description: Declarative Prolog ontology ground truth defining the foundational taxonomy for the Em-Cubed skill framework. Encodes bidirectional relationships between 14 professional disciplines, 20 canonical computational domains, authoritative academic literature references, subskill hierarchical dependency trees, and required meta-skill wrapper contracts in Prolog. Use when resolving skill ancestry, validating domain classifications, mapping professional skill trees, or querying reference materials.
purpose: Serve as the authoritative Prolog ontology ground truth for professions, domains, references, and subskill dependency trees.
dependencies: []
tags:
  - skill-taxonomy
  - prolog-ontology
  - knowledge-graph
  - professional-taxonomy
  - literature-grounding
  - subskill-trees
inputs:
  query_type:
    type: string
    required: true
    description: Ontology query predicate (`'profession_domain'`, `'recommend_materials'`, `'resolve_skill_ancestry'`, `'infer_professions'`, or `'get_domain_skills'`).
  parameters:
    type: array
    required: true
    description: Query argument parameters (e.g. `['data_scientist']` or `['execute_monte_carlo_walk']`).
outputs:
  results:
    type: array
    description: List of matched ontology facts or inferred relations from Prolog.
  query_status:
    type: string
    description: Query execution status (`'success'`, `'unmatched'`, or `'error'`).
  ancestry_tree:
    type: object
    description: Hierarchical ancestry structure if querying skill dependencies.
---

# Skill Taxonomy Ontology Engine

`skill-taxonomy` serves as the authoritative, declarative **Prolog ontology ground truth** (`skill_taxonomy.pl`) for the entire Em-Cubed multi-agent ecosystem. It defines many-to-many relationships across **14 professions**, **20 canonical domains**, **authoritative textbooks**, and **subskill dependency hierarchies**:

$$\text{Profession} \xrightarrow{\text{many-to-many}} \text{Domain} \xrightarrow{\text{1-to-many}} \text{Literature Reference}$$

$$\text{Skill} \xrightarrow{\text{subskill\_of}} \text{Parent Skill} \xrightarrow{\text{wraps}} \text{Meta-Skill}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Taxonomy Query Progression

```
[1. Query Ingest & Predicate Audit] → [2. Prolog Goal Construction] → [3. Visual Brief] → [4. Checkpoint] → [5. Knowledge Resolution & Emit]
```

### Stage 1: Query Ingest & Predicate Audit
1. Ingest `query_type` and argument `parameters`.
2. Validate that predicate belongs to supported ontology query interfaces:
   - `profession_domain/2`
   - `domain_reference/2`
   - `belongs_to_profession/2`
   - `requires_meta_wrapper/2`
   - `resolve_skill_ancestry/2`
   - `infer_professions_from_keywords/2`
   - `get_domain_skills/2`

> **Completion criterion**: Valid ontology query predicate verified.

---

### Stage 2: Prolog Goal Construction & Execution
1. Construct normalized Prolog goal string:
   `?- resolve_skill_ancestry(execute_monte_carlo_walk, Ancestry).`
2. Consult `skill_taxonomy.pl` and execute goal against SWI-Prolog engine.

> **Completion criterion**: Unification solutions resolved from Prolog knowledge base.

---

### Stage 3: The Visual Brief
For ontology exploration and professional skill trees, generate an interactive brief:
- **Location**: Write to `%TEMP%\skill-taxonomy-brief-<timestamp>.html` (Windows) or `/tmp/skill-taxonomy-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render profession-to-domain graph, literature reference mapping table, and hierarchical subskill dependency tree.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before emitting results:
1. Verify fact grounding: ensure all matched terms exist in the ontology (no hallucinated relationships).
2. If Prolog is unavailable or predicate has no matches, fall back deterministically to built-in taxonomy mapping.

> **Completion criterion**: Grounded facts verified or fallback engaged.

---

### Stage 5: Knowledge Resolution & Output Emission
1. Format query results into structured list or tree dictionary.
2. Emit complete `TaxonomyQueryResult` record.

> **Completion criterion**: Full taxonomy resolution payload emitted.

---

## Surface References

### Prolog Ontology Surface (`skill_taxonomy.pl`)

```prolog
:- module(skill_taxonomy, [
    profession_domain/2,
    domain_reference/2,
    belongs_to_profession/2,
    requires_meta_wrapper/2,
    has_subskill/2,
    recommend_materials/2,
    resolve_skill_ancestry/2,
    infer_professions_from_keywords/2,
    get_domain_skills/2
]).

% Professions and Domains
profession_domain(data_scientist, statistics).
profession_domain(data_scientist, stochastic_processes).
profession_domain(data_scientist, optimization).
profession_domain(software_engineer, distributed_systems).
profession_domain(epidemiologist, epidemiology).
profession_domain(clinical_researcher, clinical_trials).

% Literature References
domain_reference(statistics, "Wackerly - Mathematical Statistics with Applications").
domain_reference(stochastic_processes, "Norris - Markov Chains").
domain_reference(optimization, "Nocedal & Wright - Numerical Optimization").

% Subskill Hierarchy
has_subskill(modelling_stochastic_processes, generate_transition_matrix).
has_subskill(modelling_stochastic_processes, execute_monte_carlo_walk).
has_subskill(modelling_stochastic_processes, evaluate_stationarity).

% Meta-wrappers
requires_meta_wrapper(evaluate_p_value, assert_test_constraints).
requires_meta_wrapper(calculate_central_tendency, validate_measurement_level).
```

---

## Anti-Patterns & Guardrails

- **Un-Grounded Taxonomy Terms** — Inventing arbitrary domains or professions not present in `skill_taxonomy.pl`.
- **Cyclic Subskill Dependencies** — Defining parent-child subskill loops ($A \text{ subskill of } B \text{ subskill of } A$).
- **Missing Literature Grounding** — Proposing canonical computational domains without linking verified authoritative textbooks.
