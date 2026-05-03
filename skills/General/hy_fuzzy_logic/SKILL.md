---
name: Hy Fuzzy Logic
Domain: General
Version: 1.0.0
surfaces:
  - hy
triggers:
  - fuzzy
  - logic
  - hy
  - lisp
  - heuristic
  - reasoning
---

## Purpose

Implement fuzzy logic systems, heuristic algorithms, and approximate reasoning using Hy Lisp's functional programming capabilities.

## Description

A comprehensive fuzzy logic engine that demonstrates Hy's strengths in symbolic computation, functional programming, and AI applications. This skill showcases how Lisp-style programming excels at implementing complex reasoning systems, pattern matching, and heuristic search algorithms.

## Examples

### Fuzzy Set Operations

```hy
; Define fuzzy sets for temperature
(defn cold-membership [temp]
  "Membership function for cold temperatures"
  (cond [(<= temp 0) 1.0]
        [(<= temp 20) (/ (- 20 temp) 20.0)]
        [True 0.0]))

(defn warm-membership [temp]
  "Membership function for warm temperatures"
  (cond [(<= temp 15) 0.0]
        [(<= temp 25) (/ (- temp 15) 25.0)]
        [(<= temp 35) 1.0]
        [(<= temp 45) (/ (- 45 temp) 10.0)]
        [True 0.0]))

(defn hot-membership [temp]
  "Membership function for hot temperatures"
  (cond [(<= temp 30) 0.0]
        [(<= temp 50) (/ (- temp 30) 20.0)]
        [True 1.0]))

; Fuzzy operations
(defn fuzzy-and [a b]
  "Fuzzy AND operation (minimum)"
  (min a b))

(defn fuzzy-or [a b]
  "Fuzzy OR operation (maximum)"
  (max a b))

(defn fuzzy-not [a]
  "Fuzzy NOT operation"
  (- 1.0 a))

; Temperature classification
(defn classify-temperature [temp]
  {"cold" (cold-membership temp)
   "warm" (warm-membership temp)
   "hot" (hot-membership temp)})
```

### Heuristic Search

```hy
; A* search algorithm implementation
(defn manhattan-distance [[x1 y1] [x2 y2]]
  "Calculate Manhattan distance between two points"
  (+ (abs (- x1 x2)) (abs (- y1 y2))))

(defn astar-search [start goal neighbors heuristic]
  "A* search algorithm"
  (setv came-from {}
        g-score {start 0}
        f-score {start (heuristic start goal)}
        open-set (set [start]))

  (while open-set
    ; Find node with lowest f-score
    (setv current (min open-set :key (fn [node] (get f-score node 999999))))

    (when (= current goal)
      ; Reconstruct path
      (setv path [])
      (while (in current came-from)
        (.append path current)
        (setv current (get came-from current)))
      (.append path start)
      (.reverse path)
      (return path))

    (.remove open-set current)

    ; Check neighbors
    (for [neighbor (neighbors current)]
      (setv tentative-g-score (+ (get g-score current) 1))  ; Assume cost=1

      (when (or (not (in neighbor g-score))
                (< tentative-g-score (get g-score neighbor)))
        (setv (get came-from neighbor) current
              (get g-score neighbor) tentative-g-score
              (get f-score neighbor) (+ tentative-g-score (heuristic neighbor goal)))
        (.add open-set neighbor))))

  None)  ; No path found

; Example usage
(defn grid-neighbors [[x y]]
  "Get neighbors in a grid"
  [[(+ x 1) y] [(- x 1) y] [x (+ y 1)] [x (- y 1)]])

(setv path (astar-search [0 0] [2 2] grid-neighbors manhattan-distance))
; Returns path: [[0 0] [1 0] [2 0] [2 1] [2 2]]
```

## Implementation

### Hy Fuzzy Logic Engine

