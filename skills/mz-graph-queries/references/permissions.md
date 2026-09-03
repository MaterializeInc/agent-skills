# Permissions and access control

Patterns for authorization data: a permission granted on a group and inherited
by everything under it, an explicit grant lower down that overrides what it
inherited, a per-user view Materialize keeps current so a check is an index
lookup, denies, and relationship-based access in the Zanzibar shape. Read this
file to answer: what does this group actually grant, what does this user
actually have, how do I make "can u1 read doc1" cheap, how do I express a deny
that stops inheritance below it, and how do I evaluate relation tuples over an
object graph.

Fixture tables used: `groups`, `memberships`, `permissions`. Every block
assumes `references/fixture.sql` is loaded.

The fixture's group tree is g1 over g2 and g4, and g2 over g3. `permissions`
grants g1 `read` on doc1, g2 `edit` on doc2, and g3 `edit` on doc1. Membership
puts u1 in g3, u2 in g4, and u3 in g2. The override rule throughout this file
is nearest explicit wins: a group's own row for a document replaces whatever it
would have inherited, for that group and for everything below it.

## Inheritance down a group tree with overrides

```sql
WITH MUTUALLY RECURSIVE
    effective(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM permissions
        UNION
        SELECT g.id, e.doc_id, e.level
        FROM groups g JOIN effective e ON e.group_id = g.parent_id
        WHERE NOT EXISTS (
            SELECT 1 FROM permissions p
            WHERE p.group_id = g.id AND p.doc_id = e.doc_id
        )
    )
SELECT group_id, doc_id, level FROM effective ORDER BY group_id, doc_id;
```

On the fixture this returns g1 doc1 read; g2 doc1 read; g2 doc2 edit; g3 doc1
edit; g3 doc2 edit; g4 doc1 read. g3 inherits doc2 from g2 but keeps its own
`edit` on doc1 instead of g1's `read`, and the override applies at g3 only:
g4, on the other branch, still gets `read`.

It converges because the `NOT EXISTS` reads the base table `permissions`, not
the binding. `permissions` does not change while the loop runs, so the
recursive term is monotone in `effective`: the binding only ever grows, `UNION`
makes re-deriving a row a no-op, and the `(group_id, doc_id, level)` triples
are drawn from finite columns. That holds on any group graph, cycles included,
which the next section demonstrates. Write the same override as a `NOT EXISTS`
over `effective` and the recursion stops being monotone; WMR will let you
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)),
but nothing then guarantees a fixpoint.

Putting the override test inside the binding is the whole point. It stops
inheritance at the overriding group and therefore for everything below it,
because the row that would have been passed down is never derived in the first
place.

Standard SQL brings the same query. Postgres accepts this recursive term:
its restriction is that the recursive relation may not appear inside a
subquery, and here the subquery reads `permissions`, so `WITH RECURSIVE
effective AS (...)` with the identical body is legal. What changes is
`RECURSIVE` becoming `MUTUALLY RECURSIVE`, the declared column list
`effective(group_id text, doc_id text, level text)`, and what you can do with
the result: the next section but one turns it into a view Materialize keeps
current, where Postgres reruns it per request or caches it and invalidates the
cache by hand. The alternative a Postgres user often reaches for, expanding
every inherited row and resolving overrides in an outer query, needs a distance
column and an argmin per `(group, doc)` to know which explicit ancestor is
nearest, which is both more work and divergent on the graph in the next
section.

## Multiple parents and cycles

Group graphs are usually described as trees and are usually not. A group with
two parent rows inherits from both, and a chain of nesting can close on itself.
These blocks use inline data so the fixture stays a tree. In it d3 has two
parents, d1 and d2, which grant different levels on the same document; d4 hangs
under d3, and d3 also lists d4 as a parent, closing a cycle.

```sql
WITH MUTUALLY RECURSIVE
    dag(id text, parent_id text) AS (
        SELECT id, parent_id FROM (VALUES
            ('d1', NULL), ('d2', NULL),
            ('d3', 'd1'), ('d3', 'd2'),
            ('d4', 'd3'), ('d3', 'd4')) AS v(id, parent_id)
    ),
    grants(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM (VALUES
            ('d1', 'docX', 'read'),
            ('d2', 'docX', 'edit')) AS v(group_id, doc_id, level)
    ),
    effective(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM grants
        UNION
        SELECT g.id, e.doc_id, e.level
        FROM dag g JOIN effective e ON e.group_id = g.parent_id
        WHERE NOT EXISTS (
            SELECT 1 FROM grants p
            WHERE p.group_id = g.id AND p.doc_id = e.doc_id
        )
    )
SELECT group_id, doc_id, level FROM effective ORDER BY group_id, doc_id, level;
```

