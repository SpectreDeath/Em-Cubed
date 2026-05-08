import re
prolog_code = """
        parent(john, mary).
        grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
        ancestor(X, Y) :- parent(X, Y).
        ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
        """
heads = re.findall(r"([a-z][a-zA-Z0-9_]*)\s*\(", prolog_code)
print("Heads found:", heads)