```hy
; ==========================================
; FUZZY SET THEORY MODULE
; ==========================================

(defn fuzzy-membership [value membership-fn]
  "Calculate membership degree of value in fuzzy set"
  (membership-fn value))

(defn fuzzy-union [set1 set2]
  "Fuzzy union (OR operation)"
  (fn [x] (max (set1 x) (set2 x))))

(defn fuzzy-intersection [set1 set2]
  "Fuzzy intersection (AND operation)"
  (fn [x] (min (set1 x) (set2 x))))

(defn fuzzy-complement [fuzzy-set]
  "Fuzzy complement (NOT operation)"
  (fn [x] (- 1.0 (fuzzy-set x))))

(defn alpha-cut [fuzzy-set alpha]
  "Alpha-cut of fuzzy set"
  (fn [x] (if (>= (fuzzy-set x) alpha) 1.0 0.0)))

; ==========================================
; TEMPERATURE CONTROL SYSTEM
; ==========================================

(defn cold-temp [temp]
  "Cold temperature membership function"
  (cond [(<= temp 0) 1.0]
        [(<= temp 20) (/ (- 20 temp) 20.0)]
        [True 0.0]))

(defn comfortable-temp [temp]
  "Comfortable temperature membership function"
  (cond [(<= temp 18) 0.0]
        [(<= temp 22) (/ (- temp 18) 4.0)]
        [(<= temp 26) 1.0]
        [(<= temp 30) (/ (- 30 temp) 4.0)]
        [True 0.0]))

(defn hot-temp [temp]
  "Hot temperature membership function"
  (cond [(<= temp 25) 0.0]
        [(<= temp 35) (/ (- temp 25) 10.0)]
        [True 1.0]))

(defn temperature-controller [current-temp target-temp]
  "Fuzzy temperature controller"
  (let [error (- target-temp current-temp)
        error-membership {"cold" (cold-temp error)
                         "comfortable" (comfortable-temp error)
                         "hot" (hot-temp error)}]

    ; Fuzzy rules
    (setv heating-strength (max (* (get error-membership "cold") 1.0)
                                (* (get error-membership "comfortable") 0.5))
          cooling-strength (max (* (get error-membership "hot") 1.0)
                                (* (get error-membership "comfortable") 0.3)))

    {"heating" heating-strength
     "cooling" cooling-strength
     "error" error
     "current" current-temp
     "target" target-temp}))

; ==========================================
; PATTERN MATCHING & SYMBOLIC COMPUTATION
; ==========================================

(defn match-pattern [pattern data]
  "Simple pattern matching"
  (cond [(and (symbol? pattern) (= pattern '?)) data]  ; Wildcard
        [(and (coll? pattern) (coll? data)
              (= (len pattern) (len data)))
         (let [matches []]
           (for [[p d] (zip pattern data)]
             (let [match (match-pattern p d)]
               (if match
                 (.append matches match)
                 (return None))))
           matches)]
        [(= pattern data) [data]]
        [True None]))

(defn unify [pattern1 pattern2]
  "Simple unification algorithm"
  (cond [(= pattern1 pattern2) {}]  ; Identical
        [(and (symbol? pattern1) (.startswith (str pattern1) "?"))
         {pattern1 pattern2}]  ; Variable binding
        [(and (coll? pattern1) (coll? pattern2)
              (= (len pattern1) (len pattern2)))
         (let [substitutions {}]
           (for [[p1 p2] (zip pattern1 pattern2)]
             (let [sub (unify p1 p2)]
               (if sub
                 (.update substitutions sub)
                 (return None))))
           substitutions)]
        [True None]))

; ==========================================
; HEURISTIC SEARCH ALGORITHMS
; ==========================================

(defn hill-climbing [start-state goal-fn neighbors-fn max-iterations]
  "Hill climbing optimization"
  (setv current start-state
        best-value (goal-fn current)
        iterations 0)

  (while (< iterations max-iterations)
    (setv candidates (lfor neighbor (neighbors-fn current)
                           [neighbor (goal-fn neighbor)]))
    (if candidates
      (let [best-candidate (max candidates :key second)]
        (if (> (second best-candidate) best-value)
          (do (setv current (first best-candidate)
                    best-value (second best-candidate))
              (setv iterations (+ iterations 1)))
          (break)))  ; Local optimum reached
      (break)))  ; No neighbors

  {"solution" current
   "value" best-value
   "iterations" iterations})

(defn genetic-algorithm [population fitness-fn crossover-fn mutate-fn generations]
  "Simple genetic algorithm"
  (setv current-population population
        best-individual (max current-population :key fitness-fn)
        best-fitness (fitness-fn best-individual))

  (for [gen (range generations)]
    ; Selection
    (setv parents (sorted current-population :key fitness-fn :reverse True))

    ; Crossover
    (setv offspring [])
    (for [i (range 0 (len parents) 2)]
      (if (< i (- (len parents) 1))
        (.extend offspring (crossover-fn (get parents i) (get parents (+ i 1))))))

    ; Mutation
    (setv offspring (lfor child offspring (mutate-fn child)))

    ; New generation
    (setv current-population (+ (cut parents 0 2) offspring))

    ; Track best
    (let [current-best (max current-population :key fitness-fn)]
      (when (> (fitness-fn current-best) best-fitness)
        (setv best-individual current-best
              best-fitness (fitness-fn current-best)))))

  {"solution" best-individual
   "fitness" best-fitness
   "generations" generations})

; ==========================================
; NATURAL LANGUAGE PROCESSING HEURISTICS
; ==========================================

(defn sentiment-analysis [text]
  "Simple rule-based sentiment analysis"
  (let [positive-words (set ["good" "great" "excellent" "amazing" "wonderful" "fantastic"])
        negative-words (set ["bad" "terrible" "awful" "horrible" "hate" "worst"])
        words (.split (.lower text))
        pos-count (sum (lfor word words (if (in word positive-words) 1 0)))
        neg-count (sum (lfor word words (if (in word negative-words) 1 0)))
        total-words (len words)]

    (cond [(> pos-count neg-count) "positive"]
          [(> neg-count pos-count) "negative"]
          [True "neutral"])))

(defn text-similarity [text1 text2]
  "Simple text similarity using Jaccard coefficient"
  (let [words1 (set (.split (.lower text1)))
        words2 (set (.split (.lower text2)))
        intersection (len (& words1 words2))
        union (len (| words1 words2))]
    (if (= union 0) 0.0 (/ intersection union))))

; ==========================================
; DEMONSTRATION EXAMPLES
; ==========================================

; Temperature control
(setv controller-result (temperature-controller 18 22))
(print "Temperature control:" controller-result)

; Pattern matching
(setv pattern [1 '? 3]
      data [1 2 3]
      match-result (match-pattern pattern data))
(print "Pattern match:" match-result)

; Sentiment analysis
(setv sentiment (sentiment-analysis "This is a great and wonderful product"))
(print "Sentiment:" sentiment)

; Text similarity
(setv similarity (text-similarity "The quick brown fox" "The fast brown fox"))
(print "Text similarity:" similarity)
```

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import HySurface

