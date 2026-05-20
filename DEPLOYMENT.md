# Em-Cubed Deployment and Production Guide

This guide covers deploying Em-Cubed in production environments, including configuration, scaling, monitoring, and security considerations.

## Table of Contents
1. [Production Readiness Checklist](#production-readiness-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Deployment Options](#deployment-options)
4. [Scaling and Performance](#scaling-and-performance)
5. [Monitoring and Observability](#monitoring-and-observability)
6. [Security Considerations](#security-considerations)
7. [Maintenance and Updates](#maintenance-and-updates)
8. [Troubleshooting in Production](#troubleshooting-in-production)

## Production Readiness Checklist

Before deploying to production, ensure you have completed the following:

- [ ] Set `EM_CUBED_API_KEY` environment variable for API authentication
- [ ] Configure appropriate timeout values (`EM_CUBED_TIMEOUT`)
- [ ] Set up proper logging and monitoring
- [ ] Configure resource limits (memory, CPU)
- [ ] Test all skill execution paths
- [ ] Verify surface availability and health checks
- [ ] Set up backup and disaster recovery procedures
- [ ] Review and apply security patches to dependencies
- [ ] Conduct load testing with expected production traffic
- [ ] Configure proper error handling and alerting

## Environment Configuration

### Required Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EM_CUBED_API_KEY` | API key for authentication (if set, required for all API requests) | None | Optional* |
| `EM_CUBED_TIMEOUT` | Default execution timeout in seconds | 30 | No |
| `EM_CUBED_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `EM_CUBED_WORKERS` | Number of worker processes for API server | 4 | No |
| `EM_CUBED_HOST` | Host to bind API server | 0.0.0.0 | No |
| `EM_CUBED_PORT` | Port for API server | 8000 | No |
| `PYTHONPATH` | Should include the Em-Cubed source directory | . | Yes |

*Note: If `EM_CUBED_API_KEY` is set, all API requests must include the `X-API-Key` header.

### Surface-Specific Environment Variables

Some surfaces may require additional environment variables:

- **LLM Surface**: API keys for providers (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
- **Database Surfaces**: Connection strings (DATABASE_URL, etc.)
- **Cloud Surfaces**: Credentials (AWS_ACCESS_KEY_ID, etc.)

## Deployment Options

### Option 1: Direct Execution (Development/Testing)

```bash
# Install in development mode
pip install -e .

# Start the API server
em3 serve

# Or run directly
python -m em_cubed.api.main
```

### Option 2: Production Server with Gunicorn

```bash
# Install production dependencies
pip install ".[prod]"  # If you have defined prod extras
# Or manually:
pip install gunicorn uvicorn

# Start with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker em_cubed.api.main:app
```

### Option 3: Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml .
COPY README.md .
RUN pip install --no-cache-dir .

# Copy source code
COPY src/ ./src/
COPY skills/ ./skills/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start server
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "em_cubed.api.main:app"]
```

Build and run:
```bash
docker build -t em-cubed .
docker run -p 8000:8000 \
    -e EM_CUBED_API_KEY=your-secret-key \
    -e EM_CUBED_TIMEOUT=30 \
    em-cubed
```

### Option 4: Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: em-cubed
  labels:
    app: em-cubed
spec:
  replicas: 3
  selector:
    matchLabels:
      app: em-cubed
  template:
    metadata:
      labels:
        app: em-cubed
    spec:
      containers:
      - name: em-cubed
        image: em-cubed:latest
        ports:
        - containerPort: 8000
        env:
        - name: EM_CUBED_API_KEY
          valueFrom:
            secretKeyRef:
              name: em-cubed-secrets
              key: api-key
        - name: EM_CUBED_TIMEOUT
          value: "30"
        - name: EM_CUBED_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: em-cubed-service
spec:
  selector:
    app: em-cubed
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## Scaling and Performance

### Horizontal Scaling

Em-Cubed is designed to scale horizontally:
- Multiple API instances can run behind a load balancer
- Each instance maintains its own skill registry and plugin manager
- Shared state (if needed) should be externalized (e.g., Redis for caching)

### Resource Requirements

- **Memory**: 512MB-2GB per instance depending on loaded skills and surfaces
- **CPU**: 1-4 cores per instance for typical workloads
- **Storage**: Minimal for the application itself, but skills may require storage for data

### Performance Optimization

1. **Surface Initialization**: Use lazy loading for heavy surfaces (Z3, Datalog)
2. **Skill Caching**: The SkillExecutor caches skill code for faster repeated execution
3. **Connection Pooling**: For surfaces that support it (database, HTTP clients)
4. **Async Processing**: Leverage async/await for I/O-bound operations
5. **Caching Layers**: Add Redis or Memcached for frequently accessed data

### Load Testing Recommendations

Use tools like `locust`, `k6`, or `wrk` to test:
- Concurrent skill execution requests
- Mixed surface workloads
- Large input data handling
- Long-running skill executions

Example k6 script:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': '__EM_CUBED_API_KEY__', // Replace with actual key or omit if not set
    },
  };

  const payload = JSON.stringify({
    skill_id: 'example-skill',
    input_data: {
      // Skill-specific input
    }
  });

  const res = http.post('http://localhost:8000/execute', payload, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });

  sleep(1);
}
```

## Monitoring and Observability

### Health Checks

Em-Cubed provides a `/health` endpoint that returns:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-16T19:14:53Z",
  "version": "0.7.0",
  "surfaces": {
    "python": true,
    "prolog": true,
    "hy": true,
    "z3": true,
    "datalog": true,
    "janus": true,
    "llm": false,
    "sqlite": true,
    "quickjs": true
  }
}
```

### Metrics Collection

Em-Cubed exposes several metrics through its telemetry system:

1. **Execution Metrics**:
   - Skill execution count (success/failure)
   - Execution time distributions
   - Surface usage statistics
   - Memory consumption per execution

2. **System Metrics**:
   - API request rates and latencies
   - Error rates
   - Active skill executions

### Logging

Structured logging is available via structlog. Configure logging in production:

```python
# In your application startup
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONFormatter()  # Production: JSON format
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

Log to a centralized system like ELK stack, Splunk, or cloud logging services.

### Tracing

For distributed tracing, integrate with OpenTelemetry or similar:
- Trace skill execution across surfaces
- Monitor cross-surface data flow
- Track performance bottlenecks

## Security Considerations

### Authentication and Authorization

- **API Authentication**: Use `EM_CUBED_API_KEY` with `X-API-Key` header
- **Skill Execution**: All skills run in the same process context - avoid executing untrusted skills
- **Surface Isolation**: Surfaces are isolated but share process memory - consider containerization for high-risk skills

### Input Validation

- All API endpoints validate input data
- Skill input schemas are validated before execution
- Surface implementations sanitize inputs where applicable

### Dependency Security

- Regularly update dependencies: `pip list --outdated` and `pip install -U`
- Use tools like `safety` or `dependabot` to monitor for vulnerabilities
- Pin exact versions in production: `pip freeze > requirements.txt`

### Network Security

- Run behind a reverse proxy (NGINX, Traefik) for TLS termination
- Implement rate limiting at the API gateway
- Use firewall rules to restrict access to necessary ports only
- Consider API gateways (Kong, AWS API Gateway) for advanced security features

### Data Protection

- Encrypt sensitive data at rest if skills persist data
- Use environment variables or secret managers for API keys
- Consider skill-level encryption for highly sensitive operations

## Maintenance and Updates

### Update Procedure

1. **Backup**: Backup current deployment state
2. **Test**: Deploy to staging environment first
3. **Verify**: Run smoke tests and integration tests
4. **Rollout**: Use rolling updates for zero-downtime deployment
5. **Monitor**: Watch metrics and logs closely after deployment

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install -U package-name

# Or update all (test thoroughly first!)
pip install -U $(pip list --outdated --format=freeze | grep -v '^-e' | cut -d = -f 1)
```

### Skill Updates

Skills can be updated without restarting the application:
- The skill registry automatically detects file changes
- Incremental indexing can be triggered via CLI: `em3 index --incremental`
- For immediate pickup, touch the SKILL.md file or restart the skill loader

## Troubleshooting in Production

### Common Issues

#### High Memory Usage
- Check for memory leaks in custom skills
- Ensure heavy surfaces are using lazy loading
- Monitor memory usage per skill execution
- Consider increasing instance size or adding more instances

#### Slow Response Times
- Check execution time metrics
- Identify slow surfaces or skills
- Optimize skill code or consider different surface choices
- Check for blocking operations in async contexts

#### Surface Availability Issues
- Verify required dependencies are installed
- Check surface health via `/health` endpoint
- Look for initialization errors in logs
- Ensure proper permissions for file access

#### Authentication Failures
- Verify `EM_CUBED_API_KEY` is set correctly
- Check that clients are sending `X-API-Key` header
- Look for authentication errors in API logs

### Diagnostic Commands

```bash
# Check surface availability
em3 surfaces

# Get skill information
em3 skill-info <skill-id>

# Run diagnostics
em3 doctor

# View logs (if using journald)
journalctl -u em-cubed -f

# Check container logs
docker logs <container-id>
```

### Emergency Procedures

If the service becomes unresponsive:
1. Check system resources (CPU, memory, disk)
2. Review recent logs for errors or patterns
3. Restart the service if necessary
4. If using orchestrator (Kubernetes, etc.), trigger a rolling restart
5. Contact on-call engineer if issue persists

## Appendix: Production Configuration Examples

### Minimal Secure Production Setup

```bash
# Environment variables
export EM_CUBED_API_KEY="$(openssl rand -base64 32)"
export EM_CUBED_TIMEOUT="30"
export EM_CUBED_LOG_LEVEL="WARNING"
export EM_CUBED_WORKERS="$(nproc)"

# Start server
gunicorn -w $EM_CUBED_WORKERS -k uvicorn.workers.UvicornWorker em_cubed.api.main:app \
    --access-logfile - \
    --error-logfile - \
    --log-level warning
```

### High-Performance Configuration

```bash
# Environment variables
export EM_CUBED_API_KEY="your-key-here"
export EM_CUBED_TIMEOUT="10"
export EM_CUBED_LOG_LEVEL="INFO"
export EM_CUBED_WORKERS="4"
export UVICORN_WORKERS="2"  # For uvicorn workers per gunicorn worker

# Start server with optimized settings
gunicorn \
    -w $EM_CUBED_WORKERS \
    -k uvicorn.workers.UvicornWorker \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 30 \
    --graceful-timeout 30 \
    em_cubed.api.main:app
```

---

For additional help, refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file or contact the Em-Cubed maintainers.