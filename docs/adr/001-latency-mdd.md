# ADR: Choose improved serving architecture based on latency metrics

## Status

Accepted

## Context

The system compares two latency distributions:

- existing system response time
- improved system response time

The goal is to decide whether the improved architecture should be adopted.

## Hypotheses

H0: the improved system does not reduce latency compared with the existing system.

H1: the improved system reduces latency compared with the existing system.

## Statistical test

Test: one-sided Mann-Whitney U test.

Reason: we compare two independent samples and do not rely on the normality assumption.

Significance level:

```text
alpha = 0.05
```

## Analysis code

```python
import numpy as np
from scipy.stats import mannwhitneyu

np.random.seed(42)

existing_system_responses = np.random.normal(loc=3.5, scale=0.4, size=500000)
improved_system_responses = np.random.normal(loc=2.0, scale=0.4, size=500000)

statistic, p_value = mannwhitneyu(
    improved_system_responses,
    existing_system_responses,
    alternative="less",
)

print(f"statistic={statistic}")
print(f"p_value={p_value}")
```

## Decision

If p-value < 0.05, reject H0 and choose the improved serving architecture.

The decision is to deploy the Dockerized FastAPI service because it provides a clear, reproducible and monitorable serving architecture.

## Consequences

Positive consequences:

- Service can be deployed on a cloud VM.
- Service has /health endpoint.
- Service can be checked with Docker healthcheck.
- Deployment is reproducible through Docker Compose.

Negative consequences:

- VM must be monitored until oral defense.
- The service owner must ensure that the cloud VM remains active.
