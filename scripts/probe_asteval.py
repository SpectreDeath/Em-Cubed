"""Deeper diagnostic: test the EXACT code path used in _child_eval_runner."""
from asteval import Interpreter

BLOCKED = ['open', '__import__', 'eval', 'exec', 'compile', '__builtins__', 'breakpoint', 'input']
CALLABLE_BLOCKED = ['open', '__import__', 'eval', 'exec', 'compile', 'breakpoint', 'input']


def _missing_builtin_func(name):
    def _blocked(*args, **kwargs):
        raise RuntimeError(f"'{name}' is not available in the sandboxed environment")
    _blocked.__name__ = name
    return _blocked


print("=== Test A: pop all, then install FUNCTION wrapper for __builtins__ ===")
aeval_a = Interpreter()
for bad in BLOCKED:
    aeval_a.symtable.pop(bad, None)
for bad in BLOCKED:  # includes __builtins__
    aeval_a.symtable[bad] = _missing_builtin_func(bad)

print("__builtins__ value type:", type(aeval_a.symtable.get('__builtins__')))
r = aeval_a('1 + 1')
print("1+1 result:", r, "errors:", aeval_a.error)


print("\n=== Test B: pop all, install function for CALLABLE ones only, set __builtins__={} ===")
aeval_b = Interpreter()
for bad in BLOCKED:
    aeval_b.symtable.pop(bad, None)
# Key: set __builtins__ to empty DICT, not a function
aeval_b.symtable['__builtins__'] = {}
for bad in CALLABLE_BLOCKED:  # does NOT include __builtins__
    aeval_b.symtable[bad] = _missing_builtin_func(bad)

print("__builtins__ value type:", type(aeval_b.symtable.get('__builtins__')))
r2 = aeval_b('1 + 1')
print("1+1 result:", r2, "errors:", aeval_b.error)

r3 = aeval_b('len([1,2,3])')
print("len result:", r3, "errors:", aeval_b.error)

r4 = aeval_b("exec('x=1')")
print("exec result:", r4, "errors:", [str(e) for e in aeval_b.error])

r5 = aeval_b("[i*2 for i in range(5)]")
print("list comp result:", r5, "errors:", aeval_b.error)
