# Concepts

Learn about the core concepts in Materialize.

The pages in this section introduces some of the key concepts in Materialize:

Concept                                  | Description
-----------------------------------------|-----
[Clusters](/fundamentals/concepts/clusters/)          | Clusters are isolated pools of compute resources for sources, sinks, indexes, materialized views, and ad-hoc queries.
[Sources](/fundamentals/concepts/sources/)            | Sources describe an external system you want Materialize to read data from.
[Views](/fundamentals/concepts/views/)    | Views represent a named query that you want to save for repeated execution. You can use **indexed views** and **materialized views** to incrementally maintain the results of views.
[Indexes](/fundamentals/concepts/indexes/)            | Indexes represent query results stored in memory.
[Arrangements](/fundamentals/concepts/arrangements/) | Arrangements are the in-memory data structures that maintain indexes and materialized views.
[Sinks](/fundamentals/concepts/sinks/)                | Sinks describe an external system you want Materialize to write data to.
[Snapshotting](/fundamentals/concepts/snapshotting/) | The initial sync of a source's data from an upstream system, before the source can serve queries.
[Hydration](/fundamentals/concepts/hydration/) | Hydration is the reconstruction of an object's in-memory state by reading
from Materialize's storage layer and existing indexes; hydration does not
read from the upstream system.

[Reaction Time](/fundamentals/concepts/reaction-time) | Measures how quickly a system can reflect a change in input data and return an up-to-date query result. Defined as the sum of data freshness and query latency.

Refer to the individual pages for more information.

## Pages in this section

- [Namespaces](/fundamentals/concepts/namespaces/index.md): Logical namespaces for organizing objects in Materialize.
- [Arrangements](/fundamentals/concepts/arrangements/index.md): Understand how Materialize arrangements work.
- [Clusters](/fundamentals/concepts/clusters/index.md): Learn about clusters in Materialize.
- [Hydration](/fundamentals/concepts/hydration/index.md): Learn about hydration in Materialize: reconstructing an object's in-memory state by reading from the storage layer.
- [Indexes](/fundamentals/concepts/indexes/index.md): Learn about indexes in Materialize.
- [Reaction Time, Freshness, and Query Latency](/fundamentals/concepts/reaction-time/index.md): Learn about freshness, query latency, and reaction time, and how they determine how current and how fast query results are in Materialize.
- [Sinks](/fundamentals/concepts/sinks/index.md): Learn about sinks in Materialize.
- [Snapshotting](/fundamentals/concepts/snapshotting/index.md): Learn about snapshotting in Materialize: the initial sync of a source's data from an upstream system.
- [Sources](/fundamentals/concepts/sources/index.md): Learn about sources in Materialize.
- [Views](/fundamentals/concepts/views/index.md): Learn about views in Materialize.
