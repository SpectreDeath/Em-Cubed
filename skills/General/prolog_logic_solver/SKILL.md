---
name: Prolog Logic Solver
Domain: Logic
Version: 1.0.0
surfaces:
  - prolog
---

## Purpose

Solve logical puzzles, constraints, and reasoning problems using Prolog's declarative programming paradigm.

## Description

A comprehensive logic solver that demonstrates Prolog's capabilities for constraint solving, puzzle resolution, and logical inference. This skill showcases how Prolog excels at problems involving rules, relationships, and logical constraints.

## Examples

### Family Relationships

```prolog
% Define family relationships
parent(john, mary).
parent(mary, ann).
parent(mary, bob).
parent(peter, mary).
parent(lisa, mary).

male(john).
male(peter).
male(bob).
female(mary).
female(ann).
female(lisa).

% Define derived relationships
father(X, Y) :- parent(X, Y), male(X).
mother(X, Y) :- parent(X, Y), female(X).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
grandfather(X, Z) :- grandparent(X, Z), male(X).
grandmother(X, Z) :- grandparent(X, Z), female(X).

sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.
brother(X, Y) :- sibling(X, Y), male(X).
sister(X, Y) :- sibling(X, Y), female(X).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
```

### Constraint Satisfaction

```prolog
% House coloring puzzle (simplified)
% Each house has different color, different owner, etc.

% Domains
color(red).
color(blue).
color(green).
color(yellow).

nationality(english).
nationality(spanish).
nationality(japanese).
nationality(italian).

% Constraints
house(Color, Nationality, Pet, Drink, Cigarette) :-

    % All different constraints
    color(Color),
    nationality(Nationality),
    member(Pet, [dog, cat, bird, fish, horse]),
    member(Drink, [tea, coffee, milk, water, juice]),
    member(Cigarette, [winston, kool, chesterfield, lucky, parliament]),

    % Specific constraints
    (Nationality = english, Color = red;
     Nationality \= english),

    (Nationality = spanish, Pet = dog;
     Nationality \= spanish),

    (Color = green, Drink = coffee;
     Color \= green),

    (Nationality = japanese, Cigarette = parliament;
     Nationality \= japanese),

    (Color = blue, Drink = tea;
     Color \= blue).

% Find solutions
solve_houses(Houses) :-
    findall(H, house(H), Houses),
    length(Houses, 5).
```

## Implementation

### Prolog Logic Solver