This returns d1 docX read; d2 docX edit; d3 docX edit; d3 docX read; d4 docX
edit; d4 docX read. It terminates despite the cycle, and it shows the other
half of the problem: d3 holds two rows for one document because its two parents
disagree, and d4 inherits both. `UNION` deduplicates identical rows, not
conflicting ones. Decide which level wins and apply that decision in the body,
not in the binding, because "keep the strongest level per key" is non-monotone
and does not belong inside a fixpoint.

It converges for the reason the previous section gives: no column counts, so
every extra lap around the cycle re-derives a triple the binding already holds.
`dag` and `grants` are non-recursive leading bindings, computed once outside
the loop
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

`UNION ALL` on the same data never converges:

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    dag(id text, parent_id text) AS (
        SELECT id, parent_id FROM (VALUES
            ('d1', NULL), ('d2', NULL),
            ('d3', 'd1'), ('d3', 'd2'),
            ('d4', 'd3'), ('d3', 'd4')) AS v(id, parent_id)
    ),
    grants(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM (VALUES
            ('d1', 'docX', 'read'),
            ('d2', 'docX', 'edit')) AS v(group_id, doc_id, level)
    ),
    effective(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM grants
        UNION ALL
        SELECT g.id, e.doc_id, e.level
        FROM dag g JOIN effective e ON e.group_id = g.parent_id
        WHERE NOT EXISTS (
            SELECT 1 FROM grants p
            WHERE p.group_id = g.id AND p.doc_id = e.doc_id
        )
    )
SELECT group_id, doc_id, level FROM effective;
```

`ERROR:  Evaluation error: Recursive query exceeded the recursion limit 20.`
The distinct triples settled after three iterations, but every lap through
d3 to d4 to d3 adds another copy of each, so the multiplicities climb forever.
The limit is what makes that visible; without one the statement runs until it
is cancelled
([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).
This binding is topped by a union rather than a reduce, so every change it
makes is a row change and `ERROR AT RECURSION LIMIT` always fires
([semantics.md#recursion-limits](semantics.md#recursion-limits)).

Standard SQL brings the same two outcomes: `WITH RECURSIVE ... UNION` also
deduplicates against the accumulated result and terminates, and `UNION ALL`
also runs forever. Postgres 14 and later offers a `CYCLE` clause to detect the
loop instead; Materialize has neither that nor the `RECURSIVE` keyword, so
`UNION` over a binding that carries no counter is the tool
([hierarchies.md#cycles-in-a-tree](hierarchies.md#cycles-in-a-tree)).

## Per user, and a point check

An authorization service does not want the whole expansion. It wants one
question answered in a millisecond, over and over, against data that keeps
changing. Put the recursion in a view and index it.

```sql
CREATE VIEW user_access AS
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    effective(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM permissions
        UNION
        SELECT g.id, e.doc_id, e.level
        FROM groups g JOIN effective e ON e.group_id = g.parent_id
        WHERE NOT EXISTS (
            SELECT 1 FROM permissions p
            WHERE p.group_id = g.id AND p.doc_id = e.doc_id
        )
    )
SELECT DISTINCT m.user_id, e.doc_id, e.level
FROM memberships m JOIN effective e ON e.group_id = m.group_id;

