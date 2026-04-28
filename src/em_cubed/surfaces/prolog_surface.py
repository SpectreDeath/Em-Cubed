"""Prolog surface integration using pyswip."""
import subprocess
from typing import List, Dict, Any, Optional

class PrologSurface:
    """Handle Prolog code execution and predicate extraction."""
    
    def __init__(self):
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if PySWIP is available."""
        try:
            import pyswip
            return True
        except ImportError:
            return False
    
    def extract_tags(self, prolog_source: str) -> List[str]:
        """Extract predicate names from Prolog source as logic_tags."""
        if not prolog_source:
            return []
        import re
        # Match predicate heads: name( or name :- 
        heads = re.findall(r"^([a-z][a-zA-Z0-9_]*)\s*[:(]", prolog_source, re.MULTILINE)
        # Deduplicate, exclude Prolog builtins
        builtins = {"not", "is", "true", "fail", "assert", "retract"}
        return list(dict.fromkeys(h for h in heads if h not in builtins))
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Prolog code and return results."""
        if not self.available:
            return {"status": "error", "message": "PySWIP not available"}
        
        try:
            from pyswip import Prolog
            prolog = Prolog()
            # Load context as facts if provided
            if context:
                for key, value in context.items():
                    prolog.assertz(f"{key}({value})")
            # Execute code
            prolog.assertz(code)
            return {"status": "ok", "message": "Code executed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