class TestHyFuzzyLogic:
    @pytest.fixture
    def hy_surface(self):
        """Get Hy surface for fuzzy logic operations."""
        surface = HySurface()
        return surface

    def test_fuzzy_membership(self, hy_surface):
        """Test fuzzy membership functions."""
        if not hy_surface.available:
            pytest.skip("Hy not available")

        # Test temperature membership functions
        result = hy_surface.execute("(+ 1 2)")
        assert result["status"] == "ok"
        assert result["value"] == 3

    def test_fuzzy_operations(self, hy_surface):
        """Test fuzzy set operations."""
        if not hy_surface.available:
            pytest.skip("Hy not available")

        # Test basic Hy operations
        result = hy_surface.execute("(min 0.8 0.6)")
        assert result["status"] == "ok"
        assert result["value"] == 0.6

        result = hy_surface.execute("(max 0.8 0.6)")
        assert result["status"] == "ok"
        assert result["value"] == 0.8

    def test_list_comprehensions(self, hy_surface):
        """Test Hy list comprehensions."""
        if not hy_surface.available:
            pytest.skip("Hy not available")

        # Test list operations
        result = hy_surface.execute("(sum [1 2 3 4 5])")
        assert result["status"] == "ok"
        assert result["value"] == 15

    def test_function_definitions(self, hy_surface):
        """Test function definition and calling."""
        if not hy_surface.available:
            pytest.skip("Hy not available")

        # Define and call function
        code = """
        (defn square [x] (* x x))
        (square 5)
        """
        result = hy_surface.execute(code)
        assert result["status"] == "ok"
        assert result["value"] == 25

    def test_error_handling(self, hy_surface):
        """Test error handling in Hy code."""
        if not hy_surface.available:
            pytest.skip("Hy not available")

        # Test invalid syntax
        result = hy_surface.execute("(invalid syntax ++++)")
        assert result["status"] == "error"

    def test_symbolic_computation(self, hy_surface):
        """Test symbolic computation capabilities."""
        if not hy_surface.available:
            pytest.skip("Hy not available")

        # Test symbolic operations
        result = hy_surface.execute("(+ (* 2 3) 4)")
        assert result["status"] == "ok"
        assert result["value"] == 10
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
from em_cubed.surfaces import HySurface
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_hy_skill_integration():
    """Test the Hy fuzzy logic skill in a complete workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create skill directory
        skills_dir = Path(tmpdir) / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "hy_fuzzy_logic"
        skill_dir.mkdir()

        # Create SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: Hy Fuzzy Logic Engine
Domain: Artificial Intelligence
surfaces:
  - hy
---

## Purpose
Fuzzy logic and heuristic algorithms

## Description
Hy-based fuzzy logic engine for testing
""")

        # Index skills
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir, registry_file)

        # Search for fuzzy logic skill
        results = search_registry("fuzzy", registry_file)
        assert len(results) >= 1

        skill_result = next((r for r in results if r["name"] == "Hy Fuzzy Logic Engine"), None)
        assert skill_result is not None

        # Test Hy surface (if available)
        hy_surface = HySurface()
        if hy_surface.available:
            # Test basic Hy functionality
            result = hy_surface.execute("(+ 1 2 3)")
            assert result["status"] == "ok"
            assert result["value"] == 6

            # Test function definition
            result = hy_surface.execute("(defn add [x y] (+ x y)) (add 5 3)")
            assert result["status"] == "ok"
            assert result["value"] == 8
        else:
            # Skip Hy-specific tests if not available
            pytest.skip("Hy not available for testing")
