---
name: mz-demo-data
description: >
  Trigger: "demo data", "synthetic data", "live operational data", "generate
  fake data", "create a demo", "load generator alternative", or wants
  realistic continuously-updating data in Materialize for a demo. Also "I
  need streaming data to show off X" or "build a demo schema for <domain>".
  Use this to stand up auctions/bids, ecommerce, banking, IoT,
  clickstream, or zoo demos — or to design a new domain in the same style.
---

# Live operational demo data, generated entirely in SQL

This skill builds continuously-updating, realistic synthetic data inside a
running Materialize instance — no Kafka, no external load generator, no
seed scripts. Everything is plain views over `mz_now()`.

The technique comes from [this blog post][blog]. Use the catalog at the
bottom for an existing domain; use the rubric to design new ones.

[blog]: https://github.com/frankmcsherry/blog/blob/master/posts/2024-05-19.md

## Quickstart

```sh
psql -p 6875 -h localhost -U materialize -f assets/scaffold.sql
psql -p 6875 -h localhost -U materialize -f assets/common/people.sql
psql -p 6875 -h localhost -U materialize -f assets/domains/auctions.sql
```

Everything lands in its own `materialize_demo` schema, so nothing in the
user's existing schemas is touched. Every object is created `IF NOT EXISTS`,
so re-running any file is safe, but it also means re-running an *edited* file
keeps the old definitions. To rebuild, run `assets/teardown.sql` (it drops
the schema) and load again.

Then in a psql session:

```sql
SET search_path = materialize_demo;
COPY (SUBSCRIBE (SELECT COUNT(*) FROM auctions) WITH (progress = true)) TO STDOUT;
```

You should see a heartbeat tick once per second. The window is backfilled on
load, so the count starts at retention/tick (default 86,400) and stays there
as both ends of the window advance.

To change the window or tick rate, set them before `\i`. They only take
effect on a fresh load; if the scaffold is already there, run
`assets/teardown.sql` first.

```sql
\set retention '6 hours'
\set tick '1 second'
\i assets/scaffold.sql
```

To tear everything down: `psql -f assets/teardown.sql`.

## First contact: walking a fresh user from zero to demo

**Read this section first if you're an agent and a user shows up wanting a
demo.** The skill is meant to feel guided, not like a SQL reference. Drive
the user through these turns:

### Turn 1 — establish the connection

Ask once if it isn't already in context:

> What's the connection? A `psql` command, a `MATERIALIZE_URL`, or
> host/port/user/db?

Accept any of: a connection string, env var, or the four flags. Don't
proceed until you can run `psql -c 'SELECT mz_version();'` and get a row
back. If they say "localhost defaults", use
`psql -p 6875 -h localhost -U materialize -d materialize`.

### Turn 2 — pick a domain

If the user named one ("show me a banking demo"), check the catalog at the
bottom of this file. If it matches, jump to Turn 5 with that file.

If they have a domain in mind that isn't in the catalog ("I work in
logistics", "we do telecom billing", "give me healthcare"), continue to
Turn 3 — we'll build a new domain together. **Do not** force-fit their
domain onto one in the catalog; that's worse than a fresh one.

If they don't have a domain in mind, suggest 2–3 from the catalog with a
one-line hook each and let them pick. Banking is the strongest correctness
story; zoo is there to show that a domain can be anything, not just orders
and sensors.

### Turn 3 — propose the model in plain language

**Not SQL yet.** Show the user the entities and relationships in English,
plus the invariant you'd bake in. Format:

> Here's what I'd build:
> - **\<TopEntity\>** (one per moment) — fields: a, b, c
> - **\<ChildEntity\>** (3–5 per top-level) — fields: x, y
> - **\<Lookup\>** (static, N rows) — purpose
>
> **Invariant baked in:** \<one sentence — what must always hold\>
>
> **Joins to people?** \<yes/no, and why\>
>
> **Where the story beats show up:** freshness in \<the result to watch
> update\>, consistency in \<the invariant or check\>, responsiveness in
> \<the lookup to time, or the row the user can edit\>
>
> Sound right, or different entities?

