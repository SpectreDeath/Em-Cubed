"""Janus surface integration for Python-Prolog bridge."""
from typing import List, Dict, Any, Optional

class JanusSurface:
    """Handle Janus/SWI-Prolog bridge integration."""
    
    def __init__(self):
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Janus/SWI-Prolog is available."""
        try:
            # Janus is typically part of SWI-Prolog's Python bridge
            import janus_swi
            return True
        except ImportError:
            return False
    
    def query_once(self, query: str) -> Dict[str, Any]:
        """Execute a single Prolog query via Janus."""
        if not self.available:
            return {"status": "error", "message": "Janus not available"}
        
        try:
            import janus_swi
            result = janus_swi.query_once(query)
            return {"status": "ok", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def consult(self, file_path: str) -> Dict[str, Any]:
        """Load a Prolog file via Janus."""
        if not self.available:
            return {"status": "error", "message": "Janus not available"}
        
        try:
            import janus_swi
            janus_swi.consult(file_path)
            return {"status": "ok", "message": f"Loaded {file_path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
