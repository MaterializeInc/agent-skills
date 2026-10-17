# Idiomatic Materialize SQL

Learn about idiomatic Materialize SQL. Materialize offers various idiomatic query patterns, such as for top-k query pattern, first value/last value query paterrns, etc.

Materialize follows the SQL standard (SQL-92) implementation and strives for
compatibility with the PostgreSQL dialect. However, for some use cases,
Materialize provides its own idiomatic query patterns that can provide better
performance.

## Window functions

| Window Function | Idiomatic Materialize |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/first-value/" >First value within groups</a> | <a href="/transform-data/idiomatic-materialize-sql/first-value/" >Use <code>MIN/MAX ... GROUP BY</code> subquery</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/lag/" >Lag over a regularly increasing field</a> | <a href="/transform-data/idiomatic-materialize-sql/lag/" >Use self join or a self <code>LEFT JOIN/LEFT OUTER JOIN</code> by an <strong>equality match</strong> on the regularly increasing field</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/last-value/" >Last value within groups</a> | <a href="/transform-data/idiomatic-materialize-sql/last-value/" >Use <code>MIN/MAX ... GROUP BY</code> subquery</a> |
| <a href="/transform-data/idiomatic-materialize-sql/lead/" >Lead over a regularly increasing field</a> | <a href="/transform-data/idiomatic-materialize-sql/lead/" >Use self join or a self <code>LEFT JOIN/LEFT OUTER JOIN</code> by an <strong>equality match</strong> on the regularly increasing field</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/top-k/" >Top-K</a> | <a href="/transform-data/idiomatic-materialize-sql/top-k/" >Use an <code>ORDER BY ... LIMIT</code> subquery with a <code>LATERAL JOIN</code> on a <code>DISTINCT</code> subquery (or, for K=1,  a <code>SELECT DISTINCT ON ... ORDER BY ... LIMIT</code> query)</a> |

## General query patterns

| Query Pattern | Idiomatic Materialize |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/any/" >ANY() Equi-join condition</a> | <a href="/transform-data/idiomatic-materialize-sql/any/" >Use <code>UNNEST()</code> or <code>DISTINCT UNNEST()</code> to expand the values and join</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/not-in/" ><code>NOT IN (&lt;subquery&gt;)</code> predicate</a> | <a href="/transform-data/idiomatic-materialize-sql/not-in/" >Rewrite to <code>NOT EXISTS</code>, or filter out <code>NULL</code>s on both sides of the <code>NOT IN</code></a>. |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#mz_now-expressions-to-calculate-past-or-future-timestamp" ><code>mz_now()</code> with date/time operators</a> | <a href="/transform-data/idiomatic-materialize-sql/mz_now/#mz_now-expressions-to-calculate-past-or-future-timestamp" >Move the operation to the other side of the comparison</a>: |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#disjunctions-or" ><code>mz_now()</code> with disjunctions (<code>OR</code>) in materialized/indexed view definitions and <code>SUBSCRIBE</code> statements</a>: | <a href="/transform-data/idiomatic-materialize-sql/mz_now/#disjunctions-or" >Rewrite using <code>UNION ALL</code> or <code>UNION</code> (deduplicating as necessary) expression</a> |

## Pages in this section

- [`ANY()` equi-join condition](/transform-data/idiomatic-materialize-sql/any/index.md): Use idiomatic Materialize SQL for equi-join whose `ON` expression includes the `ANY()` operator.
- [`NOT IN` subquery](/transform-data/idiomatic-materialize-sql/not-in/index.md): Use idiomatic Materialize SQL for `NOT IN (subquery)` predicates to avoid a cross join in the dataflow plan.
- [Appendix](/transform-data/idiomatic-materialize-sql/appendix/index.md): Idiomatic Materialize appendix, containing example data and cheatsheets
- [First value in group](/transform-data/idiomatic-materialize-sql/first-value/index.md): Use idiomatic Materialize SQL to find the first value in each group.
- [Lag over](/transform-data/idiomatic-materialize-sql/lag/index.md): Use idiomatic Materialize SQL to access the previous row's value (lag) when ordered by a field that advances in a regular pattern, such as in regular intervals.
- [Last value in group](/transform-data/idiomatic-materialize-sql/last-value/index.md): Use idiomatic Materialize SQL to find the last value in each group.
- [Lead over](/transform-data/idiomatic-materialize-sql/lead/index.md): Use idiomatic Materialize SQL to access the next row's value (lead) when ordered by a field that advances in a regular pattern, such as in regular intervals.
- [mz_now() expressions](/transform-data/idiomatic-materialize-sql/mz_now/index.md): `mz_now()` expressions can only take comparison operators. `mz_now()` expressions cannot be used with disjunctions `OR` in view definitions.
- [Top-K in group](/transform-data/idiomatic-materialize-sql/top-k/index.md): Use idiomatic Materialize SQL to find the top-k/top-n elements in each group.
