# Remote Skill Registry Federation

## Overview

Em-Cubed supports federation with remote skill registries, allowing skills to be discovered, shared, and synchronized across different installations, teams, or organizations. This enables collaborative skill development and distribution of pre-built skills.

## Features

- **Skill Discovery**: Search for skills across multiple remote registries
- **Automatic Synchronization**: Keep local skill registry in sync with remote sources
- **Authentication Support**: Secure access to private registries
- **Caching**: Efficient local caching reduces network requests
- **Flexible Configuration**: Multiple registries with different sync intervals

## Architecture

The remote registry federation consists of:

1. **RemoteSkillRegistry**: Handles communication with remote registries
2. **SkillRegistry Extensions**: Methods for syncing and discovering remote skills
3. **Environment Configuration**: Enable/disable and configure via environment variables
4. **Caching Layer**: Local cache of remote skill data for performance

## Configuration

### Environment Variables

```bash
# Enable remote registry federation
export EM_CUBED_REMOTE_REGISTRY_ENABLED=true

# Configure registries (JSON format)
export EM_CUBED_REGISTRIES='{
  "public-hub": {
    "url": "https://skills.em-cubed.org",
    "token": "your-token-here",
    "interval": 300
  },
  "private-team": {
    "url": "https://skills.internal.company.com",
    "token": "private-token",
    "interval": 1800
  }
}'
```

### Programmatic Configuration

```python
from em_cubed.skills.registry import SkillRegistry
from em_cubed.skills.remote_registry import RemoteSkillRegistry
from pathlib import Path

# Initialize local registry
skills_dir = Path("./skills")
registry_file = Path("./skills/registry.json")
local_registry = SkillRegistry(skills_dir, registry_file)

# Initialize remote registry manager
remote_registry = RemoteSkillRegistry(local_registry)

# Add registries
remote_registry.add_registry(
    "public-hub",
    "https://skills.em-cubed.org",
    token="your-token-here",
    sync_interval=300  # 5 minutes
)

# Set the remote registry manager on the local registry
local_registry.set_remote_registry_manager(remote_registry)
```

## Usage

### Synchronizing with Remote Registries

```python
# Sync all configured registries
results = local_registry.sync_with_remote_registries()
print(f"Sync results: {results}")

# Force sync (ignore sync intervals)
results = local_registry.sync_with_remote_registries(force=True)
```

### Discovering Skills from Remote Registries

```python
# Search for skills matching a query
skills = local_registry.discover_remote_skills("data processing", limit=10)
for skill in skills:
    print(f"Found skill: {skill.name} ({skill.domain})")

# Get registry information
info = local_registry.get_remote_registry_info()
print(f"Registry info: {info}")
```

## Remote Registry API Format

Remote registries should provide a REST API with the following endpoints:

### GET /api/skills
Returns a list of skills in the registry.

**Response Format:**
```json
{
  "skills": [
    {
      "skill_id": "domain/skill-name",
      "name": "Skill Name",
      "domain": "domain",
      "version": "1.0.0",
      "surfaces": ["python", "prolog"],
      "description": "Skill description",
      "purpose": "What the skill does",
      "dependencies": [],
      "input_schema": {...},
      "output_schema": {...},
      "capabilities": {...},
      "compatibility": {...},
      "quality_thresholds": {...},
      "tags": ["tag1", "tag2"],
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z",
      "metrics": {
        "applied_count": 100,
        "success_count": 95,
        "total_execution_time": 250.5,
        "total_token_usage": 15000,
        "last_executed": "2023-12-01T10:30:00Z"
      }
    }
  ]
}
```

### GET /api/skills/search?q=query&limit=10
Search for skills matching a query.

**Parameters:**
- `q`: Search query (searches name, description, tags, etc.)
- `limit`: Maximum number of results to return (default 10)

**Response Format:** Same as `/api/skills` but filtered to matching skills.

## Security Considerations

1. **Token Security**: Registry tokens should be kept secure and not committed to version control
2. **Network Security**: Use HTTPS for all registry communications
3. **Input Validation**: All skill data from remote registries is validated before being added to the local registry
4. **Rate Limiting**: Implement rate limiting on your remote registries to prevent abuse
5. **Content Validation**: Consider implementing skill validation on remote registries to prevent malicious skills

## Best Practices

1. **Use Stable URLs**: Registry URLs should be stable and versioned if possible
2. **Monitor Sync Logs**: Check logs for sync errors or warnings
3. **Start with Public Registries**: Begin by connecting to public skill registries before setting up private ones
4. **Regular Backups**: Continue to backup your local registry even when using federation
5. **Skill Provenance**: Consider tracking which registry each skill came from for audit purposes

## Limitations

1. **Eventual Consistency**: There may be a delay between when a skill is updated in a remote registry and when it appears locally
2. **Conflict Resolution**: If the same skill exists in multiple registries, the last synced version wins
3. **Network Dependencies**: Registry federation requires network access to remote registries
4. **API Compatibility**: Remote registries must implement the expected API format

## Future Enhancements

1. **Skill Subscription**: Get notified when specific skills are updated
2. **Digital Signatures**: Verify skill authenticity and integrity
3. **Peer-to-Peer Federation**: Direct skill sharing between Em-Cubed instances
4. **Skill Marketplace**: Built-in discovery and rating system for skills
5. **Advanced Search**: Full-text search, faceted search, and skill recommendations
6. **Webhooks**: Get notified via HTTP webhooks when registry changes occur

## Troubleshooting

### "Remote registry manager not configured"
- Ensure `EM_CUBED_REMOTE_REGISTRY_ENABLED=true` is set
- Verify that you've called `set_remote_registry_manager()` on your SkillRegistry instance
- Check that the RemoteSkillRegistry was initialized correctly

### Synchronization Failures
- Check network connectivity to the remote registry
- Verify registry URL and authentication token
- Look at logs for specific error messages
- Ensure the remote registry is returning data in the expected format

### No Skills Found
- Verify that the remote registry actually contains skills
- Check that your search query matches skill names, descriptions, or tags
- Try a broader search query or remove the query parameter to see all skills
- Check the registry's /api/skills endpoint directly to see what data is available

## Example: Setting Up a Private Skill Registry

1. Deploy a registry server (could be a simple Flask/Django app or use a hosted solution)
2. Implement the `/api/skills` and `/api/skills/search` endpoints
3. Secure the registry with HTTPS and authentication (API keys, OAuth, etc.)
4. Configure Em-Cubed instances to connect to the registry using the environment variables or programmatic approach
5. Begin sharing skills across your team or organization

The remote registry federation feature transforms Em-Cubed from a local skill framework into a collaborative ecosystem where skills can be shared, discovered, and reused across teams and organizations.