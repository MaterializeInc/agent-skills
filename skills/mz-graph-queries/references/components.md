# Connected components and strongly connected components

Patterns that partition a graph instead of walking it: which nodes belong to
the same undirected component, which records are the same entity once a match
score passes a threshold, and which nodes sit inside the same directed cycle.
Read this file to answer: how do I group a link graph into clusters, what is
the golden-record id for a cluster, why did raising the threshold merge two
clusters, which accounts are in the same money loop, and how do I compute
strongly connected components without materializing the transitive closure.

Fixture tables used: `customers`, `customer_links`, `accounts`, `transfers`.
Every block assumes `references/fixture.sql` is loaded.

`customer_links` holds each pair once, in one direction, with a match score:
(c1, c2, 0.9), (c2, c3, 0.8), (c1, c3, 0.95), (c4, c5, 0.7), (c5, c6, 0.4).
c7 appears in no link at all. The fixture's transfers form a ring, a1 to a2 to
a3 and back to a1, with a3 to a4 to a5 hanging off it and a separate a6 to a7.
Those three ring accounts are the only strongly connected component with more
than one member.

Components and reachability are different questions. Reachability asks what one
node can get to, following edges in the direction they point
([reachability.md](reachability.md)). A component is an equivalence class: every
member sees the same answer, so the output is one label per node rather than one
set per node.

## Connected components by min-label propagation

Every node starts labelled with its own id and keeps the smallest label any
neighbor offers.

```sql
WITH MUTUALLY RECURSIVE
    links(a text, b text) AS (
        SELECT a, b FROM customer_links WHERE score >= 0.5
        UNION
        SELECT b, a FROM customer_links WHERE score >= 0.5
    ),
    label(id text, comp text) AS (
        SELECT id, min(comp)
        FROM (
            SELECT id, id FROM customers
            UNION ALL
            SELECT l.b, lb.comp
            FROM links l JOIN label lb ON lb.id = l.a
        ) AS x(id, comp)
        GROUP BY id
    )
SELECT id, comp FROM label ORDER BY id;
```

On the fixture this returns c1, c2 and c3 labelled c1; c4 and c5 labelled c4;
c6 labelled c6; c7 labelled c7. The c5 to c6 link scores 0.4 and does not pass
the threshold, so c6 stands alone. c7 has no link at all and still gets a row,
because the seed branch reads the node table.

It converges because a node's label never rises. Iteration one gives every node
its own id, every later iteration takes a `min` over the previous labels, and
the values are bounded below by the smallest id in the component. The id domain
is finite and the row set is fixed at one row per node from the first iteration,
so the loop stops after roughly as many iterations as the component's diameter.

That fixed row set is also why a recursion limit is not the guardrail here. A
reduce-topped binding stops raising `ERROR AT RECURSION LIMIT` once its keys
have settled, and these keys settle immediately
([semantics.md#recursion-limits](semantics.md#recursion-limits)). Nothing is
lost: this shape cannot diverge, because a value that only descends toward a
floor has nowhere to go.

Four choices carry the whole pattern.

| Choice | Why |
|---|---|
| `min` inside the binding | State stays at one row per node. Outside, the binding would have to hold every (node, reachable node) pair first |
| `links` as a leading non-recursive binding | It has no self-reference, so it is hoisted out and symmetrized once instead of per iteration ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)) |
| Threshold inside `links` | A predicate in the body is not pushed into the recursion ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)) |
| Seed from `customers` | An edge-derived seed silently drops isolated nodes such as c7 |

The `UNION` in `links` symmetrizes: an edge stored as (c1, c2) has to be
readable as (c2, c1) too, or the recursion propagates labels in one direction
only and reports forward reachability sets under the name "components". This
fixture hides that bug, because every link happens to point from the smaller id
to the larger one, and the label already flows the way `min` wants it to. A
three-node graph shaped like a V exposes it:

```sql
WITH MUTUALLY RECURSIVE
    links(a text, b text) AS (
        SELECT a, b FROM (VALUES ('n2', 'n1'), ('n2', 'n3')) AS v(a, b)
    ),
    label(id text, comp text) AS (
        SELECT id, min(comp)
        FROM (
            SELECT a, a FROM links
            UNION ALL
            SELECT b, b FROM links
            UNION ALL
            SELECT l.b, lb.comp FROM links l JOIN label lb ON lb.id = l.a
        ) AS x(id, comp)
        GROUP BY id
    )
SELECT id, comp FROM label ORDER BY id;
```

This returns n1 labelled n1, n2 labelled n2 and n3 labelled n2. The three nodes
form one undirected component and the query reports two, because no edge points
into n2. Restoring the `UNION` that flips every edge fixes it.

Standard SQL brings a different algorithm, not a different dialect of this one.
`WITH RECURSIVE` forbids an aggregate in the recursive term
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)),
so a Postgres or SQL Server user computes the undirected reachable set of every
node and then takes `MIN(reached)` per node in the outer query. It gives the
same labels. It gets there by materializing one row per ordered pair inside a
component, so a component of k nodes costs k squared rows before the aggregate
runs, and a single component of 100,000 records is ten billion rows. Moving
`min` inside the binding is the whole optimization.

## The threshold changes the answer

The same query at a lower cutoff, looking only at the c4 cluster:

```sql
WITH MUTUALLY RECURSIVE
    links(a text, b text) AS (
        SELECT a, b FROM customer_links WHERE score >= 0.3
        UNION
        SELECT b, a FROM customer_links WHERE score >= 0.3
    ),
    label(id text, comp text) AS (
        SELECT id, min(comp)
        FROM (
            SELECT id, id FROM customers
            UNION ALL
            SELECT l.b, lb.comp
            FROM links l JOIN label lb ON lb.id = l.a
        ) AS x(id, comp)
        GROUP BY id
    )
SELECT id, comp FROM label WHERE id IN ('c4', 'c5', 'c6') ORDER BY id;
```

This returns c4, c5 and c6 all labelled c4. Dropping the cutoff from 0.5 to 0.3
admits the c5 to c6 link, and c6 stops being its own component.

Convergence is unchanged. The threshold only removes edges from the relation the
binding reads, and a recursion that terminates on a graph terminates on every
subgraph of it.

Notice what c6 joined. There is no link between c4 and c6 at any score, and the
0.4 link to c5 is the weakest edge in the fixture. A component is transitive by
construction, so one marginal edge merges two clusters entirely. That is the
single most surprising property of this query for the people who ask for it, and
it is not a bug to be fixed by a better threshold. Thresholding an edge score is
a decision about edges; components are the consequence.

Standard SQL brings the same `WHERE score >= 0.3` and the same consequence. The
one Materialize-specific point is placement: the filter belongs in the `links`
binding, because a `WHERE score >= 0.3` in the body of the recursive query would
run after the recursion had already propagated labels across every edge
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

## Entity resolution, clusters and golden records

When `customer_links` holds pairwise match scores from a matching engine, this
query is the clustering step of entity resolution. The threshold is the match
cutoff, the component is the cluster of records believed to be one person, and
the label is the golden-record id. The deliverable is usually the cluster, not
the per-record label:

```sql
WITH MUTUALLY RECURSIVE
    links(a text, b text) AS (
        SELECT a, b FROM customer_links WHERE score >= 0.5
        UNION
        SELECT b, a FROM customer_links WHERE score >= 0.5
    ),
    label(id text, comp text) AS (
        SELECT id, min(comp)
        FROM (
            SELECT id, id FROM customers
            UNION ALL
            SELECT l.b, lb.comp
            FROM links l JOIN label lb ON lb.id = l.a
        ) AS x(id, comp)
        GROUP BY id
    )
SELECT comp AS golden_id, count(*) AS members, string_agg(id, ',' ORDER BY id) AS ids
FROM label
GROUP BY comp
ORDER BY comp;
```

On the fixture this returns four clusters: c1 with three members (c1, c2, c3),
c4 with two (c4, c5), and c6 and c7 alone. Singletons are clusters too, which is
what makes this the record master rather than a list of duplicates.

