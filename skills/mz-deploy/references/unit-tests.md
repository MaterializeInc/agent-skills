# EXECUTE UNIT TEST

`mz-deploy test` runs SQL unit tests against a local Materialize container. No
remote database is touched. Tests live inline in the same `.sql` file as the
view they cover, so a definition and its tests are reviewed and versioned
together.

Requires Docker.

## Grammar

```sql
EXECUTE UNIT TEST <test_name>
FOR <database>.<schema>.<view>
[AT TIME '<timestamp>']
MOCK <dependency>(<col> <type>, ...) AS (<query>)
[, MOCK <dependency>(<col> <type>, ...) AS (<query>)]
EXPECTED(<col> <type>, ...) AS (<query>);
```

| Clause | Required | Description |
|--------|----------|-------------|
| `EXECUTE UNIT TEST name` | Yes | Test name, shown in output and usable as a filter |
| `FOR database.schema.view` | Yes | The target view or materialized view, fully qualified |
| `AT TIME 'expr'` | No | Value `mz_now()` returns during the test |
| `MOCK fqn(cols) AS (query)` | Yes | One per dependency of the target — see below |
| `EXPECTED(cols) AS (query)` | Yes | The rows and column types the target should produce |

A single file may contain the `CREATE VIEW` (or `CREATE MATERIALIZED VIEW`)
followed by any number of `EXECUTE UNIT TEST` statements. Separate consecutive
`MOCK` clauses with commas; there is no comma before `EXPECTED`.

**Every dependency of the target must be mocked.** An unmocked dependency is a
validation error, not a silent pass-through — the target view is rewritten to
read from the mocks rather than from real objects, so there is nothing for an
unmocked reference to resolve to.

## Worked Example

Given `models/materialize/public/user_order_summary.sql`:

```sql
CREATE VIEW user_order_summary AS
SELECT u.id AS user_id, u.name, count(*) AS total_orders
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;

EXECUTE UNIT TEST test_single_user_single_order
FOR materialize.public.user_order_summary
MOCK materialize.public.users(id bigint, name text) AS (
  SELECT * FROM VALUES (1, 'alice')
),
MOCK materialize.public.orders(id bigint, user_id bigint) AS (
  SELECT * FROM VALUES (10, 1)
)
EXPECTED(user_id bigint, name text, total_orders bigint) AS (
  SELECT * FROM VALUES (1, 'alice', 1)
);
```

Mock and expected bodies are ordinary queries. `SELECT * FROM VALUES (...), (...)`
is the usual way to supply literal rows, but any query works.

## Mock Name Resolution

Mock names may be unqualified, schema-qualified, or fully qualified. Partial
names resolve relative to the target view:

```sql
MOCK users(...)                        -- resolves in the target's schema
MOCK public.users(...)                 -- resolves in the target's database
MOCK materialize.public.users(...)     -- fully qualified
```

Prefer fully qualified names in tests that mock across schemas, where the
relative form is ambiguous to a reader.

## Temporal Views

A view filtering on `mz_now()` is untestable without a fixed clock. `AT TIME`
pins one:

```sql
EXECUTE UNIT TEST test_recent_events
FOR materialize.public.recent_events
AT TIME '2024-01-15T12:00:00Z'
MOCK materialize.public.events(id bigint, occurred_at timestamptz) AS (
  SELECT * FROM VALUES
    (1, '2024-01-15T11:59:00Z'::timestamptz),
    (2, '2024-01-01T00:00:00Z'::timestamptz)
)
EXPECTED(id bigint, occurred_at timestamptz) AS (
  SELECT * FROM VALUES (1, '2024-01-15T11:59:00Z'::timestamptz)
);
```

## How a Test Is Evaluated

For each test, `mz-deploy test`:

1. **Validates schemas.** Mock columns must match the real object's schema —
   no missing columns, no extra columns, compatible types. `EXPECTED` columns
   must match the target's output schema. Validation happens before execution,
   using `types.lock` for external dependencies and the compiler database for
   in-project types.
2. **Creates temporary views** for each mock, for the expected result, and for
   the target rewritten to read from the mocks.
3. **Runs a symmetric difference** between actual and expected rows. Rows in
   expected but not actual are reported `MISSING`; rows in actual but not
   expected are reported `UNEXPECTED`.
4. **Passes** if that query returns zero rows.
5. **Cleans up** with `DISCARD ALL` before the next test.

Comparison is set-based: row order never matters, and duplicate rows do matter.

### Type Normalization

Types in `MOCK` and `EXPECTED` are normalized before comparison, so common
aliases are interchangeable:

| Canonical | Accepted aliases |
|-----------|------------------|
| `int4` | `int`, `integer` |
| `int8` | `bigint` |
| `text` | `varchar`, `string` |
| `float8` | `float`, `double precision` |
| `numeric` | `decimal` |
| `jsonb` | `json` |

## Running and Filtering

```bash
mz-deploy test                                     # all tests
mz-deploy test 'materialize.*'                     # all tests in a database
mz-deploy test 'materialize.public.*'              # all tests in a schema
mz-deploy test 'materialize.public.my_view'        # all tests for one view
mz-deploy test 'materialize.public.my_view#test1'  # one named test
```

The filter matches the target's fully qualified name, optionally followed by
`#<test_name>`. A trailing `*` matches all values for that position and every
position after it.

A filter that matches nothing prints `No tests found` and **exits 0**, verified
against v0.3.1. (`mz-deploy help test` claims exit 1 for this case in its Exit
Codes section, contradicting its own prose one paragraph earlier; the observed
behavior is 0.) A typo'd filter in CI therefore passes vacuously — assert on
the test count, or run the unfiltered suite, if that matters to you.

## CI

```bash
mz-deploy test --junit-xml results.xml
```

JUnit XML is consumed directly by GitHub Actions, Jenkins, and GitLab CI for
test annotations and trend tracking.

`test` shares a single Docker container named `mz-deploy-sandbox` with
`explain`, reused across invocations on the host. **Reuse is by name, not by
image** — `--docker-image` only takes effect when the container is created, so
switching images requires `docker rm -f mz-deploy-sandbox` first.

## Failure Modes

| Symptom | Cause and fix |
|---------|---------------|
| `Docker unavailable` | Install Docker and start the daemon. |
| Unmocked dependency | Add a `MOCK` for every object the target reads. |
| Mock schema mismatch | Mock columns must match the real object exactly. If an external dependency changed, run `mz-deploy lock`. |
| Expected schema mismatch | `EXPECTED` columns must match the target's output columns and types. |
| `MISSING` rows | The view did not produce a row you expected. Check the mock data, then the view logic. |
| `UNEXPECTED` rows | The view produced a row you did not expect. Either the expectation is incomplete or the logic is wrong. |
| Stale types cache | `mz-deploy clean`, or `mz-deploy lock` to refresh `types.lock`. |

Exit code is 0 when all tests pass, when no tests exist, or when a filter
matches nothing; 1 on any test failure or validation error.
