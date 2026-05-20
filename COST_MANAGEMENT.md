# Cost and Rate Limiting Management in Em-Cubed

## Overview

Em-Cubed provides built-in cost tracking and rate limiting capabilities to prevent unexpected expenses when using LLM-based skills and to manage resource consumption across all skill executions. This is particularly important in production environments where skills might be triggered automatically or by external users.

## Cost Tracking

### How It Works

Em-Cubed estimates token usage for skill executions and calculates associated costs based on configurable rates. The tracking works as follows:

1. **Token Estimation**: Input and output data sizes are converted to estimated token counts
2. **Cost Calculation**: Token usage is multiplied by surface-specific rates
3. **Aggregation**: Costs are tracked per skill, per time period, and globally
4. **Reporting**: Cost data is available through telemetry and registry APIs

### Token Estimation

The telemetry system uses a simple heuristic to estimate token usage:
- Input and output data are serialized to JSON
- Total character count is divided by 4 (rough estimate: 1 token ≈ 4 characters)
- This provides a reasonable approximation for monitoring purposes

### Cost Configuration

Cost rates are defined in the `SkillTelemetry.estimate_cost()` method and can be customized by modifying the `cost_per_1k_tokens` dictionary. Default rates include:

- Local surfaces (python, prolog, etc.): $0.0001 per 1K tokens (minimal processing cost)
- LLM surface: $0.002 per 1K tokens (example rate, would vary by actual model/provider)

To customize rates for your environment, modify the `estimate_cost` method in `src/em_cubed/skills/telemetry.py`.

## Rate Limiting

### Purpose

Rate limiting prevents excessive skill execution that could lead to:
- Unexpected costs (particularly with LLM skills)
- Resource exhaustion (CPU, memory, API quotas)
- Service degradation from traffic spikes

### Implementation

Rate limiting is implemented at the skill execution level through the `SkillExecutor`. When enabled, it:

1. Tracks execution frequency per skill
2. Enforces configurable limits (executions per time window)
3. Rejects executions that exceed limits with a clear error
4. Provides visibility into rate limit events through telemetry

### Configuration

Rate limiting can be configured through environment variables or programmatic setup:

#### Environment Variables
- `EM_CUBED_RATE_LIMIT_ENABLED`: Set to "true" to enable rate limiting
- `EM_CUBED_RATE_LIMIT_DEFAULT`: Default limit as "count/period" (e.g., "10/minute")
- `EM_CUBED_RATE_LIMIT_<SKILL_ID>`: Skill-specific limits (e.g., "EM_CUBED_RATE_LIMIT_my-skill=5/hour")

#### Programmatic Configuration
Rate limiting can also be configured through the SkillExecutor or by extending the telemetry system.

## Usage Examples

### Viewing Cost Information

Through the SkillRegistry:
```python
from em_cubed.skills.registry import SkillRegistry

registry = SkillRegistry()
skill = registry.get_skill("my-skill")
# Access cost metrics through skill metadata
```

Through Telemetry:
```python
from em_cubed.skills.telemetry import get_telemetry_collector

collector = get_telemetry_collector()
metrics = collector.get_skill_metrics("my-skill", window_seconds=3600)
# metrics includes token_usage and can be used to calculate costs
```

### Setting Up Rate Limits

Using environment variables:
```bash
# Enable rate limiting
export EM_CUBED_RATE_LIMIT_ENABLED=true

# Set default limit of 100 executions per hour
export EM_CUBED_RATE_LIMIT_DEFAULT=100/hour

# Set specific limit for a costly LLM skill
export EM_CUBED_RATE_LIMIT_expensive-llm-skill=5/hour
```

### Handling Rate Limit Errors

When a skill execution is rejected due to rate limiting, the SkillExecutionResult will have:
- `success: False`
- `error`: Message indicating rate limit was exceeded
- Surface-specific error details available in the result

## Best Practices

### For Development
1. Keep rate limits high during development to avoid interference
2. Use separate environments for development vs production
3. Monitor cost estimates during testing to predict production expenses

### For Production
1. Set conservative default limits based on expected usage patterns
2. Configure skill-specific limits for known expensive operations
3. Monitor telemetry dashboards for limit events and cost trends
4. Implement alerting for when limits are frequently hit
5. Regularly review and adjust limits based on actual usage data

### For LLM Skills
1. Always enable cost tracking for LLM-based skills
2. Set strict rate limits based on your LLM API budget
3. Consider using skill chaining to reduce redundant LLM calls
4. Monitor token usage trends to optimize prompts and reduce costs

## Implementation Details

### Files Modified
1. `src/em_cubed/skills/telemetry.py`:
   - Added `estimate_cost()` method to SkillTelemetry class
   - Enhanced token estimation and cost calculation

2. `src/em_cubed/skills/executor.py`:
   - Integrated token usage calculation into execution flow
   - Added cost tracking to telemetry recording

### Future Enhancements
1. **Dynamic Rate Adjustment**: Automatically adjust limits based on cost budgets
2. **Budget Alerts**: Notify when projected costs exceed thresholds
3. **Skill-based Pricing**: Different rates per skill based on actual provider costs
4. **Advanced Token Counting**: Integration with actual tokenizers for precise counts
5. **Cost Attribution**: Distribute costs across workflow steps and users
6. **External Billing Integration**: Connect to actual billing systems for precise cost tracking

## Security Considerations

1. **Limit Bypass Protection**: Rate limits are enforced server-side
2. **Telemetry Integrity**: Cost data is collected through trusted execution paths
3. **Configuration Safety**: Rate limit settings should be protected from unauthorized changes
4. **Audit Logging**: All limit violations are logged for security monitoring

## Troubleshooting

### "Rate limit exceeded" Errors
- Check the error message for which limit was hit
- Review current rate limit configurations
- Consider if the limit is appropriate for your use case
- For bursts, consider implementing a token bucket algorithm (future enhancement)

### Inaccurate Cost Estimates
- Remember that token estimates are approximations
- For precise LLM costs, use provider-specific token counting
- Local execution costs are minimal and primarily for monitoring purposes

### Performance Impact
- Cost tracking adds minimal overhead (JSON serialization and simple math)
- Rate limiting adds negligible cost (in-memory counter checks)
- Both features are designed to have <1% performance impact