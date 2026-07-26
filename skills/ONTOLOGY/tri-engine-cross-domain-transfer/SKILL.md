---
name: tri-engine-cross-domain-transfer
description: Maps domain concept taxonomies across biodefense, geopolitical crisis, supply chain, and financial audit domains using BFO upper-level categories.
---

# Tri-Engine Cross-Domain Knowledge Transfer Skill (`tri-engine-cross-domain-transfer`)

This skill enables cross-domain concept mapping and rule transfer between distinct domain silos (e.g. biodefense, geopolitics, supply chain, financial audit) via BFO top-level categories.

---

## 💻 Programmatic Usage Example

```python
from em_cubed.ontology.cross_domain_transfer import CrossDomainKnowledgeTransferEngine
from em_cubed.ontology.schema import OntologyTriple

# 1. Map concept taxonomies
mapping = CrossDomainKnowledgeTransferEngine.map_concept(
    source_domain="Biodefense",
    target_domain="Geopolitics",
    source_concept="PathogenVariant",
    target_concept="StateActor",
)

print(f"Alignment Confidence: {mapping.alignment_confidence}")
print(f"BFO Upper Category  : {mapping.bfo_upper_category}")

# 2. Transfer triples
triples = [OntologyTriple(subject="PathogenVariant_X", predicate="causes", object="OutbreakEvent_01")]
transferred = CrossDomainKnowledgeTransferEngine.transfer_triples(
    triples,
    {"PathogenVariant_X": "StateActor_Alpha", "causes": "initiates", "OutbreakEvent_01": "MilitarySkirmish_01"},
)
print("Transferred Triple:", transferred[0].to_dict())
```
