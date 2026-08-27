# Developing this skill

How mz-optimize-memory was built and evaluated, and how to test
changes to it. The runnable harness lives at
`evals/mz-optimize-memory/` in the agent-skills repository, the one
this skill is published in; its README covers operation. This file covers the
method.

## Provenance

The skill's content was distilled from real Materialize cost-optimization work,
then hardened through six generations of synthetic environments, five of them
graded by agent evaluations. Every lever, convention, and warning in the skill
rests on a measured rig result, on an outcome a graded run changed, or on a
cited source or docs statement. The evaluations also set the skill's emphasis:
plan-reading and mechanism diagnosis needed no help even from unassisted
agents, so the skill spends its tokens on lever selection, completeness,
estimation discipline, change-execution ordering, and verification, where
graded runs showed real gaps.

Two findings shaped the structure the most: no bare agent in the graded runs
discovered `EXPLAIN ANALYZE HINTS` on its own (hence its position as the
workflow's early step), and no run in any condition found the provable
LEFT-to-INNER conversion unprompted (hence its own section in
references/outer-joins.md).

## The evaluation design

One graded run is a four-round session against a generated environment
with planted constructions and a measured answer key. The harness
snapshots the schema (objects, indexes, hydration, dataflow and operator
census) after the build and after every round, so each round's
contribution is measurable on its own:

1. **Round 1, read-only.** The agent produces a first package: diagnosis, recommendations, and savings estimates with confidences. The prompt points at `mz_index_advice` as one thing to
   look at and asks for other optimizations as well. Graded separately
   because a confident, unmeasured first package is a real-world
   failure mode.
2. **Round 2, write access.** The agent validates and implements under
   an estimate gate. The round-1-to-round-2 delta shows whether the
   agent measures its way out of its own wrong first verdicts.
3. **Round 3, further optimizations.** The agent is asked to look for
   what it has not considered yet and to validate every new candidate on
   the bench (build, exactness both ways, before/after measurement),
   not to list ideas. Its yield is the round-3 checkpoint minus the
   round-2 one.
4. **Round 4, pressure and attribution.** Canned challenges ("a reviewer doubts your verdicts", re-derive the least confident ones by a different method) plus per-change attribution of the savings.
   Graded for stance stability: verdicts should change on new evidence
   only, and unforced flips score down.

Grading uses a weighted rubric (constructions found and fixed, first package quality, stability under pressure, estimate discipline, discipline and verification) against the measured answer key, plus one checkpoint row
per round boundary from the snapshots, and audits the database end
state, not just the report. Graders read the full session log: the
per-round transcript files hold only each round's last message. The key
rule learned the hard way: re-verify apparently wrong agent moves on the
live rig before deducting. The v4 answer key was corrected nine times by
graded runs, the v6 key several more, and several runs beat the reference
solution.

## The clean-room protocol

Comparisons are meaningless if the agent inherits context or can reach
answers, and both failure modes actually occurred in probe runs before
the harness closed them:

- User-level configuration (CLAUDE.md, settings, installed skills)
  leaks into nominally clean sessions unless explicitly excluded, and
  auto-memory injects project context into subagents. The runner
  excludes both.
- The agent's only route to the database is a generated psql wrapper,
  pinned to the run's schema and cluster, mode-switched read-only or
  read-write per round, rejecting flags and all but a read-only subset
  of meta-commands. Around it the CLI's permission layer allows plain
  read-only shell commands inside the run directory and the mounted
  source tree, allows writes only inside the run's scratch directory,
  and denies network access, interpreters, version control, and every
  file outside those directories. Round prompts and transcripts live
  outside the run directory so a round cannot read a later round's
  prompt.
- Answer keys must be structurally unreachable, not just "not
  mentioned": no mount contains them, and the readable Materialize
  source tree is a plain checkout.
- Before a batch, run the harness's `v6_preflight.sh`: it exercises the
  generated wrapper directly (read-only mode rejects writes, flags and
  meta-commands are refused) and then runs one short agent session with
  the runner's exact isolation flags that attempts each allowed and
  each denied operation, comparing the answers with the expected
  matrix. Re-run it after any harness or CLI upgrade.
- Verify the environment build (object counts, hydration) before
  launching agents, and audit runs against the database state.

## Testing a change to the skill

1. Edit the skill files.
2. Run at least one skill-condition cell and one bare cell via the harness. A
   cell is one model under one condition; the code is model then condition (`s`
   Sonnet, `o` Opus, `o8` Opus 4.8, `h` Haiku for smoke tests; then `s` skill
   or `b` bare): `run_cleanroom_v6.sh ss` and `sb`, or `os` and `ob`. Run cells
   one at a time on a laptop (each is one environment plus one agent session,
   two to four hours), and never as a background task of a tool with a timeout.
   Grade against the rubric, and compare with the recorded results in the
   harness README: the v4 table was measured on the v4 subset, the v6 table
   under the earlier three-round protocol, so a four-round cell compares to
   other four-round cells. A Haiku cell with `EVAL_SCALE` set smoke-tests the
   runner in minutes and is not a graded condition.
3. For a targeted edit, prefer re-running a cell that previously
   failed at exactly the behavior the edit addresses; a fixed cell is
   the cleanest evidence a skill change works.
4. Also run a plain usability pass: give a fresh agent the skill and a
   real (disposable) environment, and ask it to report ambiguous,
   incorrect, or misleading skill text alongside its findings. Verify
   every claim an agent makes about tool behavior before baking it
   into the skill; agents' own reports can rest on false observations.
5. Machine-verify every SQL snippet the skill contains against the
   current Materialize version (catalog names and EXPLAIN syntax
   drift).