```prolog
% ==========================================
% FAMILY RELATIONSHIPS MODULE
% ==========================================

% Basic relationships
parent(john, mary).
parent(mary, ann).
parent(mary, bob).
parent(peter, mary).
parent(lisa, mary).

% Gender definitions
male(john).
male(peter).
male(bob).
female(mary).
female(ann).
female(lisa).

% Derived relationships
father(X, Y) :- parent(X, Y), male(X).
mother(X, Y) :- parent(X, Y), female(X).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
grandfather(X, Z) :- grandparent(X, Z), male(X).
grandmother(X, Z) :- grandparent(X, Z), female(X).

sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.
brother(X, Y) :- sibling(X, Y), male(X).
sister(X, Y) :- sibling(X, Y), female(X).

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% ==========================================
% CONSTRAINT SOLVING MODULE
% ==========================================

% N-Queens problem
queens(N, Queens) :-
    length(Queens, N),
    Queens ins 1..N,
    safe_queens(Queens).

safe_queens([]).
safe_queens([Queen|Others]) :-
    safe_queens(Others),
    no_attack(Queen, Others, 1).

no_attack(_, [], _).
no_attack(Y, [Y1|Ylist], Dist) :-
    Y =\= Y1,
    abs(Y - Y1) =\= Dist,
    Dist1 is Dist + 1,
    no_attack(Y, Ylist, Dist1).

% Solve 8-queens
solve_8_queens(Solution) :- queens(8, Solution).

% ==========================================
% LOGIC PUZZLES MODULE
% ==========================================

% Einstein's Riddle (simplified version)
% Five houses, each with different characteristics

% Domains
color(red; blue; green; yellow; white).
nationality(english; spanish; japanese; italian; norwegian).
pet(dog; cat; bird; fish; horse).
drink(tea; coffee; milk; water; juice).
cigarette(winston; kool; chesterfield; lucky; parliament).

% Helper predicates
right_of(X, Y, [X,Y|_]).
right_of(X, Y, [_|Rest]) :- right_of(X, Y, Rest).

next_to(X, Y, List) :- right_of(X, Y, List); right_of(Y, X, List).

first(H, [H|_]).

% The puzzle constraints
einstein_puzzle(Houses) :-
    % Five houses
    length(Houses, 5),

    % Each house has all attributes
    maplist(house_attributes, Houses),

    % The English lives in the red house
    member(house(red, english, _, _, _), Houses),

    % The Spanish owns the dog
    member(house(_, spanish, dog, _, _), Houses),

    % Coffee is drunk in the green house
    member(house(green, _, _, coffee, _), Houses),

    % The Japanese smokes parliaments
    member(house(_, japanese, _, _, parliament), Houses),

    % The Norwegian lives in the first house
    first(house(_, norwegian, _, _, _), Houses),

    % Additional constraints...
    % (Full implementation would include all 15 constraints)

% ==========================================
% SEARCH AND REASONING MODULE
% ==========================================

% Binary search tree operations
bst_insert(empty, X, tree(empty, X, empty)).
bst_insert(tree(L, Y, R), X, tree(L1, Y, R)) :- X =< Y, bst_insert(L, X, L1).
bst_insert(tree(L, Y, R), X, tree(L, Y, R1)) :- X > Y, bst_insert(R, X, R1).

bst_search(tree(_, Y, _), Y).
bst_search(tree(L, Y, _), X) :- X < Y, bst_search(L, X).
bst_search(tree(_, Y, R), X) :- X > Y, bst_search(R, X).

% Graph search (DFS)
dfs(Start, Goal, Path) :- dfs(Start, Goal, [Start], Path).

dfs(Goal, Goal, Visited, Visited).
dfs(Current, Goal, Visited, Path) :-
    neighbor(Current, Next),
    \+ member(Next, Visited),
    dfs(Next, Goal, [Next|Visited], Path).

% Define graph edges (example)
neighbor(a, b).
neighbor(a, c).
neighbor(b, d).
neighbor(c, d).
neighbor(d, e).

% ==========================================
% UTILITY PREDICATES
% ==========================================

% List operations
member(X, [X|_]).
member(X, [_|T]) :- member(X, T).

length([], 0).
length([_|T], N) :- length(T, M), N is M + 1.

append([], L, L).
append([H|T], L, [H|R]) :- append(T, L, R).

reverse([], []).
reverse([H|T], R) :- reverse(T, RevT), append(RevT, [H], R).

% Mathematical utilities
factorial(0, 1).
factorial(N, F) :- N > 0, N1 is N - 1, factorial(N1, F1), F is N * F1.

fibonacci(0, 0).
fibonacci(1, 1).
fibonacci(N, F) :- N > 1, N1 is N - 1, N2 is N - 2,
                   fibonacci(N1, F1), fibonacci(N2, F2), F is F1 + F2.

% Set operations
union([], S, S).
union([H|T], S, U) :- member(H, S), union(T, S, U).
union([H|T], S, [H|U]) :- \+ member(H, S), union(T, S, U).

intersection([], _, []).
intersection([H|T], S, [H|I]) :- member(H, S), intersection(T, S, I).
intersection([H|T], S, I) :- \+ member(H, S), intersection(T, S, I).

% ==========================================
% DEMONSTRATION QUERIES
% ==========================================

% Family relationship queries
?- father(X, mary).           % Who is Mary's father?
?- grandmother(X, ann).       % Who is Ann's grandmother?
?- sibling(mary, X).          % Who are Mary's siblings?
?- ancestor(john, X).         % Who are John's descendants?

% Constraint solving
?- queens(4, Solution).        % Solve 4-queens problem
?- solve_8_queens(Solution).   % Solve 8-queens problem

% Logic puzzles
?- dfs(a, e, Path).           % Find path from a to e

% Utility functions
?- factorial(5, Result).       % Calculate 5!
?- fibonacci(8, Result).       % Calculate 8th Fibonacci number
```

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PrologSurface

class TestPrologLogicSolver:
    @pytest.fixture
    def prolog_surface(self):
        """Get Prolog surface for logic operations."""
        surface = PrologSurface()
        return surface

    def test_family_relationships(self, prolog_surface):
        """Test family relationship queries."""
        if not prolog_surface.available:
            pytest.skip("PySWIP not available")

        # Define family relationships
        prolog_surface.execute("parent(john, mary).")
        prolog_surface.execute("parent(mary, ann).")
        prolog_surface.execute("male(john).")
        prolog_surface.execute("female(mary).")
        prolog_surface.execute("female(ann).")

        # Define rules
        prolog_surface.execute("father(X, Y) :- parent(X, Y), male(X).")
        prolog_surface.execute("daughter(X, Y) :- parent(Y, X), female(X).")

        # Query relationships
        result = prolog_surface.execute("father(john, mary).")
        # Result format depends on PySWIP implementation

    def test_constraint_solving(self, prolog_surface):
        """Test constraint solving capabilities."""
        if not prolog_surface.available:
            pytest.skip("PySWIP not available")

        # Define simple constraints
        prolog_surface.execute("valid_age(X) :- X >= 0, X =< 120.")

        # Test constraints
        result = prolog_surface.execute("valid_age(25).")
        # Should succeed

        result = prolog_surface.execute("valid_age(150).")
        # Should fail

    def test_list_operations(self, prolog_surface):
        """Test Prolog list operations."""
        if not prolog_surface.available:
            pytest.skip("PySWIP not available")

        # Define list operations
        prolog_surface.execute("my_length([], 0).")
        prolog_surface.execute("my_length([_|T], N) :- my_length(T, M), N is M + 1.")

        # Test list length
        result = prolog_surface.execute("my_length([1,2,3], Len).")
        # Should find Len = 3

    def test_mathematical_functions(self, prolog_surface):
        """Test mathematical functions in Prolog."""
        if not prolog_surface.available:
            pytest.skip("PySWIP not available")

        # Test factorial
        prolog_surface.execute("factorial(0, 1).")
        prolog_surface.execute("factorial(N, F) :- N > 0, N1 is N - 1, factorial(N1, F1), F is N * F1.")

        result = prolog_surface.execute("factorial(5, Result).")
        # Should find Result = 120

    def test_error_handling(self, prolog_surface):
        """Test error handling for invalid Prolog code."""
        if not prolog_surface.available:
            pytest.skip("PySWIP not available")

        # Test invalid syntax
        result = prolog_surface.execute("invalid syntax +++")
        # Should handle gracefully

        # Test undefined predicates
        result = prolog_surface.execute("undefined_predicate(X).")
        # Should handle gracefully
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
from em_cubed.surfaces import PrologSurface
import tempfile
from pathlib import Path

