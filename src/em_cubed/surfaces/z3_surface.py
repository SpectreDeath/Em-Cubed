"""Z3 surface integration for SMT solving and optimization."""

import importlib.util
from typing import Dict, Any, Optional
import structlog

from .base import SurfaceBase
from ..plugin import SurfacePlugin

logger = structlog.get_logger()


class Z3Surface(SurfaceBase, SurfacePlugin):
    """Handle Z3 SMT solver execution and metadata extraction."""

    @property
    def name(self) -> str:
        return "z3"

    @property
    def description(self) -> str:
        return "Z3 SMT solver for arithmetic constraints/optimization"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        logger.info("Z3Surface initialized", available=self.available, timeout=self.timeout)

    def _check_availability(self) -> bool:
        """Check if z3 is available."""
        available = importlib.util.find_spec("z3") is not None
        if not available:
            logger.warning("z3 not available for Z3 surface")
        return available

    @staticmethod
    def extract_tags(source: Optional[str]) -> list:
        """Extract assertion/query identifiers from Z3 source.
        
        Looks for common Z3 patterns like:
        - Assertions: solver.add(), assert()
        - Variables: Int(), Real(), Bool(), BitVec()
        - Functions: Function(), DeclareFun()
        """
        if not source:
            return []
        import re

        tags = set()
        
        # Extract variable/function declarations
        var_patterns = [
            r'\b(Int|Real|Bool|BitVec)\s*\(',  # Variable types
            r'\bFunction\s*\(',                 # Function declarations
            r'\bDeclareFun\s*\(',               # Function declarations
            r'\bConst\s*\(',                    # Constants
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, source)
            tags.update(matches)
            
        # Extract common assertion patterns
        assert_patterns = [
            r'\.add\s*\(',                      # solver.add()
            r'\bassert\s*\(',                   # assert()
            r'\boptimize\s*\.',                 # optimize operations
            r'\bmaximize\s*\(',                 # maximize()
            r'\bminimize\s*\(',                 # minimize()
        ]
        
        for pattern in assert_patterns:
            if re.search(pattern, source):
                tags.add("assertion")
                
        # Extract query patterns
        query_patterns = [
            r'\bcheck\s*\(',                    # check()
            r'\bmodel\s*\.',                    # model access
            r'\bvalue\s*\(',                    # value()
        ]
        
        for pattern in query_patterns:
            if re.search(pattern, source):
                tags.add("query")
        
        return list(tags)

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Z3 code and return results."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Z3 code - implementation with timeout protection."""
        logger.info("Executing Z3 code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Z3 execution but z3 not available")
            return {"status": "error", "message": "z3 not available"}

        try:
            from z3 import Solver, Optimize, sat, unsat, unknown

            # Determine if this is an optimization problem based on keywords
            is_optimization = any(keyword in code.lower() for keyword in ['maximize', 'minimize', 'optimize'])
            
            # Create appropriate solver
            solver_instance = Optimize() if is_optimization else Solver()
            
            # Add context variables if provided
            if context:
                # Note: In a real implementation, we might want to inject context variables
                # For now, we'll just log that context was provided
                logger.debug("Context provided for Z3 execution", context_keys=list(context.keys()))

            # Execute the code in a restricted environment
            # We'll use exec with limited globals for safety
            globals_dict = {
                'Solver': Solver,
                'Optimize': Optimize,
                'sat': sat,
                'unsat': unsat,
                'unknown': unknown,
                # Import commonly used Z3 constructs
                'Int': __import__('z3').z3.Int,
                'Real': __import__('z3').z3.Real,
                'Bool': __import__('z3').z3.Bool,
                'BitVec': __import__('z3').z3.BitVec,
                'Function': __import__('z3').z3.Function,
                'DeclareFun': __import__('z3').z3.DeclareFun,
                'Const': __import__('z3').z3.Const,
                'And': __import__('z3').z3.And,
                'Or': __import__('z3').z3.Or,
                'Not': __import__('z3').z3.Not,
                'Xor': __import__('z3').z3.Xor,
                'Implies': __import__('z3').z3.Implies,
                'If': __import__('z3').z3.If,
                'Equals': __import__('z3').z3.Equals,
                'Distinct': __import__('z3').z3.Distinct,
                'Sum': __import__('z3').z3.Sum,
                'Prod': __import__('z3').z3.Prod,
            }
            
            # Add context to globals if provided
            if context:
                globals_dict.update(context)

            # Execute the code
            local_vars: Dict[str, Any] = {}
            exec(code, globals_dict, local_vars)
            
            # Check if solver was used and get result
            result_info = {}
            if 'solver' in local_vars:
                solver_instance = local_vars['solver']
                if hasattr(solver_instance, 'check'):
                    result = solver_instance.check()
                    result_info['status'] = str(result)
                    if result == sat:
                        result_info['model'] = str(solver_instance.model())
                    elif hasattr(solver_instance, 'upper') and is_optimization:
                         # For optimization, try to get bounds
                         try:
                             result_info['upper'] = str(solver_instance.upper())
                             result_info['lower'] = str(solver_instance.lower())
                         except Exception:
                             pass
            
            logger.info("Z3 execution successful")
            return {"status": "ok", "value": result_info or "Execution completed"}

        except Exception as e:
            logger.exception("Z3 execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)