It converges for the reason the first block does; the `GROUP BY` runs once in
the body, at the fixpoint. In a maintained view the recursion is where an
incoming match score does its work, and the aggregate only reshapes the
fixpoint into one row per cluster.

Three things go wrong in production, and none of them is a Materialize problem.

| Trap | What happens | What to do |
|---|---|---|
| Transitive chaining | A matches B, B matches C, C matches Z, and A is now the same person as Z. The previous section merges c6 into c4's cluster through one 0.4 edge | Raise the cutoff, or require a stronger structure than connectivity |
| Unstable golden ids | `min(id)` is the smallest id present now. A new record with a smaller id relabels every member of its cluster, and every downstream key that referenced the old label | Propagate `min` over a value that only grows, such as the oldest record's id or a surrogate assigned at first sight, and never over a raw uuid |
| Cliques expected | Users hear "cluster" and picture every member matching every other member. A component only promises a path | Report the cluster size and the weakest edge in it next to the cluster, so a chain is visible |

Standard SQL brings the reach-set-then-`MIN` shape from the first section, and
entity resolution is where its cost lands hardest. The reason to cluster at all
is that the record set is large, and the pair count inside a single runaway
cluster is what breaks the job. The other change is that a `WITH RECURSIVE`
clustering is a batch job rerun on a schedule, while this binding in a
materialized view reclusters as scores arrive.

## Strongly connected components from the closure

On a directed graph, "connected" has two readings. Weak connectivity is the
previous sections, applied to the symmetrized edges. Strong connectivity asks
which nodes can reach each other both ways, which is the question behind circular
payments, cyclic dependencies and mutual ownership. Given the transitive closure,
it is a self-join:

```sql
CREATE VIEW scc_closure AS
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    reach(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON t.src = r.dst
    )
SELECT a.id, least(a.id, min(m.dst)) AS component
FROM accounts a
LEFT JOIN (
    SELECT r1.src, r1.dst
    FROM reach r1 JOIN reach r2 ON r1.src = r2.dst AND r1.dst = r2.src
) m ON m.src = a.id
GROUP BY a.id;
```

```sql
SELECT id, component FROM scc_closure ORDER BY id;
```

The read returns a1, a2 and a3 labelled a1, and a4 through a7 each labelled with
themselves. a4 and a5 are reachable from the ring and cannot reach it back, so
they are their own components; a6 and a7 are in a different weak component
entirely and are still two separate strong components.