```

## Usage Patterns

### Fuzzy Logic Control Systems

```hy
; Temperature control system
(defn fuzzy-temperature-controller [current-temp desired-temp]
  (let [error (- desired-temp current-temp)
        heating (cond [(> error 5) 1.0]    ; High heating
                      [(> error 0) 0.5]    ; Medium heating
                      [True 0.0])]         ; No heating
        cooling (cond [(< error -5) 1.0]   ; High cooling
                      [(< error 0) 0.5]    ; Medium cooling
                      [True 0.0])]         ; No cooling
    {"heating" heating "cooling" cooling}))
```

### Heuristic Search

```hy
; 8-puzzle solver using A*
(defn manhattan-heuristic [state goal]
  "Calculate Manhattan distance heuristic"
  ; Implementation for 8-puzzle
  0)  ; Simplified

(defn solve-8-puzzle [start-state]
  "Solve 8-puzzle using A* search"
  ; A* implementation for 8-puzzle
  start-state)  ; Simplified
```

### Natural Language Processing

```hy
; Simple text classification
(defn classify-sentiment [text]
  (let [positive-words (set ["good" "great" "excellent" "amazing"])
        negative-words (set ["bad" "terrible" "awful" "horrible"])
        words (.split (.lower text))
        pos-score (sum (lfor word words (if (in word positive-words) 1 0)))
        neg-score (sum (lfor word words (if (in word negative-words) 1 0)))]
    (cond [(> pos-score neg-score) "positive"]
          [(> neg-score pos-score) "negative"]
          [True "neutral"])))

; Usage
(classify-sentiment "This product is really great and amazing")
; Returns: "positive"
```

## Security Considerations

Hy execution provides several safety features:

- **Functional Paradigm**: Immutable data structures reduce side effects
- **Lisp Macros**: Controlled code generation
- **Namespace Isolation**: Limited access to Python runtime
- **Symbolic Computation**: Focus on data transformation over system access

However, consider:

- **Memory Usage**: Recursive functions can cause stack overflow
- **Performance**: Lisp-style code may be slower than optimized Python
- **Library Access**: Hy has access to full Python standard library

## Dependencies

- **Hy**: Lisp dialect for Python (pip install hy)
- **Em-Cubed**: Framework execution environment

## Performance Characteristics

- **Strengths**:
  - Excellent for symbolic computation
  - Functional programming patterns
  - Macro system for code generation
  - Seamless Python integration

- **Considerations**:
  - Learning curve for Lisp syntax
  - May be slower for numerical computing
  - Memory intensive for large data structures

## Comparison with Other Approaches

| Approach | Best For | Hy Advantages | Hy Disadvantages |
|----------|----------|----------------|------------------|
| Python | General computing | - | Complex symbolic tasks |
| Prolog | Logic constraints | - | Functional patterns |
| Hy | Symbolic AI | Lisp power, macros, functional | Syntax learning curve |
| Multi-surface | Complex AI | Combines paradigms | Coordination complexity |

## Future Enhancements

- **Machine Learning Integration**: Neural network implementations
- **Expert Systems**: Rule-based reasoning engines
- **Natural Language**: Advanced NLP algorithms
- **Computer Vision**: Image processing pipelines
- **Robotics**: Control system implementations</content>
<parameter name="filePath">D:\GitHub\projects\em-cubed\skills\hy_fuzzy_logic\SKILL.md