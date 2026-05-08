from em_cubed.indexer import extract_prolog_tags

prolog_code = """
parent(john, mary).
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
"""
tags = extract_prolog_tags(prolog_code)
print("Tags:", tags)
print("Expected: parent, grandparent, ancestor")
print("Has parent?", "parent" in tags)
print("Has grandparent?", "grandparent" in tags)
print("Has ancestor?", "ancestor" in tags)
