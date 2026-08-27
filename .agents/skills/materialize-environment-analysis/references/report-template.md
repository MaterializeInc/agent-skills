# Report Template

The shape of the analysis report SKILL.md's Step 4 produces. Fill every
section from the queries in `queries.md`; the Cluster Topology table comes
from the `Cluster Topology` query there plus the credit columns of
`Current Compute Cost per Cluster`.

```markdown
# Environment Analysis

**Date**: <date>
**Materialize Version**: <version>

## Executive Summary
<2-3 paragraph high-level assessment>

## Cluster Topology
| Cluster | Size | Replicas | Credits/Hr | Monthly Credits | Utilization |

## Deployed Objects
### Sources (<count>)
### Materialized Views (<count>)
### Sinks (<count>)
### Indexes (<count>)

## Performance Analysis
### Freshness
### Hydration
### Cluster Utilization
### Worker Skew
### Source and Sink Health

## Cost Analysis (if requested)

## Index Advice Summary

## SQL-Level Analysis
### Materialized View Definitions
### Index Analysis

## Optimization Recommendations
<numbered list with specific SQL for each>
```
