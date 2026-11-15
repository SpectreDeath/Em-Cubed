# Skill Summary Card: `evaluate_skill_proposal`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        evaluate_skill_proposal                   │
│ Category:    META_ENGINEERING / Skill Onboarding       │
│ Invocation:  /evaluate_skill_proposal                  │
│ Trigger:     "evaluate skill proposal", "skill blueprint│
│              "onboard skill", "map skill taxonomy",    │
│              "infer profession", "skill ancestry"      │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Evaluate raw skill proposals against the  │
│              Prolog ontology to generate validated     │
│              SkillBlueprints with references & wrappers│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest proposal name & description text | Proposal Text AST | Non-empty text verified |
| **2. Prolog Query**| Infer professions & query domains in Prolog | Grounded Fact Record | Valid relations extracted |
| **3. Visual Brief** | Render blueprint card & literature checklist | `%TEMP%\evaluate-skill-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate fact grounding & confidence score | Blueprint Gate Record | Confidence computed |
| **5. Model Emission**| Assemble `SkillBlueprint` & emit JSON payload | `SkillBlueprint` Payload | Full blueprint payload emitted |

---

## Invariants & Guardrails

- [ ] **Ontology Fact Grounding**: All domains and references must match `skill_taxonomy.pl`.
- [ ] **Deterministic Fallback**: Built-in mapping executes if PySWIP is unavailable.
- [ ] **Confidence Level**: Scale strictly bounded to `high`, `medium`, or `low`.
