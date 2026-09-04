# Eval harness for mz-graph-queries

The reproducible test environment and clean-room runner that the
mz-graph-queries skill was developed and evaluated against. The skill's
`DEVELOPMENT.md` describes the methodology. This directory holds the runnable
pieces.

One graded run is a single authoring round: the agent gets fourteen requests
phrased as they would arrive from a colleague, creates fourteen views in its
own schema, and writes a short report. `grade.py` then diffs every view against
an independent Python answer key, applies six mutations, and re-diffs.

## What the environment is

`build_fixture.py --eval` generates a seeded fourteen-table world in seven
groups, one group per graph shape the skill covers:

| group | tables | shape |
|---|---|---|
| org chart | `employees` | tree, with dirty edges |
| bill of materials | `parts`, `bom` | DAG with shared components |
| payments | `accounts`, `transfers` | cyclic digraph |
| authorization | `groups`, `memberships`, `permissions` | tree with inherited and overridden grants |
| identity resolution | `customers`, `customer_links` | undirected graph, edges stored once |
| road network | `cities`, `roads` | weighted undirected graph, edges stored once |
| pipeline lineage | `pipelines`, `depends_on` | DAG |

Six traps are planted in the data, one per way a naive recursive query goes
wrong:

| trap | where | what it breaks |
|---|---|---|
| a three-manager cycle plus a dangling reportee, detached from the tree | `employees` | a descendants query that assumes the hierarchy is a tree never terminates |
| a leaf component reachable under two distinct assemblies | `bom` | a query that deduplicates parts undercounts quantity and cost |
| a four-account transfer ring | `transfers` | reachability and closure queries that do not deduplicate never terminate |
| an explicit grant on a child group that replaces an inherited one | `permissions` | inheritance without override handling returns the wrong level |
| pair links stored in one direction only | `customer_links` | one-direction traversal splits clusters |
| roads stored in one direction only | `roads` | one-direction traversal reports the wrong shortest distance, or none |

Two more traps are in the prompts rather than the data: t06 asks for "all
paths" when the colleague needs a set of reachable accounts, and t14 hands over
a colleague's `UNION ALL` view that never returns and asks for a diagnosis.

Scale and seed are the two knobs. `--scale 100` is the graded size (504
employees, 200 parts and 298 bom edges, 1000 accounts and 3004 transfers, 30
groups, 300 customers and 300 links, 30 cities and 60 roads, 40 pipeline tasks
and 52 dependencies); `--scale 20` is a smoke size.
`--seed N` picks the graph; seed 1 is the default. Both the fixture and the
answer keys are derived from the same seed and scale, so a run is reproducible
and the keys are recomputed rather than recorded. `--no-traps` drops the
manager cycle for reference testing only; it is not usable for a graded run,
because the t01 prompt names the loop manager.

All vocabulary and data are invented, and nothing derives from any real
customer environment.

## Files

