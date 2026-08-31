# Eval harness for mz-optimize-memory

The reproducible test environment and clean-room runner that the
mz-optimize-memory skill was developed and evaluated against.
The skill's `DEVELOPMENT.md` describes the methodology. This directory
holds the runnable pieces. "v6" in the file names is the sixth
generation of the eval environment. Each generation is a superset of the
one before it: v4's ten constructions, v5's thirteen more, and v6's eight
more, chosen so that the levers, signatures, and reference files the skill
carries are exercised somewhere. `build_v6.py --v4` re-emits the v4 subset
byte-identically (which is what the calibration matrix at the bottom of
this file was measured on) and `--v5` re-emits the v5 environment.

Four constructions are built but OUT OF GRADING SCOPE in v6: C7 and C8
(per-event pre-aggregation) and C23 (distributive pre-aggregation), because
the skill's first version drops pre-aggregation entirely, and C22
(dictionary compression), because the feature is experimental. Their
objects stay in the environment as haystack. `v6-rubric.md` and section 3f
of the answer key say what that means for grading.

## What the environment is

`build_v6.py` generates a synthetic delivery-dispatch analytics
environment: 60 tables, 76 views, 14 materialized views, roughly 9,200
lines of SQL, about 2.4 GB of arrangement memory at full scale. Planted
in it are thirty-one optimization constructions (dead indexes, a
width-trap index proposal, over- and under-sized GROUP SIZE hints,
payload-heavy arrangements, boundary-reorganization opportunities, a
nullable-key landmine that punishes a careless index, a provable
LEFT-to-INNER conversion, four subquery-decorrelation shapes, two window
gadgets, a general outer-join lowering, a redundant DISTINCT, a
null-safe join that cross-joins, a basic aggregate that retains its whole
input, an argmax redundancy, a distributive pre-aggregation site, a
cluster-wide dictionary-compression candidate, two ways of breaking the
variadic-outer-join lowering, a window pair that is really a group
aggregate, both outer-join pushdown gaps, seven more subquery-rewrite
sites, a differential join waiting for a delta-enabling index package, and
a late-materialization site) plus red herrings that are already optimal and
must be left alone. Every construction's memory
signature was validated by measurement, and `v6-ANSWER-KEY.md` records
the measured ground truth, including two reference solutions and
per-construction savings. All vocabulary and data are invented, and nothing
derives from any real customer environment.

## Files

