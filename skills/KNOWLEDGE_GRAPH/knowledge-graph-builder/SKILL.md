---
Domain: KNOWLEDGE_GRAPH
Version: 1.0.0
Complexity: High
Type: Process
Category: Cognitive Skills
Estimated Execution Time: 5-10 minutes
name: knowledge-graph-builder
Source: community
---
origin: manual
triggers:
  - knowledge_management
  - graph_construction
  - entity_extraction
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:30:00Z"
updated_at: "2026-05-02T12:30:00Z"

## Purpose

Multi-surface knowledge graph builder that uses Python for entity extraction and graph algorithms, Prolog for logical relationship inference, and Datalog for recursive knowledge discovery.

## Description

This skill constructs knowledge graphs by:
- Python for NLP entity extraction, embedding computation, and graph analysis
- Prolog for deductive reasoning and logical relationship discovery
- Datalog for recursive pattern matching and transitive knowledge inference

## Examples

### Document Knowledge Extraction

```
Input: Technical documents and their relationships
Output: Knowledge graph with entities, relationships, and inferred facts
```

## Implementation

### Python Entity Extraction

```python
import spacy
from typing import Dict, List, Tuple, Set, Any
from collections import defaultdict
import numpy as np
from dataclasses import dataclass

@dataclass
class Entity:
    id: str
    type: str
    text: str
    confidence: float
    embeddings: np.ndarray = None

@dataclass
class Relationship:
    source: str
    target: str
    type: str
    confidence: float
    evidence: List[str] = None

class KnowledgeGraphBuilder:
    """Build knowledge graphs from text."""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.node_embeddings: Dict[str, np.ndarray] = {}
    
    def extract_entities(self, text: str, nlp) -> List[Entity]:
        """Extract entities using spaCy NER."""
        doc = nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity = Entity(
                id=f"{ent.text}_{ent.label_}",
                type=ent.label_,
                text=ent.text,
                confidence=getattr(ent._, "confidence", 1.0)
            )
            entities.append(entity)
            self.entities[entity.id] = entity
        
        return entities
    
    def extract_relationships(self, text: str) -> List[Relationship]:
        """Extract relationships using dependency parsing."""
        doc = nlp(text)
        relationships = []
        
        for token in doc:
            if token.dep_ in ("nsubj", "dobj") and token.head.pos_ == "VERB":
                # Subject-verb-object relationship
                subj = token
                obj = [child for child in token.head.children if child.dep_ == "dobj"]
                
                if obj:
                    rel = Relationship(
                        source=subj.text,
                        target=obj[0].text,
                        type=token.head.lemma_,
                        confidence=0.8,
                        evidence=[sent.text for sent in doc.sents]
                    )
                    relationships.append(rel)
        
        self.relationships.extend(relationships)
        return relationships
    
    def compute_embeddings(self, texts: List[str], model) -> Dict[str, np.ndarray]:
        """Compute embeddings for entities."""
        import torch
        
        embeddings = {}
        for text in texts:
            inputs = model.tokenizer(text, return_tensors="pt", truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)
            embeddings[text] = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        
        return embeddings
    
    def cluster_entities(self, threshold: float = 0.8) -> Dict[str, List[str]]:
        """Cluster similar entities based on embeddings."""
        clusters = defaultdict(list)
        
        for entity_id, embedding in self.node_embeddings.items():
            found_cluster = False
            for cluster_id, cluster_embs in clusters.items():
                centroid = np.mean([self.node_embeddings[e] for e in cluster_embs], axis=0)
                similarity = np.dot(embedding, centroid) / (np.linalg.norm(embedding) * np.linalg.norm(centroid))
                if similarity > threshold:
                    clusters[cluster_id].append(entity_id)
                    found_cluster = True
                    break
            
            if not found_cluster:
                clusters[entity_id].append(entity_id)
        
        return dict(clusters)

def graph_metrics(graph: Dict[str, List[str]]) -> Dict[str, float]:
    """Calculate knowledge graph metrics."""
    nodes = set(graph.keys())
    for neighbors in graph.values():
        nodes.update(neighbors)
    
    edges = sum(len(v) for v in graph.values())
    density = edges / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
    
    # Degree distribution
    degrees = [len(graph.get(n, [])) for n in nodes]
    avg_degree = np.mean(degrees) if degrees else 0
    
    return {
        "nodes": len(nodes),
        "edges": edges,
        "density": density,
        "avg_degree": avg_degree
    }
```

### Prolog Logical Inference

```prolog
% Knowledge graph rules
related(Entity1, Entity2, Relationship) :-
    triple(Entity1, Relationship, Entity2).

transitive_relationship(Entity1, Entity3, Path) :-
    related(Entity1, Entity2, Rel1),
    related(Entity2, Entity3, Rel2),
    Path = [Rel1, Rel2].

% Type hierarchy inference
subtype(Type1, Type2) :-
    type_hierarchy(Type1, Type2).

subtype(Type1, Type3) :-
    type_hierarchy(Type1, Type2),
    subtype(Type2, Type3).

% Entity type validation
valid_entity(Entity, Type, Graph) :-
    member(triple(Entity, instance_of, Type), Graph),
    type_constraints(Type, Constraints),
    satisfies_constraints(Entity, Constraints, Graph).

% Contradiction detection
contradiction_exists(Graph) :-
    member(triple(S, P, O1), Graph),
    member(triple(S, P, O2), Graph),
    O1 \= O2,
    conflicting_predicates(P).

% Common neighbors
common_neighbors(Entity1, Entity2, Neighbors) :-
    findall(N, (triple(N, _, Entity1), triple(N, _, Entity2)), Neighbors).

% Knowledge completion
inferred_triple(Subject, Predicate, Object) :-
    triple(Subject, PartOfPredicate, Intermediate),
    triple(Intermediate, RestOfPredicate, Object),
    atomic_list_concat([PartOfPredicate, RestOfPredicate], '_', Predicate).
```

### Datalog Knowledge Discovery

```datalog
% Transitive relationships
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).

% Entity type inference
entity_type(E, T) :- type(E, T).
entity_type(E, super_type) :- entity_type(E, T), subtype(T, super_type).

% Co-occurrence patterns
frequently_cooccur(E1, E2) :-
    cooccur(E1, E2, Count),
    Count > 5.

% Knowledge graph completion
likely_relationship(S, P, O) :-
    embedding_similarity(S, O, Similarity),
    Similarity > 0.8.

% Community detection
same_community(E1, E2) :-
    community(E1, C1),
    community(E2, C2),
    C1 = C2.
```

## Testing

```python
# Test entity extraction
from skills.knowledge_graph_builder import KnowledgeGraphBuilder, Entity

kg = KnowledgeGraphBuilder()
entities = kg.extract_entities("Apple Inc. was founded by Steve Jobs in California.", nlp)
assert len(entities) >= 2
assert "Apple Inc." in [e.text for e in entities]
```