| File | Role |
|---|---|
| `fixture.py` | The fixture data model: table definitions, the small example world, the seeded eval world, SQL serialization, and mutations. |
| `build_fixture.py` | CLI over `fixture.py`. Emits SQL on stdout; `--small` is the skill's example world, `--eval --seed N --scale N` the eval world, `--manifest` prints the fixture parameters as JSON instead of SQL. |
| `reference.py` | Independent Python implementations of every answer, used as the answer key. Do not let evaluated agents read this file. |
| `tasks.py` | The task registry: one `Task` per prompt, with its answer key, its mutation, and its prompt file. Do not let evaluated agents read this file. |
| `tasks/tNN.md` | The fourteen colleague requests, as templates with fixture parameters substituted at run time. |
| `mzclient.py` | Talks to Materialize through the `psql` binary. Reads `EVAL_PSQL_ARGS`. |
| `grade.py` | Automatic grading. Diffs every view against the key, applies the mutations, re-diffs, reads the recursion guardrail out of each view definition, and writes `results.json` and `worksheet.md`. |
| `verify_skill_sql.py` | Runs every fenced `sql` block in the skill's reference files against the small fixture and compares with recorded output. `--record` re-records. |
| `expected/` | Recorded output for `verify_skill_sql.py`, one directory per skill reference file. |
| `tests/` | Unit tests for the fixture, the reference keys, the grader, and the SQL verifier. |
| `run_cleanroom.sh` | Builds a run's schema and cluster, generates the prompt and the wrapper, runs one graded agent round, and grades it. |
| `bench-psql.template` | The sandbox wrapper the runner and the preflight generate per run (the agent's only command). |
| `preflight.sh` | Permission preflight: exercises the generated wrapper directly, then runs one short agent session with the runner's isolation flags and compares each allowed and denied operation with the expected matrix. `--wrapper-only` skips the agent part. Run it before a batch and after any harness or CLI upgrade. |
| `prompt.txt.in` | The round prompt template. The runner substitutes the schema name and the fourteen rendered tasks. |
| `rubric.md` | Grading rubric: five axes with weights, and the re-check rule. |
| `GRADING-TEMPLATE.md` | Per-run grading worksheet. |

## Requirements

- A disposable Materialize instance reachable via `psql`. Never point this at a
  real environment.
- `python3` and `psql`, plus `uuidgen` for the preflight's agent part. GNU
  `timeout` is not required: the wrapper's 180 s statement cap and the runner's
  round budget are both enforced by a plain-bash watchdog, because macOS ships
  no GNU `timeout` and, more importantly, Materialize does not cancel a
  diverging recursive peek on `statement_timeout` alone.
- For graded agent runs: the Claude Code CLI (`claude`). Building the fixture,
  running the tests, and grading need no agent at all.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `EVAL_PSQL_ARGS` | `-h localhost -p 6877 -U materialize -d materialize` | Connection arguments for every psql invocation, the generated wrapper included. |
| `EVAL_BENCH_ROOT` | `$HOME/eval-bench` | Per-run working directories. Must be absolute. |
| `EVAL_CLUSTER_SIZE` | `25cc` | Replica size for the cluster the runner creates per run. |
| `EVAL_SCALE` | `100` | Fixture scale. 100 is the graded size. |
| `EVAL_TIMEOUT` | `7200` | Wall-clock budget for the round, in seconds. Enforced by a plain-bash watchdog in the runner, not by GNU `timeout`. |
| `SKILL_DIR` | `../../skills/mz-graph-queries` (relative to the runner) | The skill under test, mounted for `*s` conditions. |

## How to run

Start a disposable emulator on port 6877:

```bash
docker run -d --name mz-graph-queries -p 127.0.0.1:6877:6875 -p 127.0.0.1:6878:6876 \
  materialize/materialized:latest
```

Check the harness before a batch, and after any harness or CLI upgrade:

```bash
./preflight.sh --wrapper-only      # wrapper only, no agent; expect PASS lines and exit 0
./preflight.sh                     # adds the agent permission matrix
python3 -m unittest discover -s tests -t . -q   # fixture, keys, grader, SQL verifier
```

Smoke-test the runner end to end on the cheapest model:

```bash
./run_cleanroom.sh hs
```

Run the graded cells one at a time (`sb` bare, `ss` with the skill; `ob` and
`os` for Opus). The second argument is the seed:

```bash
./run_cleanroom.sh ss 1
./run_cleanroom.sh sb 1
```

Each run builds schema and cluster `gq_<cond>_s<seed>`, writes the agent's
working directory to `$EVAL_BENCH_ROOT/gq_<cond>_s<seed>/`, and leaves the
prompt, transcript, report, and grading output in
`$EVAL_BENCH_ROOT/gq_<cond>_s<seed>.private/`. Drop the run's schema and
cluster when you are done with it. The runner does not drop anything from a
previous run of the same cell except that cell's own schema and cluster, which
it recreates.

Grading is automatic at the end of a run. To re-grade a schema by hand, for
instance after fixing a harness bug:

```bash
python3 grade.py --schema gq_ss_s1 --seed 1 --scale 100 --out $EVAL_BENCH_ROOT/gq_ss_s1.private
```

## How grading works

`grade.py` writes `results.json` (a `summary` block plus a record per task) and
`worksheet.md` (one row per task) into the run's private directory. The five
axes of `rubric.md` weigh 2.0 (initial correctness), 1.0 (correctness after
mutation), 0.75 (convergence and guardrails), 0.75 (maintainability) and 0.5
(explanation), summing to 5.0. Axes 1 to 3 are computed from the summary keys `initial_ok`,
`post_mutation_ok`, `mutations`, `timed_out`, `guardrail`, and `exists`. Axes 4
(maintainability) and 5 (explanation) are manual and read the agent's
`report.md`, the transcript, and the view definitions in the run schema.

Two grader states need a human before they are scored. A task marked
`count-only` timed out on the full result and was compared by row count only,
so its pass is provisional. A mutation marked `skipped` was never applied
against a usable view. Both are described in `rubric.md`.

The re-check rule: before deducting for any automatic failure, re-run the
failing view by hand and compare it with `reference.py`. A fixture, reference,
or grader bug is possible; fix it in the harness, re-grade, and record the
correction. A run is never scored down for a harness bug.

## The isolation model

The graded conditions are meaningful only if the agent cannot see answers or
inherit context. The runner enforces, per run:

- **No user-level configuration**: `--setting-sources project` keeps the
  operator's own CLAUDE.md, settings, and skills out of the session, and
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` disables auto memory. The runner also
  refuses to start if any ancestor of the bench directory holds a `CLAUDE.md`,
  which would be loaded regardless of those flags.
- **One route to the database**: the generated `bench-psql` wrapper, pinned to
  the run's schema and cluster, flags and most meta-commands rejected,
  statements killed at 180 seconds by a watchdog the agent cannot raise
  (changing `statement_timeout` is refused, and the cap override exists for
  harness tests and clamps downward only). Around it the CLI's permission layer allows
  plain read-only shell commands inside the run directory, allows writes only
  inside the run's `scratch/` directory, and denies network access,
  interpreters, version control, and every file outside those directories. The
  prompt, transcript, report, and grading output live in the sibling
  `.private/` directory, outside the agent's reach. `preflight.sh` verifies
  this matrix.
- **Answer-key unreachability**: `reference.py`, `tasks.py`, and `grade.py`
  live in this directory, which is never mounted into a run. Under a skill
  condition the runner copies only `SKILL.md` and `references/` into the bench,
  never the skill's `DEVELOPMENT.md`, which describes this harness and its
  grading.
- **No retrieval**: `Skill`, `WebSearch`, and `WebFetch` are disallowed inside
  runs, so the only guidance the agent has is the mounted skill.

Porting note: those flags are Claude Code CLI specifics, and any other harness
needs equivalents for the same four guarantees.

## Safety notes

Everything here is for disposable local instances. The runner creates and drops
schemas and clusters, and the fixture plants cycles that make a careless
recursive query run until the wrapper kills it. Never run any of it against a
shared or production environment.

Two watchdog limits worth knowing. The round watchdog signals the agent process
itself; a process the agent had already spawned can outlive it, so check for
strays after a killed round. And a run whose round was killed is still graded,
on whatever views the agent had created by then; the runner says so on the line
above the grade.

## Recorded results

| run | condition | seed | initial_ok | post_mutation_ok | timed_out | guardrail | axis total (/5) |
|---|---|---|---|---|---|---|---|
| gq_sb_s1 | sonnet, bare | 1 | 14/14 | 6/6 | 0 | 0/14 | 4.292 |
| gq_ss_s1 | sonnet, skill | 1 | 14/14 | 6/6 | 0 | 7/14 | 4.825 |

**Both rows were produced by the skill as of commit `fefc26d`, before the
fold-back edits.** Commit `550a2df` (2026-09-03) changed `SKILL.md` Step 4 and
the reduce-topped guardrail passages in `references/shortest-paths.md` and
`references/rollups.md` in response to what these two cells showed. A later cell
is therefore not comparable to the `guardrail` column above on equal terms: a
higher number in a fresh `ss` run is the expected effect of that edit, not a
model or variance difference. Re-run `sb` alongside any fresh `ss` before
reading a delta.

Both cells: 2026-09-03, scale 100, Materialize v26.38.1, Claude Code 2.1.259,
model `claude-sonnet-5`. Neither was killed by the watchdog and neither produced
a `count-only` or `skipped` grade, so nothing above is provisional. The
per-cell grading sheets are `GRADE.md` in each run's private directory; they
record the hand re-checks behind the guardrail and index columns.

The Opus cells (`ob`, `os`) are pending; they are not part of the plan that
produced these two.

What the two Sonnet cells say, for anyone reading the table before running
more. The automatic correctness axes are at ceiling in both conditions: bare
Sonnet already takes every planted data trap on this fixture and diagnoses the
t14 `UNION ALL` correctly, so Axes 1 and 2 do not discriminate here and the
0.533 of separation is entirely on guardrails, indexes, aggregate placement and
whether the loose phrasings were interpreted out loud. A harder fixture, or a
scale where the closure shapes stop finishing inside the statement cap, is what
would move Axes 1 and 2.
