"""Probe that uses the ACTUAL module import path from the child process."""
import multiprocessing
import sys
import os

# Make em_cubed importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def _child_using_module(q):
    """Mimics what _child_eval_runner does but with verbose output."""
    import traceback as tb_mod
    try:
        # This is exactly what the spawned child does
        from em_cubed.surfaces.python_surface import _build_restricted_interpreter, _BLOCKED_SYMBOLS

        print(f"[CHILD] Module imported OK. _BLOCKED_SYMBOLS = {_BLOCKED_SYMBOLS}", flush=True)

        # Try build with empty context
        aeval = _build_restricted_interpreter({})
        print(f"[CHILD] Interpreter built OK. __builtins__ type: {type(aeval.symtable.get('__builtins__'))}", flush=True)

        # Evaluate simple code
        result = aeval('1 + 1')
        print(f"[CHILD] 1+1 = {result}, errors = {aeval.error}", flush=True)

        if aeval.error:
            err_msg = str(aeval.error[0].msg) if hasattr(aeval.error[0], 'msg') else str(aeval.error[0])
            q.put({"status": "error", "message": err_msg})
        else:
            q.put({"status": "ok", "value": result})

    except Exception as e:
        print(f"[CHILD] EXCEPTION: {e}", flush=True)
        print(tb_mod.format_exc(), flush=True)
        q.put({"status": "exception", "message": str(e), "tb": tb_mod.format_exc()})


if __name__ == "__main__":
    print(f"Python: {sys.version}", flush=True)
    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_child_using_module, args=(q,))
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
