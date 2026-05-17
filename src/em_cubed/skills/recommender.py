"""Skill recommendation engine.

Analyzes task requirements, skill capabilities, and usage patterns
to recommend appropriate skills for a given problem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

import structlog

from .registry import SkillRegistry
from .semantic_search import get_semantic_search_manager

logger = structlog.get_logger()


@dataclass
class TaskRequirement:
    """A requirement for a task."""
    category: str  # e.g., "optimization", "nlp", "decision"
    surfaces: List[str] = field(default_factory=list)  # Preferred surfaces
    capabilities: List[str] = field(default_factory=list)  # Required capabilities
    complexity: str = "medium"  # low, medium, high
    expected_input_types: Dict[str, str] = field(default_factory=dict)
    expected_output_types: Dict[str, str] = field(default_factory=dict)
    max_execution_time: Optional[float] = None
    min_success_rate: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "surfaces": self.surfaces,
            "capabilities": self.capabilities,
            "complexity": self.complexity,
            "expected_input_types": self.expected_input_types,
            "expected_output_types": self.expected_output_types,
            "max_execution_time": self.max_execution_time,
            "min_success_rate": self.min_success_rate,
        }


@dataclass
class RecommendationResult:
    """A skill recommendation."""
    skill_id: str
    name: str
    relevance_score: float  # 0-1
    matching_criteria: List[str] = field(default_factory=list)
    composition_opportunities: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "relevance_score": self.relevance_score,
            "matching_criteria": self.matching_criteria,
            "composition_opportunities": self.composition_opportunities,
            "quality_metrics": self.quality_metrics,
            "reasoning": self.reasoning,
        }


class SkillRecommender:
    """Recommends skills based on task requirements."""

    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.logger = logger.bind(component="skill_recommender")
        # Initialize semantic search manager if not already initialized
        from .semantic_search import initialize_semantic_search, get_semantic_search_manager
        initialize_semantic_search(registry)
        self.semantic_search = get_semantic_search_manager()

    def recommend(self, requirement: TaskRequirement, limit: int = 5) -> List[RecommendationResult]:
        """Find skills matching the given requirements."""
        # First, get keyword-based recommendations
        candidates = self.registry.list_skills()
        scored = []

        for skill in candidates:
            if skill.skill_id is None:
                continue  # Skip skills without valid ID
            score, criteria = self._score_skill(skill, requirement)
            if score > 0:
                scored.append((score, skill, criteria))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Get semantic search enhancement if available
        semantic_results = []
        if self.semantic_search and self.semantic_search.model:
            # Create a query from the requirement
            query_parts = [
                requirement.category,
                " ".join(requirement.surfaces),
                " ".join(requirement.capabilities),
                requirement.complexity
            ]
            query = " ".join(filter(None, query_parts)).strip()
            
            if query:
                try:
                    semantic_matches = self.semantic_search.search(query, limit=limit*2)
                    # Convert to same format as keyword results
                    for skill, similarity in semantic_matches:
                        # Only add if not already in keyword results or if it has higher similarity
                        existing_scores = [s[0] for s in scored if s[1].skill_id == skill.skill_id]
                        if not existing_scores or similarity > max(existing_scores):
                            # Create criteria for semantic match
                            semantic_criteria = [f"Semantic match: {similarity:.2f}"]
                            scored.append((similarity, skill, semantic_criteria))
                except Exception as e:
                    self.logger.warning("Semantic search failed", error=str(e))

        # Re-score and re-sort with semantic results included
        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, skill, criteria in scored[:limit]:
            # Ensure skill has a valid ID (filtered earlier, but enforce for type checker)
            assert skill.skill_id is not None, "Skill ID should not be None at this point"
            # Find composition opportunities
            comp_opps = self.registry.find_compatible_skills(skill.skill_id)
            qm = self.registry.get_quality(skill.skill_id)

            result = RecommendationResult(
                skill_id=skill.skill_id,
                name=skill.name,
                relevance_score=score,
                matching_criteria=criteria,
                composition_opportunities=comp_opps[:3],
                quality_metrics=qm.to_dict() if qm else {},
                reasoning=self._generate_reasoning(skill, criteria),
            )
            results.append(result)

        return results

    def _score_skill(self, skill, requirement: TaskRequirement) -> tuple[float, List[str]]:
        """Score a skill against requirements."""
        score = 0.0
        criteria = []

        # Domain matching
        if requirement.category.lower() == skill.domain.lower():
            score += 0.4
            criteria.append(f"Domain match: {skill.domain}")

        # Surface preference
        if requirement.surfaces:
            for surface in requirement.surfaces:
                if surface in skill.surfaces:
                    score += 0.1
                    criteria.append(f"Preferred surface: {surface}")

        # Capability matching (using tags)
        if requirement.capabilities:
            for cap in requirement.capabilities:
                if cap in skill.tags:
                    score += 0.1
                    criteria.append(f"Capability match: {cap}")

        # Quality thresholds
        qm = self.registry.get_quality(skill.skill_id)
        if qm:
            if qm.success_rate >= requirement.min_success_rate:
                score += 0.2
                criteria.append(f"High success rate: {qm.success_rate:.1%}")
            else:
                # Penalize low success rate
                score -= 0.2

            # Check execution time if specified
            if requirement.max_execution_time and qm.avg_execution_time:
                if qm.avg_execution_time <= requirement.max_execution_time:
                    score += 0.1
                    criteria.append(f"Fast execution: {qm.avg_execution_time:.2f}s")
                else:
                    score -= 0.1

        # Complexity appropriateness
        complexity_weights = {"low": 0.8, "medium": 1.0, "high": 1.2}
        score *= complexity_weights.get(requirement.complexity, 1.0)

        return min(1.0, max(0.0, score)), criteria

    def _generate_reasoning(self, skill, criteria: List[str]) -> str:
        """Generate human-readable reasoning for the recommendation."""
        reasons = []
        if criteria:
            reasons.append("Matches: " + ", ".join(criteria[:3]))
        if skill.purpose:
            reasons.append(f"Purpose: {skill.purpose[:100]}")
        if skill.surfaces:
            reasons.append(f"Surfaces: {', '.join(skill.surfaces)}")
        return "; ".join(reasons)

    def recommend_chain(self, start_skill_id: str, end_skill_id: str, max_hops: int = 3) -> List[List[str]]:
        """Find skill chains between start and end skills."""
        from collections import deque

        start = self.registry.get_skill(start_skill_id)
        end = self.registry.get_skill(end_skill_id)
        if not start or not end:
            return []

        # BFS to find shortest paths
        queue = deque([(start_skill_id, [start_skill_id])])
        visited = {start_skill_id}
        paths: List[List[str]] = []

        while queue and len(paths) < 5:  # Find up to 5 paths
            current, path = queue.popleft()
            if current == end_skill_id:
                paths.append(path)
                continue
            if len(path) >= max_hops:
                continue

            # Explore neighbors (skills compatible with current)
            for neighbor in self.registry.find_compatible_skills(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return paths

    def get_similar_skills(self, skill_id: str, limit: int = 5) -> List[RecommendationResult]:
        """Find skills similar to the given skill."""
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return []

        candidates = self.registry.list_skills()
        scored = []

        for candidate in candidates:
            if candidate.skill_id is None or candidate.skill_id == skill_id:
                continue
            similarity = self._calculate_similarity(skill, candidate)
            if similarity > 0.2:
                scored.append((similarity, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, candidate in scored[:limit]:
            assert candidate.skill_id is not None, "Candidate skill ID should not be None"
            qm = self.registry.get_quality(candidate.skill_id)
            results.append(RecommendationResult(
                skill_id=candidate.skill_id,
                name=candidate.name,
                relevance_score=score,
                matching_criteria=[f"Similar to {skill.name}"],
                quality_metrics=qm.to_dict() if qm else {},
            ))

        return results

    def _calculate_similarity(self, skill1, skill2) -> float:
        """Calculate similarity between two skills."""
        score = 0.0

        # Domain similarity
        if skill1.domain == skill2.domain:
            score += 0.3

        # Surface overlap
        common_surfaces = set(skill1.surfaces) & set(skill2.surfaces)
        if common_surfaces:
            score += 0.2 * (len(common_surfaces) / max(len(skill1.surfaces), len(skill2.surfaces)))

        # Tag overlap
        common_tags = set(skill1.tags) & set(skill2.tags)
        if common_tags:
            score += 0.3 * (len(common_tags) / max(len(skill1.tags), len(skill2.tags), 1))

        # Purpose/description similarity (simple word overlap)
        if skill1.purpose and skill2.purpose:
            words1 = set(skill1.purpose.lower().split())
            words2 = set(skill2.purpose.lower().split())
            overlap = len(words1 & words2) / max(len(words1 | words2), 1)
            score += 0.2 * overlap

        return min(1.0, score)

    def get_recommendations_for_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> List[RecommendationResult]:
        """Parse task description and recommend skills (heuristic-based)."""
        # Simple keyword-based extraction from description
        keywords = self._extract_keywords(task_description)
        complexity = self._detect_complexity(task_description)

        # Determine category from domains list (first match)
        domain_list = keywords.get("domains", [])
        category = domain_list[0] if domain_list else "General"

        requirement = TaskRequirement(
            category=category,
            surfaces=keywords.get("surfaces", []),
            capabilities=keywords.get("capabilities", []),
            complexity=complexity,
        )

        return self.recommend(requirement)

    def _extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract task keywords from natural language description."""
        text_lower = text.lower()
        keywords: Dict[str, List[str]] = {"domains": [], "surfaces": [], "capabilities": []}

        # Domain keywords
        domain_keywords = {
            "nlp": ["text", "language", "nlp", "generate", "sentiment"],
            "optimization": ["optimize", "minimize", "maximize", "constraint"],
            "machine_learning": ["learn", "train", "predict", "model"],
            "decision": ["choose", "decide", "select", "multi-criteria"],
            "automation": ["automate", "workflow", "pipeline"],
        }

        for domain, terms in domain_keywords.items():
            if any(term in text_lower for term in terms):
                keywords["domains"].append(domain.upper())

        # Surface hints
        if "python" in text_lower or "code" in text_lower:
            keywords["surfaces"].append("python")
        if "logic" in text_lower or "rule" in text_lower or "prolog" in text_lower:
            keywords["surfaces"].append("prolog")
        if "fuzzy" in text_lower or "adaptive" in text_lower:
            keywords["surfaces"].append("hy")

        return keywords

    def _detect_complexity(self, text: str) -> str:
        """Detect task complexity from description."""
        text_lower = text.lower()
        if any(word in text_lower for word in ["simple", "basic", "easy"]):
            return "low"
        if any(word in text_lower for word in ["complex", "advanced", "sophisticated", "multi"]):
            return "high"
        return "medium"
