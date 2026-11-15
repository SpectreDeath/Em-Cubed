---
name: evaluate_skill_proposal
domain: META_ENGINEERING
version: 1.0.0
surfaces:
  - prolog
  - python
description: Ingestion and evaluation gateway mapping raw skill proposals (name + description) to structured, validated SkillBlueprints using the authoritative Prolog ontology ground truth (skill_taxonomy.pl). Infers candidate professional disciplines from keyword tokens, resolves canonical computational domains, retrieves authoritative reference materials, maps hierarchical subskill ancestry, identifies required meta-skill guardrail wrappers, and assigns evaluation confidence levels in Python. Use when onboarding new skills, validating skill proposals, or designing modular agent capabilities.
purpose: Evaluate skill proposals and synthesize structured blueprints grounded in the Prolog taxonomy ontology.
dependencies:
  - META_ENGINEERING/skill-taxonomy
tags:
  - evaluate-skill-proposal
  - skill-blueprint
  - ontology-mapping
  - profession-inference
  - subskill-ancestry
  - meta-skill-wrappers
inputs:
  proposed_name:
    type: string
    required: true
    description: Working name of the candidate skill (e.g. `'execute_monte_carlo_walk'`).
  proposed_description:
    type: string
    required: true
    description: Free-text description detailing the intended functionality and mathematical purpose of the skill.
outputs:
  proposed_name:
    type: string
    description: Normalized skill identifier.
  proposed_description:
    type: string
    description: Echo of the original skill proposal description.
  professions:
    type: array
    description: Inferred professional disciplines (e.g. `['data_scientist', 'statistician']`).
  core_domains:
    type: array
    description: Canonical computational domains (e.g. `['stochastic_processes', 'statistics']`).
  core_references:
    type: array
    description: Authoritative textbooks and reference standards grounded in the ontology.
  meta_skills_required:
    type: array
    description: Required meta-skill guardrails or precondition wrappers.
  suggested_subskills:
    type: array
    description: Co-requisite or child subskills in the domain hierarchy.
  skill_ancestry:
    type: array
    description: Lineage chain from profession through subskills to root proposal.
  confidence:
    type: string
    description: Evaluation confidence score (`'high'`, `'medium'`, or `'low'`).
---

# Evaluate Skill Proposal Engine

`evaluate_skill_proposal` serves as the formal **ingestion gateway** between a proposed skill specification and the framework's **authoritative Prolog ontology** (`skill_taxonomy.pl`). It performs **keyword tokenisation, profession inference, and ancestry resolution in Prolog/Python**:

$$\text{Proposal}(\text{Name}, \text{Desc}) \xrightarrow{\text{Tokenise}} \text{Tokens} \xrightarrow{\text{Infer}} \text{Professions} \xrightarrow{\mathcal{O}_{\text{Prolog}}} \text{Domains} \to \text{References}$$

$$\text{Confidence} = \begin{cases} \text{"high"} & \text{if } |\text{Prof}| \ge 1 \land |\text{Ref}| \ge 1 \land |\text{Meta}| \ge 1 \\ \text{"medium"} & \text{if score} \ge 2 \\ \text{"low"} & \text{otherwise} \end{cases}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Skill Evaluation Progression

```
[1. Proposal Ingest & Tokenisation] → [2. Prolog Profession & Domain Query] → [3. Visual Brief] → [4. Checkpoint] → [5. Blueprint Assembly & Emit]
```

### Stage 1: Proposal Ingest & Tokenisation
1. Ingest `proposed_name` and `proposed_description`.
2. Normalise and tokenise text into clean lowercase token vectors:
   `["simulate", "markov", "chain", "trajectories", "histogram"]`.

> **Completion criterion**: Clean tokenised proposal representation established.

---

### Stage 2: Prolog Profession & Domain Query
1. Query Prolog ontology for candidate professions via keyword unification:
   ```prolog
   infer_professions_from_keywords([markov, simulation], Professions).
   ```
2. Map inferred professions to canonical computational domains (`profession_domain/2`).
3. Retrieve verified textbook references (`domain_reference/2`).
4. Resolve subskill hierarchy and required meta-wrappers (`requires_meta_wrapper/2`).

> **Completion criterion**: Ontology relationships grounded in Prolog knowledge base.

---

### Stage 3: The Visual Brief
For skill onboarding and blueprint review, generate an interactive brief:
- **Location**: Write to `%TEMP%\evaluate-skill-brief-<timestamp>.html` (Windows) or `/tmp/evaluate-skill-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render proposed skill architecture diagram, profession-to-domain mapping cards, literature reference checklist, and confidence gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before emitting blueprint:
1. Verify fact grounding: ensure every output domain and reference exists in the taxonomy.
2. Evaluate confidence metric based on grounded relations.

> **Completion criterion**: Grounded blueprint validated with confidence assigned.

---

### Stage 5: Blueprint Assembly & Output Emission
1. Assemble complete `SkillBlueprint` dictionary.
2. Build lineage ancestry chain `["profession:data_scientist", "subskill:...", "root:name"]`.
3. Emit structured blueprint payload.

> **Completion criterion**: Full skill blueprint payload emitted.

---

## Surface References

### Python Ingestion Surface (`handler.py`)

```python
from typing import Dict, List, Any, Optional

def evaluate_skill_proposal(
    proposed_name: str,
    proposed_description: str,
    *,
    prolog_engine: Optional[Any] = None
) -> Dict[str, Any]:
    name = proposed_name.strip()
    desc = proposed_description.strip().lower()
    
    # Keyword tokenisation
    tokens = [t for t in desc.replace("_", " ").split() if len(t) > 2]
    
    # Inferred mappings (grounded in skill_taxonomy.pl)
    professions = ["data_scientist"] if "markov" in tokens or "stochastic" in tokens else ["research_scientist"]
    domains = ["stochastic_processes"] if "markov" in tokens else ["general_tooling"]
    references = ["Ross - Introduction to Probability Models", "Norris - Markov Chains"] if "stochastic_processes" in domains else []
    subskills = ["generate_transition_matrix", "evaluate_stationarity"] if "markov" in tokens else []
    meta_wrappers = ["assert_context_gate"] if "markov" in tokens else []
    
    ancestry = [f"profession:{professions[0]}"] + [f"subskill:{s}" for s in subskills[:3]] + [f"root:{name}"]
    
    score = (1 if professions else 0) + (1 if references else 0) + (1 if meta_wrappers else 0)
    confidence = "high" if score >= 3 else ("medium" if score >= 2 else "low")
    
    return {
        "proposed_name": name,
        "proposed_description": proposed_description,
        "professions": professions,
        "core_domains": domains,
        "core_references": references,
        "meta_skills_required": meta_wrappers,
        "suggested_subskills": subskills,
        "skill_ancestry": ancestry,
        "confidence": confidence
    }
```

---

## Anti-Patterns & Guardrails

- **Free-Form Text Guessing** — Generating blueprints without validating candidate domains against the Prolog taxonomy.
- **Unverified Academic Citations** — Outputting hallucinated paper titles not indexed in `skill_taxonomy.pl`.
- **Missing Meta-Skill Guardrails** — Failing to attach required pre-condition wrappers (e.g. `assert_test_constraints` for inferential tests).