CREATE INDEX user_access_by_user_doc ON user_access (user_id, doc_id);
```

The `CREATE INDEX` is what makes this a maintained dataflow. A plain
`CREATE VIEW` is a named query and nothing more; with the index in place the
expansion is computed once and kept up to date as `groups`, `memberships` and
`permissions` change
([hierarchies.md#a-maintained-closure-table](hierarchies.md#a-maintained-closure-table)).
`ERROR AT RECURSION LIMIT 100` is the guardrail every maintained recursive view
needs: without it a bad group graph leaves a view that installs, never
hydrates, and spins a dataflow until it is dropped
([semantics.md#recursion-limits](semantics.md#recursion-limits)).

```sql
SELECT user_id, doc_id, level FROM user_access ORDER BY 1, 2, 3;
```

On the fixture this returns u1 doc1 edit; u1 doc2 edit; u2 doc1 read; u3 doc1
read; u3 doc2 edit. u1 sits in g3 and gets g3's override on doc1 plus g2's
grant on doc2; u2 sits in g4 and gets only what g1 hands down; u3 sits in g2.

The question the service actually asks is one row:

```sql
SELECT level FROM user_access WHERE user_id = 'u1' AND doc_id = 'doc1';
```

This returns `edit`. Because the index covers `(user_id, doc_id)`, `EXPLAIN`
reports this as a fast-path `Index Lookup on ... user_access (using ...
user_access_by_user_doc)` with `Lookup values: ("u1", "doc1")`: it is answered
from the index arrangement rather than by rerunning the recursion, and the
arrangement is current with the inputs. Index the columns your checks filter
on; a filter on a column the index does not cover is a scan of the whole
expansion.

This binding converges exactly as the first one does; wrapping it in a view and
joining `memberships` in the body changes nothing about the fixpoint. Note that
`memberships` is joined in the body rather than carried through the loop, which
keeps the binding three columns wide
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

Standard SQL brings the same recursion, but the maintenance is yours: a
materialized view you `REFRESH` on a schedule, and a window during which the
answer is stale, or a permissions cache in the application that every grant
change, group move and membership edit has to invalidate correctly. Here the
recursion is the cache, and the update is incremental rather than a full
recompute
([semantics.md#update-locality](semantics.md#update-locality)).

## Denies

A deny is not a separate mechanism. Model it as an explicit row with
`level = 'none'`, and the override rule already does the hard part: the deny is
an explicit grant for its group, so the in-binding `NOT EXISTS` stops the
inherited row from reaching that group and everything under it. The body then
drops the `'none'` rows themselves. The data here is a three-group chain where
the middle group denies a document the root grants.

```sql
WITH MUTUALLY RECURSIVE
    tree(id text, parent_id text) AS (
        SELECT id, parent_id FROM (VALUES
            ('h1', NULL), ('h2', 'h1'), ('h3', 'h2')) AS v(id, parent_id)
    ),
    grants(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM (VALUES
            ('h1', 'docA', 'read'),
            ('h1', 'docB', 'read'),
            ('h2', 'docA', 'none')) AS v(group_id, doc_id, level)
    ),
    effective(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM grants
        UNION
        SELECT g.id, e.doc_id, e.level
        FROM tree g JOIN effective e ON e.group_id = g.parent_id
        WHERE NOT EXISTS (
            SELECT 1 FROM grants p
            WHERE p.group_id = g.id AND p.doc_id = e.doc_id
        )
    )
SELECT group_id, doc_id, level FROM effective
WHERE level <> 'none'
ORDER BY group_id, doc_id;
```

This returns h1 docA read; h1 docB read; h2 docB read; h3 docB read. docA
reaches h1 only: h2's `'none'` overrides what h1 grants, and h3 inherits that
`'none'` rather than the `read`, so neither survives the body's filter. docB,
which nobody denies, reaches all three groups.

Both halves are load-bearing. The in-binding `NOT EXISTS` is what stops
inheritance below h2; the body's `level <> 'none'` only removes the deny rows
from the answer. Convergence is unchanged, because the filter lives in the body
and the binding is the monotone one from the first section.

Standard SQL brings the same query, and in either dialect the modeling choice
is the part that matters. A deny kept in a separate table and applied as an
anti-join after the expansion removes rows for the denied group and nothing
else: h3 would keep the `read` it inherited from h1, because an anti-join on
`(group_id, doc_id)` has no way to know the path from h1 to h3 ran through h2.
Putting the deny in the same table as the grants is what makes it inherit.

## Relationship-based access (Zanzibar shape)

Zanzibar-style systems store relation tuples, `(object, relation, subject)`,
and derive access by walking them. That walk is reachability over a graph whose
nodes are objects and users ([reachability.md](reachability.md)), with one
branch per rewrite rule.

```sql
WITH MUTUALLY RECURSIVE
    tuples(object text, relation text, subject text) AS (
        SELECT object, relation, subject FROM (VALUES
            ('folder:f1', 'viewer', 'user:ann'),
            ('doc:d1', 'parent', 'folder:f1'),
            ('doc:d1', 'editor', 'user:bob')) AS v(object, relation, subject)
    ),
    holds(object text, relation text, user_id text) AS (
        SELECT object, relation, subject FROM tuples WHERE subject LIKE 'user:%'
        UNION
        SELECT object, 'viewer', user_id FROM holds WHERE relation = 'editor'
        UNION
        SELECT t.object, 'viewer', h.user_id
        FROM tuples t JOIN holds h ON h.object = t.subject AND h.relation = 'viewer'
        WHERE t.relation = 'parent'
    )