def test_prolog_skill_integration():
    """Test the Prolog logic solver in a complete workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create skill directory
        skills_dir = Path(tmpdir) / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "prolog_logic_solver"
        skill_dir.mkdir()

        # Create SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: Prolog Logic Solver
Domain: Logic
surfaces:
  - prolog
---

## Purpose
Logic solving and constraint satisfaction

## Description
Prolog-based logic solver for testing
""")

        # Index skills
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir, registry_file)

        # Search for logic solver
        results = search_registry("logic", registry_file)
        assert len(results) >= 1

        skill_result = next((r for r in results if r["name"] == "Prolog Logic Solver"), None)
        assert skill_result is not None

        # Test Prolog surface (if available)
        prolog_surface = PrologSurface()
        if prolog_surface.available:
            # Test basic Prolog functionality
            result = prolog_surface.execute("X is 2 + 3.")
            # Result should contain X = 5

            # Test list operations
            prolog_surface.execute("my_length([], 0).")
            prolog_surface.execute("my_length([_|T], N) :- my_length(T, M), N is M + 1.")
            result = prolog_surface.execute("my_length([a,b,c], Len).")
            # Should find Len = 3
        else:
            # Skip Prolog-specific tests if not available
            pytest.skip("PySWIP not available for Prolog testing")
```

## Usage Patterns

### Basic Logic Queries

```prolog
% Define facts
likes(john, pizza).
likes(mary, pizza).
likes(john, burgers).

% Define rules
friends(X, Y) :- likes(X, Z), likes(Y, Z), X \= Y.

% Query
?- friends(john, Who).  % Who are John's friends?
```

### Constraint Solving

```prolog
% Send + More = Money puzzle
solve_puzzle([S,E,N,D,M,O,R,Y]) :-

    % All different digits
    fd_domain([S,E,N,D,M,O,R,Y], 0, 9),
    fd_all_different([S,E,N,D,M,O,R,Y]),

    % Constraints
    S #\= 0, M #\= 0,

    % SEND + MORE = MONEY
    1000*S + 100*E + 10*N + D +
    1000*M + 100*O + 10*R + E #=
    10000*M + 1000*O + 100*N + 10*E + Y,

    % Label variables
    fd_labeling([S,E,N,D,M,O,R,Y]).
```

### Knowledge Base Queries

```prolog
% Define knowledge base
bird(tweety).
bird(polly).
can_fly(X) :- bird(X), not penguin(X).
penguin(polly).

% Query capabilities
?- can_fly(tweety).  % Yes
?- can_fly(polly).   % No (penguin)
```

## Security Considerations

Prolog execution requires careful consideration:

- **Safe Execution**: Use PySWIP in controlled environments
- **Resource Limits**: Prolog can consume significant CPU/memory
- **Input Validation**: Validate all Prolog code before execution
- **Sandboxing**: Consider running Prolog in isolated processes

## Dependencies

- **PySWIP**: Python-Prolog bridge library
- **SWI-Prolog**: Underlying Prolog implementation
- **Em-Cubed**: Framework for skill execution

## Performance Characteristics

- **Strengths**:
  - Excellent for logical inference
  - Declarative problem solving
  - Backtracking search algorithms
  - Pattern matching and unification

- **Considerations**:
  - May be slower for numerical computations
  - Memory intensive for large knowledge bases
  - Learning curve for declarative programming

## Comparison with Other Approaches

| Approach | Best For | Prolog Advantages | Prolog Disadvantages |
|----------|----------|-------------------|---------------------|
| Python | General computing | - | Complex logic patterns |
| Prolog | Logic/Constraints | Declarative, backtracking | Numeric computation |
| Hy | Lisp programming | - | Logic constraints |
| Multi-surface | Complex problems | Combines all approaches | Coordination overhead |