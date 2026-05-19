"""Container executor for running skills in isolated environments."""
import json
import sys
import traceback
from pathlib import Path

from em_cubed.skills.executor import SkillExecutor
from em_cubed.plugin_manager import PluginManager
from em_cubed.skills.registry import SkillRegistry


def main():
    """Main entry point for containerized skill execution."""
    if len(sys.argv) < 4:
        print(json.dumps({
            "status": "error",
            "message": "Usage: python -m em_cubed.container_executor <code_file> <context_file> <timeout>"
        }))
        sys.exit(1)
    
    context_file = Path(sys.argv[2])
    timeout = float(sys.argv[3]) if sys.argv[3] != "null" else None
    
    try:
        # Read code and context
        _ = Path(sys.argv[1]).read_text(encoding="utf-8")
        context = {}
        if context_file.exists() and not context_file.is_symlink():
            context_content = context_file.read_text(encoding="utf-8")
            if context_content.strip():
                context = json.loads(context_content)
        
        # Initialize plugin manager and registry
        plugin_manager = PluginManager()
        registry = SkillRegistry()
        skills_dir = Path("/app/skills")
        
        # Initialize executor
        executor = SkillExecutor(plugin_manager, registry, skills_dir)
        
        # Determine surface from context or default to python
        surface_name = context.get("surface", "python")
        
        # Create execution request
        from em_cubed.skills.executor import SkillExecutionRequest
        request = SkillExecutionRequest(
            skill_id="containerized_skill",
            input_data=context.get("skill_input", {}),
            surface=surface_name,
            timeout=timeout,
            context=context
        )
        
        # Execute skill
        import asyncio
        result = asyncio.run(executor.execute(request))
        
        # Output result as JSON
        print(json.dumps({
            "status": "ok" if result.success else "error",
            "value": result.output,
            "message": result.error,
            "execution_time_ms": result.execution_time_ms,
            "surface_used": result.surface_used
        }))
        
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Container executor error: {str(e)}\n{traceback.format_exc()}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()