SELECT object, relation, user_id FROM holds ORDER BY object, relation, user_id;
```

This returns doc:d1 editor user:bob; doc:d1 viewer user:ann; doc:d1 viewer
user:bob; folder:f1 viewer user:ann. Bob is a viewer because he is an editor,
and Ann is a viewer of the document because she is a viewer of its parent
folder.

The three branches are Zanzibar's three userset kinds:

| Zanzibar rewrite | Branch here |
|---|---|
| `this` | the seed: tuples whose subject is a user |
| `computed_userset` | `relation = 'editor'` implies `viewer` on the same object |
| `tuple_to_userset` | follow `parent` tuples, take the folder's viewers |

Nested groups are one more branch of the same shape, following `member` tuples
from a group subject to its members. Intersection and exclusion rules are the
exception: `permission = editor AND NOT banned` is non-monotone and does not
belong in the binding. Put it in the body, or express it as a `NOT EXISTS` over
the base `tuples` relation, which is what the first section does with
`permissions`.

It converges because `holds` carries no counter and its three columns are drawn
from finite domains: objects and users come from `tuples`, and relations come
from `tuples` plus the literal `'viewer'`. Every branch only adds triples,
`UNION` folds re-derivations, so the fixpoint is reached in as many iterations
as the deepest chain of rewrites. A cycle in the folder graph costs nothing for
the same reason. `tuples` is a non-recursive leading binding and is evaluated
once.

A check against this is the same shape as `user_access`: make `holds` a view,
index it on `(object, relation, user_id)`, and `EXISTS` over that index answers
"may Ann view doc:d1" as a point lookup instead of an expansion.

Standard SQL cannot write this one. The recursive term references `holds`
three times across three branches, and standard `WITH RECURSIVE` allows exactly
one reference to the recursive relation
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)).
A Postgres user either chains several recursive CTEs, one per rewrite rule, and
accepts that a rule feeding back into an earlier one is not expressible, or
moves the whole walk into application code, which is what most Zanzibar
implementations do.

## Pitfalls

- Assuming the group graph is a tree. A group with two parent rows inherits
  from both, and when they disagree the expansion holds one row per distinct
  level. A point check written to expect a single row silently gets two.
  `UNION` deduplicates identical rows, not conflicting ones; pick a winner in
  the body.
- Not stating the override rule. "Nearest explicit ancestor wins", the rule in
  this file, and "most permissive grant wins" are both common and they give
  different answers for the same data. Neither is a default; write down which
  one the system implements before writing the query.
- `NOT EXISTS` over the binding instead of over the base table. Reading
  `permissions` keeps the recursive term monotone and the fixpoint guaranteed.
  Reading `effective` makes the recursion non-monotone, and WMR will run it
  without complaint until you notice it is not settling.
- Filtering denies only in the body. `WHERE level <> 'none'` removes the deny
  row from the answer; it does not stop inheritance. The deny stops inheritance
  because it is an explicit row and the in-binding `NOT EXISTS` treats it as an
  override. Drop either half and descendants of the denied group get access.
- No recursion limit on the maintained view. One group cycle plus any counter
  column and the view installs, never hydrates, and holds a dataflow until it
  is dropped.
- Confusing the point check with the expansion. "Can u1 read doc1" is one index
  lookup. "Everything u1 can read" is the full `(user, doc)` product in the
  worst case, and the index holds all of it whether or not anyone asks for it.
  Size the cluster for the expansion, not for the lookup.
- Filtering a one-shot version of the query in the body. A
  `WHERE user_id = 'u1'` there still expands every group's permissions first,
  because predicates are not pushed into a recursive binding
  ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
  Restrict inside the binding if you genuinely only ever ask about one user;
  otherwise maintain the whole thing and let the index do the filtering.