| File | Role |
|---|---|
| `build_v6.py` | Environment generator. Emits SQL on stdout. `--manifest` prints the construction manifest, `--scale` builds a smaller variant for syntax checks, `--reference` / `--reference-conservative` emit the fixed reference environments, `--build-ts` pins the data anchor for reproducible A/B pairs, `--v4` emits the v4 subset and `--v5` the v5 environment. |
| `v6_checks.sh` | Signature validation: confirms each planted construction measures as designed. Sections selectable by argument. |
| `v6_c9_arm.sh` | Arms / restores the nullable-key landmine (deliberately causes a multi-minute one-worker grind when armed, see safety notes). |
| `run_cleanroom_v6.sh` | Builds the environment and runs one graded four-round agent session against it, snapshotting the schema after the build and after every round. |
| `bench-psql.template` | The sandbox wrapper the runner and the preflight generate per run (the agent's only command). |
| `v6_preflight.sh` | Permission preflight: exercises the generated wrapper directly, then runs one short agent session with the runner's isolation flags and compares each allowed and denied operation with the expected matrix. `--wrapper-only` skips the agent part. Run it before a batch and after any harness or CLI upgrade. |
| `v6-prompt-1/2/3/4.txt.in` | The four round prompts (templates, the runner substitutes schema, gate, and source-tree path). |
| `v6-colleague-proposal.sql` | A 25-item colleague proposal for a separate adjudication experiment (not part of the v6.1 protocol). |
| `v6-rubric.md` | Grading rubric: five axes with weights. |
| `v6-ANSWER-KEY.md` | Measured ground truth and grading aids. Do not let evaluated agents read this file (see isolation). |
| `GRADING-TEMPLATE.md` | Per-run grading worksheet. |

## Requirements

- A disposable Materialize instance reachable via psql. A local
  emulator (`docker run -p 6875:6875 materialize/materialized`) or a
  source build both work. The full-scale environment needs roughly
  3.5 GB of memory headroom on the instance. Never point this at a real
  environment.
- `python3`, `psql`, `uuidgen`.
- Table headroom on the instance. One v6 environment is 60 tables and the
  emulator's `max_tables` default is 200, so a baseline plus a reference
  plus one graded run's schema (180) fits and a fourth environment does
  not. The failure is a clean error at the first table over the line
  (`creating table would violate max_tables limit`), which aborts the load
  partway. Drop schemas you are done with before starting another build,
  or raise the limit first for a multi-cell campaign (`ALTER SYSTEM SET
  max_tables = 400` as `mz_system` on the emulator's port 6877).
- For graded agent runs: the Claude Code CLI (`claude`). The
  environment build and signature checks need no agent at all.
- A plain checkout of MaterializeInc/materialize for the agent to read
  source and docs from (`MZ_SRC`).

## Configuration

The scripts read these environment variables, with defaults (the
Meaning column says where a variable applies when it is not global):

| Variable | Default | Meaning |
|---|---|---|
| `EVAL_PSQL_ARGS` | `-h localhost -p 6875 -U materialize -d materialize` | Connection arguments for every psql invocation. |
| `EVAL_BENCH_ROOT` | `$HOME/eval-bench` | Per-run working directories (wrapper, prompts, transcripts). |
| `MZ_SRC` | `$EVAL_BENCH_ROOT/mz-src` | Materialize checkout the agent may read. |
| `SKILL_DIR` | `../../skills/mz-optimize-memory` (relative to the runner) | The skill under test, mounted for `*s` conditions. |
| `EVAL_SCALE` | unset | When set (for example `100`), passed to the generator as `--scale`: a small environment for smoke-testing the runner, never for graded cells. |
| `EVAL_CLUSTER_SIZE` | `100cc` | Replica size for the cluster `build_v6.py` creates. The default is what the Docker emulator ships (1 process, 2 workers). A source build also accepts the dev size map's `scale=1,workers=2`. |

## Quickstart

Build and validate the environment without any agent:

```bash
python3 build_v6.py v6dev | PGOPTIONS="-c statement_timeout=1h" psql -h localhost -p 6875 -U materialize -d materialize -v ON_ERROR_STOP=1 -f -
./v6_checks.sh v6dev            # all sections, or: ./v6_checks.sh v6dev mem
```

Build a reference pair for an A/B, both from one data anchor:

```bash
TS=$(date -u -d '5 minutes ago' '+%Y-%m-%d %H:%M:%S')
python3 build_v6.py v6dev --build-ts "$TS" | psql ... -f -
python3 build_v6.py v6fix --reference --build-ts "$TS" | psql ... -f -
```

The fact table is loaded by one million-row `INSERT`, which can outrun the
server's default `statement_timeout` of one minute on a slow host; the
`PGOPTIONS` prefix raises it for the build session only (the runner does
the same).

`--build-ts` must be at or before wall-clock now. The temporal spine
keeps rows whose `created_at` is within the last 24 hours of
`mz_now()`, so a future anchor puts most of the anchor window ahead of
the clock, the spine comes out a fraction of its designed size, and
every per-anchor construction silently shrinks with it.

Run one graded cell (condition codes: `sb`/`ss` Sonnet bare/skill,
`ob`/`os` Opus bare/skill, `o8b`/`o8s` Opus 4.8 bare/skill; `hb`/`hs` Haiku
4.5 exist only for smoke-testing the runner with `EVAL_SCALE` set):

```bash
./run_cleanroom_v6.sh ss
```

The runner builds a fresh schema named after the run, waits for
hydration, generates the sandbox wrapper, and drives four rounds in one
resumed agent session: 1 (read-only first package), 2 (validate and implement under a 15 MB estimate
gate), 3 (look for further optimizations and validate them on the bench),
4 (pressure, method-upgrade probes and per-change attribution). After the
build and after every round it snapshots the schema (objects, indexes,
hydration, dataflow and operator census) into `snapshot-r0.txt` ..
`snapshot-r4.txt`, so the rubric's checkpoint grades can quantify what
each round added. Transcripts (`transcript-rN.txt`, the last message of
each round; the full session is in the CLI's project log), the round
prompts and the snapshots land in `$EVAL_BENCH_ROOT/<run>.private/`,
outside the agent's working directory `$EVAL_BENCH_ROOT/<run>/`. Grade with `v6-rubric.md` +
`v6-ANSWER-KEY.md` + `GRADING-TEMPLATE.md`, auditing the database
state as well as the transcript. Drop the run's schema and cluster
afterwards.

## The isolation model

The graded conditions are meaningful only if the agent cannot see
answers or inherit context. The runner enforces, per run:

- **No user-level configuration**: `--setting-sources project` keeps
  the operator's own CLAUDE.md, settings, and skills out of the
  session, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` disables auto
  memory. Both leaks were observed in probes before these flags were
  added, so re-probe after harness upgrades: `./v6_preflight.sh` runs
  the probe and prints PASS or FAIL per operation.
- **One route to the database**: the generated `bench-psql` wrapper
  (mode-switched read-only vs read-write between rounds, flags and most
  meta-commands rejected). Around it the CLI's permission layer allows
  plain read-only shell commands inside the run directory and `MZ_SRC`,
  allows writes only inside the run's `scratch/` directory, and denies
  network access, interpreters, version control, and every file
  outside those directories; round prompts and transcripts are kept
  outside the run directory so a round cannot read a later round's
  prompt. `v6_preflight.sh` verifies this matrix.
- **Answer-key unreachability**: the key lives in this directory,
  which is never mounted into a run. `MZ_SRC` must be a plain
  Materialize checkout. Do not point it at a tree containing this
  repository, and do not run evaluated agents with this repository's
  skills installed user-globally (that is what `--setting-sources
  project` guards against).
- **No retrieval**: `Skill`, `WebSearch`, and `WebFetch` tools are
  disallowed inside runs.

Porting note: those flags are Claude Code CLI specifics, and any other
harness needs equivalents for the same four guarantees.

Design note: the original v4 campaign appended a single-file precursor
of the skill to the round-1 prompt. This runner instead mounts the
published skill directory (`SKILL.md` + `references/`) read-only and
tells the agent where it is, preserving the skill's
progressive-disclosure structure. Results are therefore comparable in
design, not byte-for-byte, with the campaign numbers below.

## Recorded campaign results (for calibration)

These six cells ran against the v4 subset of this environment, which
`build_v6.py --v4` still emits byte-identically, so they remain valid
calibration for the harness and the protocol. They do not calibrate the
twenty-one constructions v5 and v6 add; for those, see the v6 cells below.

Grades are 0-5 against the rubric. The percentage is the measured
memory reduction the run achieved on the v4 subset, whose baseline was
about 1.5 GB, whose measured reference solution was -16.2%, and whose
best known result was -26.3%, found by an agent, beyond the reference.

| condition | bare | with skill (precursor) |
|---|---|---|
| Sonnet | 2 (-6.1%) | 4 (-11.7%) |
| Opus | 4 (-10.6%) | 5 (-26.3%) |
| Opus 4.8 | 3 (-0.1%) | 3.5 (-7.5%) |

Those six v4 cells ran a three-round protocol with a 15-item proposal and
1800/3600/1800 s budgets on the v4 subset, so they calibrate the
constructions, not the four-round scores.

Four cells ran on the full v6 environment on 2026-08-27 under the
earlier three-round protocol (first package, change window, pressure and
attribution; budgets 5400/9000/5400 s; one cell at a time on a thermally
throttled laptop; key reference -37.1%). They calibrate the v6
constructions and are comparable to each other, not to four-round cells
(their round-1 prompt also carried a 24-item colleague proposal to adjudicate, which v6.1 drops from the main protocol):

| condition | bare | with skill |
|---|---|---|
| Sonnet 5 | 1.75 (-4.6%) | 2.2 (-4.1%) |
| Opus 5 | 3.4 (-20.5%) | 3.9 (-33.4%) |

No cell has been graded under the four-round protocol yet.

The answer key was corrected nine times by the runs themselves, so
when grading: re-verify apparently wrong agent moves against the live
environment before deducting. Three different runs each beat the
reference on some axis.

## Safety notes

- Everything here is for disposable local instances. The generator
  creates clusters and large materialized views, and the armed landmine
  (`v6_c9_arm.sh`) deliberately produces a multi-minute single-worker
  grind. Never run any of it against a shared or production
  environment.
- Two runs can share one instance (schemas are namespaced), but they
  will see each other's catalog names, and at 60 tables per environment
  three environments is the practical limit (see `max_tables` above). The recorded campaign accepted
  that for concurrent runs and observed no contamination. Reference
  environments must not be live while graded runs execute.

## Troubleshooting a run

- A runner exit code of 124 means a round hit its `timeout` budget; the
  transcript of that round is empty and the schema is left in place.
- The runner does not drop anything: before relaunching a condition, drop
  its schema and cluster (`DROP SCHEMA v6_<cond> CASCADE; DROP CLUSTER
  v6_<cond> CASCADE`) and move the previous `$EVAL_BENCH_ROOT/v6_<cond>*`
  directories aside, or the build fails on `CREATE SCHEMA`.
- `canceling statement due to statement timeout` during the build means the
  `PGOPTIONS` prefix on the build's psql was lost; the million-row insert
  needs more than the server's one-minute default on a slow host.
- Keep the runner in the foreground of a detached shell (`setsid nohup`),
  never as a background task of a tool that applies a command timeout.
