*** Begin Patch
*** Update File: src/em_cubed/surfaces/python_surface.py
@@
-from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeoutError
+from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeoutError
@@
-def _missing_builtin_func(nm: str):
-    """Return a callable that raises a clear RuntimeError for a missing builtin.
-
-    This helper avoids late-binding closure issues and linter complaints from
-    constructing lambdas inside loops.
-    """
-    def _fn(*a, **k):
-        _raise_missing_builtin(nm)
-    return _fn
+def _missing_builtin_func(nm: str):
+    """Return a callable that raises a clear RuntimeError for a missing builtin.
+
+    This helper avoids late-binding closure issues and linter complaints from
+    constructing lambdas inside loops.
+    """
+    def _fn(*a, **k):
+        _raise_missing_builtin(nm)
+    return _fn
*** End Patch
