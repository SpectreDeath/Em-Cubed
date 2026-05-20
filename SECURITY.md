# Security Guide for Em-Cubed

## Containerized Skill Execution

Em-Cubed provides containerized execution capabilities to securely run skills from untrusted or external sources. This feature isolates skill execution in lightweight containers with strict resource limitations.

### How It Works

When containerized execution is enabled for a surface:
1. Skills are executed in isolated Docker/Podman containers
2. Containers run with restricted privileges (read-only filesystem, no network access)
3. Resource limits are enforced (CPU, memory, execution time)
4. Each execution uses a fresh container instance
5. Containers are automatically cleaned up after execution

### Enabling Containerized Execution

Containerized execution can be enabled per-surface through the PluginManager:

```python
from em_cubed.plugin_manager import PluginManager

# Initialize plugin manager
plugin_manager = PluginManager()

# Enable containerized execution for specific surfaces
plugin_manager.enable_containerized_execution("python", timeout=30.0)
plugin_manager.enable_containerized_execution("prolog", timeout=15.0)

# Disable when no longer needed
plugin_manager.disable_containerized_execution("python")
```

### Security Features

#### Isolation
- Each skill runs in its own container instance
- Filesystem access is limited to mounted volumes only
- Network access is completely disabled (`--network=none`)
- Containers run as non-root user

#### Resource Limits
- Memory: Limited to 512MB by default (configurable)
- CPU: Limited to 0.5 cores by default (configurable)
- Execution time: Configurable timeout with default of 30 seconds
- Process limits: Container-enforced process limits

#### Filesystem Security
- Root filesystem is mounted as read-only
- Only specific directories are mounted with appropriate permissions:
  - `/execution`: Read-only access to skill code and context
  - `/output`: Read-write access for execution results

### Configuration Options

Containerized execution behavior can be customized through:

1. **Timeout Settings**: 
   - Per-surface timeout when enabling containerized execution
   - Global timeout via `EM_CUBED_TIMEOUT` environment variable
   - Surface-specific timeout in skill metadata

2. **Resource Limits** (modify in `container_surface.py`):
   - Memory limit: `--memory=512m`
   - CPU limit: `--cpus=0.5`
   - Additional limits can be added as needed

### Best Practices

1. **Enable for Untrusted Sources**: Always enable containerized execution when running skills from:
   - External repositories
   - User-submitted skills
   - Third-party skill registries
   - Unverified sources

2. **Consider Performance Impact**: Containerized execution has overhead:
   - Container startup time (~100-500ms)
   - Filesystem mounting overhead
   - Process isolation costs
   - For trusted skills, consider using regular execution

3. **Monitor Resource Usage**: 
   - Monitor container execution times via telemetry
   - Adjust timeouts based on actual skill performance
   - Watch for resource limit exceeded errors

4. **Keep Images Updated**: 
   - Container images should be rebuilt periodically
   - Security patches to base images should be applied
   - Consider using image scanning in production

### Limitations

1. **First-time Overhead**: Initial execution may be slower as container images are pulled/cached
2. **Debugging Complexity**: Debugging skills in containers requires additional tooling
3. **Surface Limitations**: Some surfaces with complex dependencies may require custom container images
4. **File System Access**: Skills needing access to host filesystem must use mounted volumes explicitly

### Troubleshooting

#### "Container runtime not available"
- Ensure Docker or Podman is installed and running
- Verify the user has permissions to run container commands
- Check that the container runtime is in PATH

#### "Container execution failed"
- Check the error message for specific failure reasons
- Verify the skill code is valid for the target surface
- Ensure required dependencies are available in the container image
- Check resource limits (memory, time) are sufficient

#### "Invalid JSON output from container"
- Ensure the skill returns properly formatted JSON output
- Check for unhandled exceptions that might break JSON output
- Validate that the container executor script is working correctly

### Implementation Notes

The containerized execution feature consists of:

1. **ContainerizedSurfacePlugin** (`src/em_cubed/container_surface.py`):
   - Wraps surface plugins with container execution
   - Handles container lifecycle and resource limits
   - Provides health checks for container availability

2. **PluginManager Extensions** (`src/em_cubed/plugin_manager.py`):
   - Methods to enable/disable containerized execution per surface
   - Automatic routing to containerized plugins when enabled
   - Integration with existing lazy-loading mechanism

3. **Container Executor** (`src/em_cubed/container_executor.py`):
   - Entry point running inside containers
   - Loads and executes skills using the standard SkillExecutor
   - Returns results as JSON to the host process

4. **Dockerfile** (`Dockerfile`):
   - Base image for building containerized surface images
   - Installs Em-Cubed in a secure, non-root configuration

### Future Enhancements

1. **Custom Container Images**: Allow specifying custom images per surface
2. **Advanced Networking**: Controlled network access for skills requiring external APIs
3. **Volume Management**: More granular control over filesystem mounts
4. **Image Signing**: Verification of container image integrity
5. **Resource Profiling**: Automatic adjustment of limits based on usage patterns