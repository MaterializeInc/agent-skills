# FAQ: Indexes
Frequently asked questions about indexes.
## Are indexes in Materialize optimized for `ORDER BY`?

No.

The index data is distributed across the cluster's
workers by a hash of the key, which spreads the maintenance and lookup work
across the cluster.

Within each worker, index keys are ordered by their internal representation
(the encoded key's length, then its bytes), not by the data types' natural
ordering.

As such, Materialize indexes are not optimized for ordered access, including
`ORDER BY` clauses.

## Are indexes in Materialize optimized for range queries?

No.

The index data is distributed across the cluster's
workers by a hash of the key, which spreads the maintenance and lookup work
across the cluster.

Within each worker, index keys are ordered by their internal representation
(the encoded key's length, then its bytes), not by the data types' natural
ordering.

As such, Materialize indexes are not optimized for ordered access, including
range queries.

## Are indexes in Materialize optimized for `GROUP BY` aggregations?

No. An index on the grouping key does not reduce the work of computing the aggregation: Materialize reads the full index and maintains the aggregation separately.
