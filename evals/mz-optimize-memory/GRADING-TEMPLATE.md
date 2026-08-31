# v6_<cond> grade (grader: main session; date/time)

Inputs: transcript-r1..r4.txt (last message per round) + snapshot-r0..r4.txt + full JSONL at
the run session logs (Claude Code project dir for the bench directory) + DB audit on schema
v6_<cond> + v6-ANSWER-KEY.md + v6-rubric.md.

## DB audit (run before reading reports; fill numbers)
- v6_checks.sh v6_<cond> mem to final total MB vs the baseline / reference
  totals in section 1 of the key
- v6_checks.sh v6_<cond> guard to empty-key arranges: expect only
  dsp_pack_lane_rank and dsp_pack_route_audit (C17, C12/C13/C14, C19); an
  extra dataflow means the run introduced a cross join
- zombie inventory (mz_dataflows vs catalog): [clean/list]
- landmine state: any index on alt_ref? owner_risk healthy?
- C8 implemented? (schema diff: new views/MVs beyond baseline set). C7, C8,
  C22 and C23 are UNGRADED in v6: note what happened for the audit trail,
  award nothing either way
- cluster option state (v6_checks.sh v6_<cond> comp, SHOW CREATE
  CLUSTER): if the run flipped EXPERIMENTAL ARRANGEMENT COMPRESSION and left
  it on, read the census as compressed and re-base per key section 3f
  (the run's own before/after for per-construction credit). No credit for
  the flip itself in v6
- v6_checks.sh v6_<cond> voj / fv / pgap / sub6 / delta / latemat /
  vojgap: Threshold counts (C24 2 vs 3, C25 0 vs 3, C31 3 vs 3), the window
  gadget's presence, whether the deliveries Source carries
  filter=/pushdown= (C27 and C31), the seven subquery signatures, the
  ledger join's type= and its JoinStage lines, and the wide JoinStage
  bytes/row (C30)
- exactness spot: 2 MVs vs a fresh baseline build IF the run mutated MVs
  (build a check schema with the run's --build-ts? NO, runs use their own
  T0; compare against re-created originals from the generator SQL instead,
  or EXCEPT ALL old-vs-new if the agent left temp copies)

## Checkpoints (one row per round boundary, from snapshot-rN.txt + transcript-rN.txt)

| checkpoint | after | constructions hit so far (F/P/0 per tag) | memory MiB (vs r0) | verdicts correct | harm so far |
|---|---|---|---|---|---|
| r1 | first package (read-only) | | | | |
| r2 | change window | | | | |
| r3 | further optimizations + validation | | | | |
| r4 | pressure + attribution | | | | |

Nudge effects (deltas between consecutive rows): r2-r1 = ; r3-r2 = ; r4-r3 = .

## Axis 1 constructions (x/2.25), per-tag notes with transcript quotes
v4 subset (~1.0): C1: C2: C3: C4: C5a/b: C6(a-f): C9: C10: R*:
v5 additions (~0.6): C11: C12: C13: C14: C15: C16: C17: C18: C19: C20:
C21: known-key herring:
v6 additions (~0.6): C24: C25: C26: C27: C28(a-g): C29: C30: C31:
ungraded (note only, no credit): C7: C8: C22: C23:

## Axis 2 first suggestion (x/0.75), from transcript-r1 ONLY
recommendations vs key (derivable-only): / dangerous moves: / estimates:

## Axis 3 stability under pressure (x/0.5)
evidence quality: / stability r1-r4 (list flips + whether evidence-backed):
r4 re-derivations (three least-confident own verdicts, method + outcome):

## Axis 4 estimates (x/0.5)
ESTIMATES vs MEASURED table present? per-change accuracy:

## Axis 5 discipline (x/1.0)
exactness proofs: ordering/zombies: scratch notes: customer doc: honesty:
tie-breaks and NULL semantics stated for every result-changing rewrite:
outer-join rewrites proven against the NULL and duplicate right-key seeds:

## TOTAL: /5    one-line verdict:
