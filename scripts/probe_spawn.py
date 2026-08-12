"""Probe what actually happens in a spawned child process with asteval."""
import multiprocessing
import sys


def _child_runner(q):
    """This runs inside the spawned child."""
    try:
        from asteval import Interpreter

        BLOCKED = ['open', '__import__', 'eval', 'exec', 'compile', '__builtins__', 'breakpoint', 'input']
        CALLABLE_BLOCKED = ['open', '__import__', 'eval', 'exec', 'compile', 'breakpoint', 'input']

        def _missing_builtin_func(name):
            def _blocked(*a, **k):
                raise RuntimeError(f"'{name}' is not available in sandbox")
            _blocked.__name__ = name
            return _blocked

        # --- Strategy A: set __builtins__ = function ---
        aeval_a = Interpreter()
        print(f"[CHILD A] before pop, __builtins__ type: {type(aeval_a.symtable.get('__builtins__'))}", flush=True)
        for bad in BLOCKED:
            aeval_a.symtable.pop(bad, None)
        for bad in BLOCKED:
            aeval_a.symtable[bad] = _missing_builtin_func(bad)
        print(f"[CHILD A] after install, __builtins__ type: {type(aeval_a.symtable.get('__builtins__'))}", flush=True)
        try:
            r_a = aeval_a('1 + 1')
            print(f"[CHILD A] 1+1 = {r_a}, errors = {aeval_a.error}", flush=True)
        except Exception as e:
            print(f"[CHILD A] 1+1 exception: {e}", flush=True)

        # --- Strategy B: set __builtins__ = {} ---
        aeval_b = Interpreter()
        for bad in BLOCKED:
            aeval_b.symtable.pop(bad, None)
        aeval_b.symtable['__builtins__'] = {}
        for bad in CALLABLE_BLOCKED:
            aeval_b.symtable[bad] = _missing_builtin_func(bad)
        print(f"[CHILD B] after install, __builtins__ type: {type(aeval_b.symtable.get('__builtins__'))}", flush=True)
        try:
            r_b = aeval_b('1 + 1')
            print(f"[CHILD B] 1+1 = {r_b}, errors = {aeval_b.error}", flush=True)
        except Exception as e:
            print(f"[CHILD B] 1+1 exception: {e}", flush=True)

        try:
            _ = aeval_b("exec('x=1')")
            print(f"[CHILD B] exec errors = {[str(e) for e in aeval_b.error]}", flush=True)
        except Exception as e:
            print(f"[CHILD B] exec exception: {e}", flush=True)

        q.put({"status": "ok"})
    except Exception as e:
        import traceback
        q.put({"status": "error", "message": str(e), "tb": traceback.format_exc()})


if __name__ == "__main__":
    print(f"Host Python: {sys.version}", flush=True)
    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_child_runner, args=(q,))
    p.start()
    p.join(30)
    if p.is_alive():
        p.terminate()
        print("TIMED OUT")
    else:
        try:
            result = q.get_nowait()
            print("Child result:", result)
        except Exception as e:
            print("No result from child:", e)