It converges because `reach` is the ordinary closure binding, whose termination
does not depend on the graph being acyclic
([reachability.md#whole-graph-closure](reachability.md#whole-graph-closure)):
pairs are drawn from a finite set, `UNION` makes a re-derived pair a no-op, and
the relation only grows. Everything after the binding runs once at the fixpoint.
Because the top of the binding is a `UNION` and not a reduce, every change it
can make is a row change, so `ERROR AT RECURSION LIMIT 100` here is a real
guardrail rather than a decoration
([semantics.md#recursion-limits](semantics.md#recursion-limits)).

Three details in the body are load-bearing. The `LEFT JOIN` keeps accounts with
no mutual partner, which is most of them. `least(a.id, min(m.dst))` handles
those accounts without a `coalesce`: `min` over an empty group is null, and
`least` ignores nulls, so a singleton falls back to its own id. That is what the
a4 through a7 rows show. And the seed of `reach` is the edge table rather than a
reflexive (id, id) row, so a mutual pair means a genuine cycle through the node
and not the identity.

Use this form when the closure is wanted for its own sake, or when the graph is
small. It costs a relation that approaches the square of the node count, and
then joins that relation to itself. A 100,000-account graph with one large
strongly connected component cannot hold the intermediate result, and no amount
of filtering in the body helps, because the filter is not pushed in.

Standard SQL brings exactly this query, with `WITH RECURSIVE reach(src, dst)`
and `UNION`, and no way to do better. The closure is the only strongly connected
component algorithm expressible in a single `WITH RECURSIVE` term, because the
alternatives need either an aggregate inside the recursion or two mutually
dependent relations, and standard SQL forbids both
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)).
The next section is the query a Postgres user cannot write.

## Strongly connected components without the closure

Trim the edge set instead of closing it. Two nested label propagations run over
the surviving edges, one forward and one backward, and an edge survives only if
its endpoints agree on both labels.

```sql
CREATE VIEW scc_trim AS
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    intra(src text, dst text) AS (
        SELECT src, dst FROM transfers
        EXCEPT ALL
        SELECT src, dst FROM transfers_delayed
        UNION ALL
        SELECT t.src, t.dst
        FROM transfers t
        JOIN fwd f_src ON f_src.node = t.src
        JOIN fwd f_dst ON f_dst.node = t.dst
        JOIN bwd b_src ON b_src.node = t.src
        JOIN bwd b_dst ON b_dst.node = t.dst
        WHERE f_src.label = f_dst.label AND b_src.label = b_dst.label
    ),
    fwd(node text, label text) AS (
        WITH MUTUALLY RECURSIVE
            l(node text, comp text) AS (
                SELECT node, min(comp)
                FROM (
                    SELECT id, id FROM accounts
                    UNION ALL
                    SELECT i.dst, l.comp FROM intra i JOIN l ON l.node = i.src
                ) AS x(node, comp)
                GROUP BY node
            )
        SELECT node, comp FROM l
    ),
    bwd(node text, label text) AS (
        WITH MUTUALLY RECURSIVE
            l(node text, comp text) AS (
                SELECT node, min(comp)
                FROM (
                    SELECT id, id FROM accounts
                    UNION ALL
                    SELECT i.src, l.comp FROM intra i JOIN l ON l.node = i.dst
                ) AS x(node, comp)
                GROUP BY node
            )
        SELECT node, comp FROM l
    ),
    transfers_delayed(src text, dst text) AS (SELECT src, dst FROM transfers)
SELECT node, label AS component FROM fwd;
```

```sql
SELECT node, component FROM scc_trim ORDER BY node;
```

The read returns the same seven rows as `scc_closure`: a1, a2 and a3 labelled
a1, and a4 through a7 labelled with themselves.

The mechanism is one round of seeding followed by rounds of trimming.

| Round | `transfers_delayed` | `intra` after the update |
|---|---|---|
| 1 | empty | every transfer: the seed survives `EXCEPT ALL`, and `fwd` and `bwd` are still empty so the second branch produces nothing |
| 2 and after | all transfers | the seed cancels, and only edges whose endpoints share a forward label and a backward label survive |

The delay idiom is what makes round one different from every later round
([semantics.md#binding-order-and-the-delay-idiom](semantics.md#binding-order-and-the-delay-idiom)).
`transfers_delayed` is defined after `intra`, so `intra` reads its previous
value, which is empty on the first pass. Without it the full edge set would be
re-added every round and nothing would ever be trimmed.

Sharing a forward label means both endpoints are reachable from the same
smallest-id node; sharing a backward label means both reach it. Two nodes with
the same pair of labels are therefore mutually reachable, which is exactly
membership in one strongly connected component, and an edge between them is an
intra-component edge. Those are the edges the loop keeps, and they are
recoverable from the view:

```sql
SELECT t.src, t.dst
FROM transfers t
JOIN scc_trim a ON a.node = t.src
JOIN scc_trim b ON b.node = t.dst
WHERE a.component = b.component
ORDER BY t.src, t.dst;
```

This returns the three ring edges, a1 to a2, a2 to a3 and a3 to a1. The three
edges whose endpoints sit in different components, a3 to a4, a4 to a5 and a6 to
a7, are gone.

The outer loop converges because `intra` only shrinks after round one. Fewer
edges give coarser labels, coarser labels admit fewer edges, and the edge set is
finite, so the sequence is monotone decreasing and has a fixpoint. Each nested
block converges by the min-label argument of the first section. The outer
`ERROR AT RECURSION LIMIT 100` does see this loop's progress, because the outer
loop's changes are edges leaving `intra`, and those are row changes. On this
fixture the outer loop reaches its fixpoint in two rounds, and the same block
written with `ERROR AT RECURSION LIMIT 1` raises where `2` returns the answer.

The two forms agree on every account:

```sql
SELECT count(*) AS disagreements
FROM scc_closure c FULL OUTER JOIN scc_trim t ON c.id = t.node
WHERE c.id IS NULL OR t.node IS NULL OR c.component <> t.component;
```

This returns 0.

What the trimming form buys is that no relation here is larger than the edge
table. Nothing quadratic is ever built, so it is the form for a graph too large
to close. What it costs is iterations: the nested propagations rerun from
scratch on every outer round, and each one takes iterations proportional to the
diameter of what is left. On a small or a nearly acyclic graph the closure form
is both shorter and faster; on a large graph it is the one that does not fit.

Both views above are plain views, so nothing runs until they are read. Adding
`MATERIALIZED` to either one installs and hydrates on v26.38.1, nested recursive
block included, and then maintains the labels as transfers arrive: inserting a
transfer from a5 back to a3 closes a larger loop, and both maintained views
relabel a4 and a5 into a1's component without being recomputed.

Note where a nested block is allowed to go: derived-table position, as `fwd` and
`bwd` use it here. The scalar-subquery form aborts `environmentd` on this
version
([semantics.md#pitfalls](semantics.md#pitfalls)).

Standard SQL brings nothing here. `WITH RECURSIVE` permits one recursive
relation with one self-reference, no aggregate in the recursive term and no
nested recursive block, and this query needs three mutually dependent relations,
a `min` inside two of them, and a recursion inside a recursion. A Postgres user
who needs strongly connected components on a graph too large to close writes it
in a procedural language, or pulls the edges out to a graph library.

## Pitfalls

- Forgetting to symmetrize. `label` then propagates in one direction and returns
  forward reachability sets under the name "components". The fixture will not
  tell you: its links all point from the smaller id to the larger one, so the
  wrong query gives the right answer on it. The V-shaped block above is the
  smallest case that fails.
- Symmetrizing a relation that is directed on purpose. "Paid", "reports to",
  "depends on" and "follows" are not symmetric, and flipping them merges every
  node a payment ever reached into one cluster. Symmetrize a similarity or a
  co-occurrence; leave a flow alone.
- `min(id)` as a durable cluster key. It is the smallest id in the cluster
  today. One new record with a smaller id relabels every member, and every
  join key downstream that stored the old label is now wrong. Propagate a value
  that only grows, or map the component to a surrogate once and keep it.
- Saying "connected" on a directed graph without saying which. Weak
  connectivity symmetrizes first and answers "same island". Strong connectivity
  answers "same cycle". On the fixture's transfers they differ: a1 through a5
  are one weak component and three strong ones.
- Expecting a component to be a clique. A component only promises a path, so a
  chain of weak links is one cluster. Raising the threshold does not change
  that; it changes which chain.
- Asking for cycles when the need is strongly connected components. A single
  strongly connected component can contain exponentially many simple cycles, so
  the enumeration is unbounded where the partition is one row per node. "Which
  accounts are in a money loop" is this file; "list the loops" usually is not
  the question.
- Adding `ERROR AT RECURSION LIMIT` to a label binding and calling it guarded.
  The row set of a min-propagation is fixed from the first iteration, so the
  limit has no row change to notice
  ([semantics.md#recursion-limits](semantics.md#recursion-limits)). The
  propagation cannot diverge, so nothing is lost, but the limit is not what is
  protecting you.
- The closure form on a dense graph. `reach` approaches the square of the node
  count and is then joined to itself. Use the trimming form when the closure
  will not fit ([reachability.md#whole-graph-closure](reachability.md#whole-graph-closure)).
- Filtering the component table in the body to "only look at one cluster". The
  recursion still labels the whole graph, because predicates are not pushed into
  a recursive binding
  ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
  Filter the edges instead, as the threshold does.
- Seeding `label` from the edge table. Isolated nodes vanish, and in entity
  resolution the isolated nodes are the records that matched nothing, which are
  exactly the ones a record master has to keep.