Wait for their reaction. **Don't write SQL until they sign off.** They will
usually correct one of: an entity name, a missing field, the invariant, or
the cardinality. Cheap to iterate here, expensive later.

The story-beats line is a plan, not a script. See [Story
beats](#story-beats-freshness-consistency-responsiveness) for what each one
means and how to reveal it. If a beat has no natural home in the domain,
leave it out of the line rather than inventing an entity to carry it.

### Turn 4 — show the byte budget

Once entities are confirmed, show the byte allocation explicitly:

> Per top-level row, 16 random bytes:
> ```
> [0..2]  id              24-bit
> [3]     person_id       mod 256, FK to people
> [4]     kind            mod N
> [5]     n_children      1..K
> [6]     time offset     for due_at
> [7..]   free
> ```
> Children re-hash `(parent.random || child_index)` for their own bytes.

This is the last cheap-to-change step. If the user wants higher cardinality
in some field, swap bytes here, not later.

### Turn 5 — write and load

Copy `assets/domains/_template.sql` to `assets/domains/<their>.sql` and
fill it in following the byte budget. Then:

```sh
# Every file is IF NOT EXISTS — safe to re-run.
psql ... -f assets/scaffold.sql
psql ... -f assets/common/people.sql    # only if domain joins people
psql ... -f assets/domains/<their>.sql
```

If you are iterating on the domain file, re-running it will not replace
views that already exist. Drop the domain's objects first (`DROP VIEW
materialize_demo.<name>_core CASCADE` takes its whole chain), or run
`assets/teardown.sql` and load everything again.

### Turn 6 — prove it works, hand over the wheel

Show the user three queries, after `SET search_path = materialize_demo;`:

1. **Heartbeat** — confirms data is flowing:
   ```sql
   COPY (SUBSCRIBE (SELECT COUNT(*) FROM <top_table>) WITH (progress = true)) TO STDOUT;
   ```
2. **Invariant** — confirms correctness; should return the expected fixed
   value (usually 0).
3. **One "cool" query** — the demo payoff. For aggregations,
   `SELECT ... GROUP BY ...`; for cross-domain, a join through `people`.

These three are also where the story beats planned in Turn 3 usually land.
Subscribe to a *result* as well as the heartbeat, so the user watches an
aggregate move as its input changes (freshness). Run the invariant
while data is changing underneath it (consistency). Run the cool query with
`\timing` on, and if the domain has an editable table, change a row and read
the result again (responsiveness). When a beat shows up, name it in one
plain sentence, with the number you just saw.

Then offer: "Want to layer another domain on top? You'll see joins through
the shared `people` table stay live too."

If you can publish a page the user can share, also offer one that records
what they built and what they saw. See [A shareable
record](#a-shareable-record).

### Things to *not* do during first contact

- Don't dump the catalog up front. The user came with a domain or wants
  guidance — give them one path, not a menu.
- Don't ship SQL without the plain-language proposal first.
- Don't skip the byte budget. It's where misalignments hide (e.g., two
  fields sharing byte 5 by accident).
- Don't claim "it's done" until the heartbeat ticks and the invariant
  query returns its expected value against THEIR Materialize instance.
- Don't add columns the user didn't ask for. The template's free bytes
  exist; leave them free unless the user names a use.
- Don't open with a speech about freshness, consistency and
  responsiveness. Show the beat first, then name it.

## Story beats: freshness, consistency, responsiveness

These are the three properties people usually come to Materialize for. A
demo is most convincing when the user watches each one happen on their own
domain, rather than reading a claim about it. Don't force them into the
demo. Plan in Turn 3 where each one will show up, build the domain so that
moment exists, and point it out when it happens.

**Freshness** is often the headline: how soon a result reflects its
inputs, through joins, aggregates, and late or corrected data. Report the
lag you measure, not the lag you expect.
- Show it with a `SUBSCRIBE ... WITH (progress = true)` on a *derived*
  result, not only on the raw input. Each update carries an `mz_timestamp`
  that tracks the wall clock.
- Measure it. Generated rows become visible at their moment, so the gap
  between an update's `mz_timestamp` and the wall-clock time the client
  receives it is the time from "event arrived" to "result in hand". Measure
  the input view too. The difference is what the domain's logic costs.
- Materialize keeps its own record, at one-second granularity:
  ```sql
  SELECT o.name, l.lag
  FROM mz_internal.mz_wallclock_global_lag l
  JOIN mz_objects o ON o.id = l.object_id
  JOIN mz_schemas s ON s.id = o.schema_id
  WHERE s.name = 'materialize_demo';
  -- Distribution over recent history:
  -- mz_internal.mz_wallclock_global_lag_histogram (lag_seconds, count)
  ```
- If lag is seconds or more and growing, that is a finding, not a detail
  to skip. The `mz-debug-freshness` skill finds the cause.

**Consistency** means every result is correct as of a single timestamp, and
all views read at that timestamp agree with each other.
- The domain's invariant is the natural place. Subscribe to it, or re-run
  it while data changes, and it never shows a wrong value.
- A second, independent computation of the same answer makes a strong
  check: a view that compares the two with `EXCEPT ALL` in both directions
  stays empty.

**Responsiveness** is how quickly a read against an indexed view comes
back, and how soon a write shows up in the results that depend on it.
Report the times you measure.
- Time a lookup with `\timing`.
- Generated data runs on its own, so it gives the user nothing to change.
  If the domain has a natural setting (a threshold, a price, a plan, a
  lookup row), make it a regular table. An `UPDATE` followed by a read of
  the result it changes shows responsiveness and consistency together.

Report every number with the scale it was measured at (rows, events per
second, where it ran). A sub-second number from a laptop is still worth
showing, as long as it is labelled as a laptop number.

### A shareable record

Some agents can publish a page the user can keep and pass around (Claude's
artifacts, for example). If you can, offer one once the beats have shown
up. Offer it, don't build it unasked. It gives the user something to show
a colleague, and it is the natural place to set each beat against the
volume of data behind it. A sentence of the form "results within
\<measured lag\> of their inputs, while maintaining \<measured row count\>
\<entities\> arriving at \<measured rate\> per second" says more than either
half. Fill every placeholder from a measurement in this session, or drop
the clause.

Put in it:
- The domain in two sentences, with the entities and their rates as agreed
  in Turn 3.
- The scale: rows maintained, events per second, the window, how many views
  deep the cool query sits, and where it ran (laptop emulator, cloud
  cluster size).
- Each beat that showed up, with the number you measured. Freshness as
  arrival-to-result time, and the lag histogram if you read it.
  Consistency as the invariant and how many changes it held through.
  Responsiveness as lookup latency and the time from `UPDATE` to changed
  result.
- The invariant and the cool query as SQL, so a reader can rerun them.

Keep it honest:
- Only numbers measured in this session, each labelled with its scale. No
  extrapolating from a laptop to production.
- The page is a snapshot, so say when it was measured. If it can't be
  live, a captured `SUBSCRIBE` trace drawn as values against wall-clock
  time stands in for the moving result.
- A beat that didn't show up is left out, not claimed. A finding, such as
  lag that grew, goes in plainly.
- Leave out hostnames, connection strings, credentials, and the user's
  organization and cluster names unless they ask for them. The data is
  synthetic, so the rows themselves are safe to show.

## The two-layer model

Every demo built with this skill has exactly two layers:

1. **Scaffold** (stable). The `moments` view — a sliding window of timestamps
   — and the `random` view — MD5(moment) producing 16 deterministic bytes per
   moment. **Do not edit per-domain.** Always loaded first; the same scaffold
   serves every domain. Lives in `assets/scaffold.sql`.

2. **Domain** (creative). Views that turn `random` bytes into entities,
   relationships, and aggregates. One file per domain in `assets/domains/`.
   Domains can compose: load multiple and they cross-join naturally via the
   shared `people` table.

Knowing where the line is matters. If you find yourself wanting to edit the
scaffold from a domain file, you almost certainly want to add another view
on top instead.

## The four design rules for a domain

Every domain in the catalog follows these four rules. Apply them when
designing a new one.

### 1. PKs are derived deterministically from `moment`

A row's primary key is a function of its moment's random bytes:

```sql
get_byte(random, 0) + get_byte(random, 1) * 256 + get_byte(random, 2) * 65536  AS id
```

**Why:** the same moment always yields the same id, so re-derivation is stable
even though the underlying view is a sliding window. PKs naturally vanish from
the system when their moment falls out of retention.

### 2. FKs come from re-derivation, not declared constraints

A child row is generated by re-hashing the parent's random bytes:

```sql
WITH expanded AS (
    SELECT id AS parent_id, ...
           digest(random::text || generate_series(1, n_children)::text, 'md5') AS random
    FROM parent_core
)
SELECT ... FROM expanded;
```

**Why:** when the parent's moment falls out of retention, every child derived
from it vanishes simultaneously. Referential integrity for free, no
`FOREIGN KEY` declarations needed. This is the key insight that makes the
whole approach work.

### 3. Distributions are byte-mask choices

Cardinality is controlled by which bytes you read:

| Pattern                                | Cardinality      |
|----------------------------------------|------------------|
| `get_byte(random, 0)`                  | 256              |
| `get_byte(random, 0) + get_byte(random, 1) * 256` | 65,536 |
| `mod(get_byte(random, 0), 5)`          | 5                |
| `get_byte(random, 0) < 80`             | ~31% boolean     |

**Why:** explicit and predictable. A 256-account banking demo uses one byte
mod 64 for from-account; a 16M-id auction marketplace uses three bytes. Pick
the cardinality you need.

### 4. Evolution is `moment + interval`

Time-relative fields are derived from the moment plus a random offset:

```sql
moment + (get_byte(random, 6)::text || ' minutes')::interval AS end_time
```

**Why:** the field is monotone in the moment, so downstream views can filter
on it sensibly. Combined with rule #1, this gives you a temporal lifecycle
(start, end, expiry) tied to the entity's identity.

## Invariant-by-construction patterns

The strongest demos rely on invariants that **cannot be violated** because of
how the data is constructed. Two patterns:

**Sum-to-zero (double entry).** Each event emits two child rows with opposite
signs (`banking.sql`). `SUM(ledger_entries.amount) = 0` holds at every
consistent timestamp, regardless of concurrent transaction volume. This is
the headline Materialize correctness demo and it's almost impossible to fake
with off-the-shelf data.

**Count matches declared fanout.** A parent row declares `n_items`, and uses
`generate_series(1, n_items)` to emit children. `COUNT(children) =
SUM(parent.n_items)` is invariant (`ecommerce.sql`). State it in aggregate;
the per-parent form breaks on id collisions (next section).

When designing a new domain, look for an invariant of this form. A demo
without one is weaker — it shows speed but not correctness.

## Invariants vs. id collisions

The blog's construction derives primary keys from 24 bits of MD5 entropy
(`get_byte(random, 0..2)` packed into an int). At default settings — 86,400
moments in retention — the birthday paradox guarantees roughly 230–500
id collisions in steady state. **This is intentional and expected.** The
blog accepts it; this skill keeps it for fidelity to the blog and to keep
parent ids in a tractable range.

Collisions affect which invariant shapes you can honestly claim:

**Survives collisions (claim freely):**
- Aggregate equalities. `COUNT(children) = SUM(n_children over all parents)`.
- Sum-to-zero. `SUM(ledger_entries.amount) = 0`.
- Subset / FK by re-derivation. `every child.parent_id has matching parent` —
  re-derivation guarantees this even when multiple parents share an id (the
  child joins to *some* row with that id).
- Distribution-shape claims. `~10% of page_views are /checkout`.

**Does NOT survive collisions (don't claim, or restate as aggregate):**
- Per-parent fanout equality. `for every parent, COUNT(children with this id) = parent.n_children`.
  Two parents sharing an id will sum their children, breaking the equality.
- Per-id uniqueness. `every id appears exactly once`.
- Per-row temporal monotonicity that depends on id grouping.

When the user asks "what's the invariant," default to the aggregate form
unless the construction makes per-id claims structurally true (e.g.
double-entry, where each transaction emits exactly two entries no matter
what id arithmetic does).

If a demo *requires* unique ids (e.g. a customer-facing dashboard that
treats id as a key), the fix is to either widen the id space (use 4+
bytes), use `EXTRACT(EPOCH FROM moment)::bigint` as the id (collision-free
by construction), or accept ~0.5% noise as a feature ("real data is
messy"). All three are reasonable; the catalog uses the blog's 24-bit
form for fidelity.

## Adapting to a new domain

When walking a user through this, follow the **First contact** protocol
above — propose-then-confirm, don't write SQL upfront. The mechanical
checklist is below.

To add `assets/domains/<yours>.sql`, work through these steps in order:

1. **List the entities.** Top-level (one per moment), child rows (per parent
   via fanout), shared lookups (static).
2. **Pick the byte budget for each top-level entity.** Random gives you 16
   bytes per moment. Allocate bytes to fields by cardinality:
   id (3 bytes), FK to people (1 byte mod 256), category (1 byte mod N),
   timing offsets (1 byte), free for amount/value (2–3 bytes).
3. **Decide which existing shared tables you reference.** Today: `people`. If
   you reference people, your domain joins the cross-domain "same person
   appears in multiple data products" story automatically.
4. **Identify the invariant.** What sum, count, or equality must hold by
   construction? Bake it in via fanout or two-legged emission, not as a
   `CHECK` constraint.
5. **Copy the template.** `cp assets/domains/_template.sql assets/domains/<yours>.sql`
   and fill in the TODOs. The template already encodes the standard
   `_core` view → public MV → child MV → aggregate VIEW pattern, with every
   object in `materialize_demo` and created `IF NOT EXISTS`. Keep that
   structure.
6. **Add two validation queries** at the bottom: a `SUBSCRIBE` heartbeat
   and an invariant query that should always return 0 (or a fixed value).

## Validation

For every domain, two queries:

```sql
-- Heartbeat: confirms the domain is live and producing rows.
COPY (SUBSCRIBE (SELECT COUNT(*) FROM <table>) WITH (progress = true)) TO STDOUT;

-- Invariant: should return a fixed value (usually 0).
SELECT ... ;
```

If the heartbeat ticks but the invariant drifts, the byte budget is
misaligned — likely two entities sharing the same byte for different
purposes. Re-allocate.

## The catalog

| File | Domain | Highlights | Joins `people`? |
|---|---|---|---|
| `domains/auctions.sql`   | Auctions & bids                | Marketplace; lifecycle (end_time); winning-bid demo            | No |
| `domains/ecommerce.sql`  | Orders, line items, totals     | Multi-row child fanout; `order_totals` aggregate-as-view       | Yes |
| `domains/banking.sql`    | Accounts, double-entry txns    | **`SUM(balances) = 0`** invariant. Strongest correctness demo. | Yes |
| `domains/iot.sql`        | Devices, readings, alerts      | High cardinality; threshold alerts; per-site rollup            | No |
| `domains/clickstream.sql`| Sessions, page views, funnel   | Funnel analytics; conversion rate by channel                   | Yes |
| `domains/zoo.sql`        | Zoo visits, ratings, shipments | Three invariants at once, richest domain. Proof that a domain needn't be boring: front-of-house ratings correlate with back-of-house consultations by construction. | Yes |

Loading more than one ecommerce/banking/clickstream domain at once gives you
the cross-product demo: "show me Person 042's orders, their transactions, and
their browsing session — all live, all consistent."

## File map

```
skills/mz-demo-data/
├── SKILL.md                  ← you are here
├── README.md                 short human intro
└── assets/
    ├── scaffold.sql          moments + random; do not edit per-domain
    ├── teardown.sql          drops the materialize_demo schema
    ├── common/
    │   └── people.sql        256-identity pool, shared across domains
    └── domains/
        ├── _template.sql         ← copy this to start a new domain
        ├── auctions.sql
        ├── ecommerce.sql
        ├── banking.sql
        ├── iot.sql
        ├── clickstream.sql
        └── zoo.sql
```
