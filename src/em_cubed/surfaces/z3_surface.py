"""Z3 surface integration for SMT solving and optimization."""

import asyncio
import importlib.util
from typing import Dict, Any, Optional
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class Z3Surface(SurfaceBase):
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
        """Execute Z3 code with timeout protection."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Z3 code - implementation with timeout protection."""
        logger.info("Executing Z3 code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Z3 execution but z3 not available")
            return {"status": "error", "message": "z3 not available"}

        try:
            from z3 import Solver, Optimize, sat, unsat, unknown, Int, Real, Bool, BitVec, Function, Const, And, Or, Not, Xor, Implies, If, Distinct, Sum, Product
            from asteval import Interpreter

            def execute_code():
                # Determine if this is an optimization problem based on keywords
                is_optimization = any(keyword in code.lower() for keyword in ['maximize', 'minimize', 'optimize'])
                
                # Create appropriate solver (expose to user code)
                solver_instance = Optimize() if is_optimization else Solver()

                # Create asteval interpreter with Z3 symbols pre-registered
                aeval = Interpreter()

                # Inject Z3 symbols and solver into interpreter's namespace
                aeval.symtable['Solver'] = Solver
                aeval.symtable['Optimize'] = Optimize
                aeval.symtable['sat'] = sat
                aeval.symtable['unsat'] = unsat
                aeval.symtable['unknown'] = unknown
                aeval.symtable['Int'] = Int
                aeval.symtable['Real'] = Real
                aeval.symtable['Bool'] = Bool
                aeval.symtable['BitVec'] = BitVec
                aeval.symtable['Function'] = Function
                aeval.symtable['Const'] = Const
                aeval.symtable['And'] = And
                aeval.symtable['Or'] = Or
                aeval.symtable['Not'] = Not
                aeval.symtable['Xor'] = Xor
                aeval.symtable['Implies'] = Implies
                aeval.symtable['If'] = If
                aeval.symtable['Distinct'] = Distinct
                aeval.symtable['Sum'] = Sum
                aeval.symtable['Product'] = Product
                # Provide a pre-created solver instance for convenience
                aeval.symtable['solver'] = solver_instance

                # Add context to interpreter if provided
                if context:
                    aeval.symtable.update(context)

                # Execute the code
                aeval(code)

                # Check for errors
                if aeval.error:
                    error_msg = str(aeval.error[0])
                    logger.info("Z3 execution failed with error", error=error_msg)
                    return {"status": "error", "message": error_msg}

                # Build result info from solver state if available
                result_info = {}
                if 'solver' in aeval.symtable:
                    solver = aeval.symtable['solver']
                    if hasattr(solver, 'check'):
                        check_result = solver.check()
                        result_info['status'] = str(check_result)
                        if check_result == sat:
                            result_info['model'] = str(solver.model())
                        elif hasattr(solver, 'upper') and is_optimization:
                            try:
                                result_info['upper'] = str(solver.upper())
                                result_info['lower'] = str(solver.lower())
                            except Exception:
                                pass

                logger.info("Z3 execution successful")
                return {"status": "ok", "value": result_info or "Execution completed"}

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, execute_code
            )

        except asyncio.TimeoutError:
            logger.warning("Z3 execution timed out", timeout=self.timeout)
            return {
                "status": "error",
                "message": f"Execution timed out after {self.timeout}s"
            }
        except Exception as e:
            logger.exception("Z3 execution failed", error=str(e), code=code)
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return bool(self.available)