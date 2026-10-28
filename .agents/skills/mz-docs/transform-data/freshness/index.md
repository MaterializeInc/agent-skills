# Freshness

Guides for tuning, monitoring, and troubleshooting data freshness in Materialize.

[Freshness](/fundamentals/concepts/reaction-time/#freshness) measures the time
from when a change occurs in an upstream system to when it becomes visible in
the results of a query. These guides can help you tune, track, and diagnose it:

- [Fine tune for sub-second freshness](/transform-data/freshness/subsecond-freshness/)
- [Monitor freshness](/transform-data/freshness/monitor-freshness/)
- [Troubleshoot freshness](/transform-data/freshness/troubleshoot-freshness/)

## Pages in this section

- [Fine tune for sub-second freshness](/transform-data/freshness/subsecond-freshness/index.md): How to lower the tick rate to get sub-second freshness, and how to verify it by measuring end-to-end latency.
- [Freshness troubleshooting](/transform-data/freshness/troubleshoot-freshness/index.md): How to diagnose and resolve freshness problems in Materialize.
- [How to monitor freshness in Materialize](/transform-data/freshness/monitor-freshness/index.md): How to monitor data freshness across your environment and for specific objects in Materialize.
