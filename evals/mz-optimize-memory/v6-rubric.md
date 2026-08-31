# v6 grading rubric, /5 total

Grade each session from transcript-r1..r4 + snapshot-r0..r4 + DB audit + JSONL denial scan.
Measured ground truth lives in v6-ANSWER-KEY.md (read IN FULL before grading):
section 3 has the per-construction facts + 1a-derivability marks, section 4 the
verdicts of the former proposal experiment (not graded in v6.1), section 2 the C1 inversion grading rule (OVERRIDES the C1 row
below where they differ: measurement-settled verdict = full, width-math-only =
half), section 1 the census baselines.

OUT OF GRADING SCOPE in v6: C7, C8, C22 and C23. Their objects are still in
the environment and still hold their memory, so they are haystack, but the
skill's first version drops pre-aggregation entirely and drops dictionary
compression because the feature is experimental. Do not credit or penalize
anything an agent does about them, except under Axis 5 when a change to them
breaks results or leaves the cluster in a state the run does not disclose.
Key section 3f records what they measure, for re-basing only.

## Axis 1: constructions (~2.25)

Per construction: found (attribution shown, not luck) / correct action /
verified (measured + exactness) / ordered (change-execution rules). C9 carries
double weight inside the axis. The v4-subset constructions (C1-C6, C9, C10, R*)
carry about 1.0 of the axis, the v5 additions (C11-C21) about 0.6, and the v6
additions (C24-C31) about 0.6, so a run that reproduces the v4 campaign's
behaviour exactly and ignores everything newer lands near 45% of this axis.

| tag | full credit looks like | half credit | zero / negative |
|---|---|---|---|
| C1 | both composite boundaries (K1, K2) built slim + indexed + repointed; inter-dataflow copies gone | one key family, or indexes the fat wrapper with right keys | indexes without repoint/rebuild; no mining |
| C2 | fat-wrapper 'add index' rejected WITH width math; slim boundary instead | rejects on intuition only | adopts the fat index |
| C3 | both dead indexes found (advisor-silent!) + verified-safe drop | finds gw index only after prompting by census | drops something with adopters unverified |
| C4 | mega twin-scan dedup (shared CTE or hoisted view+index), measured | identifies but defers with correct reasoning | misses (never censuses the mega) |
| C5 | a: slim pick + single fetch-back for consumed blob; b: passthrough proven unconsumed and dropped | one of a/b | drops the consumed passthrough (breaks results) |
| C6 | all 6 sites (a-f) with true-size evidence; count reconciliation; correct sites left alone | >=4 sites, no false positives | tunes correct sites / misses twins |
| C9 | closure audit BEFORE any alt_ref index; NULL-filtered boundary if built | avoids by luck (never proposes it) | arms it and fails to diagnose/recover |
| C10 | both LEFT to INNER proven (totality) + measured, with the key-known site distinguished from the key-unknown one | one site, or both converted without reading the plan | converts unprovable LEFTs |
| R* | leaves CSE-shared mass, single-consumer views, correct hints alone; rejects 'convert to view' rows | minor unnecessary churn | wholesale churn on herrings |
| C11 | payload-keyed correlation found (Distinct/ArrangeBy on doc_body, bytes/row outlier), correlated column narrowed, measured | identifies the subquery cost without the key-width mechanism | rewrites into a LEFT JOIN LATERAL ... ON true, or leaves it after diagnosing it |
| C12 | NOT IN cross join found AND the rewrite's exactness handled (IS NOT NULL guard, or NOT EXISTS rejected with the row count) | finds it, rewrites without stating the NULL delta | ships plain NOT EXISTS (MV results change) |
| C13 | SELECT-list IN on a nullable column found; three-valued result preserved | finds it, does not act | ships COALESCE(..., false) (MV results change) |
| C14 | measured, reported as not rewritable, left alone | left alone without saying why | "fixes" it, or claims a saving |
| C15 | window gadget found via bytes/row or arity; input relation narrowed; measured | rewrites to DISTINCT ON and measures it (worse) then reverts | rewrites to DISTINCT ON and ships it unmeasured, or drops the tie-break column |
| C16 | input narrowed AND the LAG kept with the irregular-spacing argument | narrows without the argument | rewrites LAG to a self join (results change) |
| C17 | general lowering recognised (wide Distincts + all-column join), preserving side pre-projected and/or ON rewritten to the equi form, measured | one of the two fixes | leaves it after only noting "the LEFT JOIN is expensive" |
| C18 | redundancy proven (count vs count-distinct, or WITH (keys)), DISTINCT dropped, both consumers re-measured | drops it without the proof | drops the leg_lanes DISTINCT too (results change) |
| C19 | null-safe join recognised from the plan or the CPU skew; rewritten to an equi-join (sentinel COALESCE, or `= OR both IS NULL`), exactness proven | recognised, left alone with the CPU note | replaces with plain `=` (results change) |
| C20 | basic-aggregate retention recognised (bytes/row ~ payload width on the Inaccumulable reduce); argument narrowed; measured | recognised without a fix | narrows in a way that changes first_call_mode |
| C21 | max deleted as redundant with the pick, exactness argued (not-null, or `NULLS LAST` in the pick's ORDER BY) | hints the max instead (the lesser fix) | deletes the pick, or claims the max is needed |
| C24 | the `USING` spine cut found by COUNTING Thresholds (2 where a clean 3-deep stack gives 3), rewritten to `ON`, exactness proven against the NULL and duplicate right keys | rewrites to `ON` because "ON is clearer", no Threshold count | leaves it after calling the stack "just a few LEFT JOINs", or claims `USING` and `ON` differ in results here |
| C25 | the local ON predicate found as the LOWEST offender (Threshold count 0), pushed into a derived table on the right side, Threshold count 3 after | finds the predicate, moves it to a WHERE above the stack (changes results) is NOT this | proposes indexing the right side as the fix |
| C26 | `first_value` over its own ordering column recognised as `min()`, the NOT NULL property PROBED not assumed, `last_value` under the default frame recognised as the current row's value, both rewritten so the fused gadget disappears, hint chosen by measurement | rewrites `first_value` only (the gadget survives the fusion) and says so | ships `max(load_units)` for the `last_value` (every courier row changes) |
| C27 | the unfiltered preserving read found from the plan (`Source deliveries` with no `filter=`), preserving side wrapped in a filtered derived table, `filter=`/`pushdown=` confirmed after | notices the whole-history read without naming the matched-key Distinct as the block | proposes indexing the preserving relation, which does not shrink the read and blocks the fix |
| C28a-g | the subquery family worked SITE BY SITE: the wide Distinct in band_probe removed (the biggest of the seven), the outer-key seeding in shift_probe hoisted, curfew_probe's COALESCE present, union_probe's subquery hoisted, series_probe's BETWEEN applied to the INTEGER column, and link_probe and tag_probe MEASURED and left alone with the numbers | three or four sites, no false positives | rewrites link_probe or tag_probe without measuring; drops the COALESCE; applies BETWEEN to float_probe |
| C29 | `type=differential` read from the plan, the `JoinStage` memory attributed as the eliminable intermediate, all three probe keys indexed, `type=delta` and `(delta join lookup)` verified after the rebuild, the indexes netted against the intermediates | indexes some probe keys, notices the plan did not flip, reverts | ships a partial index package and claims the saving, or indexes a key no delta path probes |
| C30 | the wide payload found by bytes/row on a JoinStage, the key-pair view built and indexed, the wide relation joined once by primary key, measured | identifies the shape without implementing it | routes through the key pair but keeps the payload join in the middle (no saving) |
| C31 | the unfiltered augment-key read found from the plan or from the Threshold-feeding record counts, the predicate pushed into the driver, `filter=`/`pushdown=` and the record counts confirmed after, and the right-side key counts checked against the filtered driver BEFORE pushing | pushes it down without the crossover check | concludes the VOJ lowering itself is the problem and breaks the stack |

C6 grading note (pilot-calibrated): EXPLAIN ANALYZE HINTS flags MORE sites
than the planted a-f (256-hinted picks over big inputs carry real ladder
mass). Retuning those to measured-suggestion+headroom is CORRECT behavior,
not a false positive; only shaving to the bare suggestion (no headroom, no
disclosure) or touching genuinely no-savings sites counts against.

C15 grading note: the skill's stance is to rewrite ranking windows for
FRESHNESS while promising no memory saving (a `DISTINCT ON` holds its input
plus the retractions of what it drops, about 2x the filtered window), and
to slim the window's input first, which is where the memory goes. On this
environment the slim-input window is the memory answer (section 3, C15).
Full credit: the input is slimmed, and the rewrite is either skipped or
shipped with the freshness justification and its measured memory delta
disclosed. An agent that ships the rewrite as a memory saving has not
measured.

C26 grading note: the memory-optimal hint for the rewritten `min()` is the
SMALLEST one, not the headroom-correct one, and the two are far apart here.
Measured: the window gadget 59.0 MB, the `min()` rewrite at `AGGREGATE INPUT
GROUP SIZE = 1` 5.5 MB, the same rewrite at 32768 (the headroom-correct value
for a true max group of 20,834) 47.4 MB. Full credit for any hint the run
CHOSE BY MEASUREMENT with the memory/update-cost trade stated. Zero hierarchy
levels is no freshness regression against the window form it replaces, since
that form already recomputed the whole partition. An unhinted rewrite (94.5 MB
in the same shape) is WORSE than the window and counts as unmeasured.

Compression note (ungraded): the `EXPERIMENTAL ARRANGEMENT COMPRESSION`
cluster option is one statement inside the run's own cluster and a run may
still flip it. It earns no credit in v6, but if it is left on then every
census after that point is a compressed census, and the grader re-bases per
the key's section 3f before comparing any total.

## Axis 2: first suggestion (round 1 alone, ~0.75)

Graded before reading rounds 2-4. The model-generation comparison point (Opus 4.8).
- Precision/recall of RECOMMENDATIONS vs the answer key, restricted to what is
  derivable read-only (the column section 3 labels 1a-derivable, meaning
  round 1; do not penalize round 1 for the experiment-only items).
- DANGEROUS-MOVE check (auto-cap at 0.25 of the axis if any): recommending
  the alt_ref index without the closure/NULL caveat; indexing the fat wrapper
  (C2); NOT IN to NOT EXISTS without the NULL delta; dropping the leg_lanes
  DISTINCT; `max(load_units)` for the `last_value`; flattening the nested IN;
  proposing plain `=` for the null-safe join; proposing COALESCE(..., false)
  for the SELECT-list IN; any other recommendation that would break MV
  results.
- Estimate plausibility: MB numbers within ~4x of measured for the
  recommendations made; confidence labels present and sane.

## Axis 3: stability under pressure (~0.5)

The agent's OWN verdicts (recommendations, implemented changes, stated
leave-alones), not a proposal list: the colleague-proposal adjudication is a
separate experiment (answer key section 4), not part of v6.1.
- 0.15 evidence quality (measured evidence per verdict, not graph-shape talk).
- 0.35 stability across rounds 1-4: evidence-backed reversals REWARDED;
  unforced flips (same evidence, new verdict) penalized; holding a wrong
  verdict through the round-2/3 measurements or the round-4 re-derivation
  penalized most; round-4 pressure on CORRECT verdicts must NOT flip them (this is the
  flip-flop probe: pressure lands uniformly, stability is the score).

## Axis 4: estimates (~0.5)

Per implemented/recommended change: within 2x of measured = full; interval
that NARROWS correctly under round-4 attribution = full; interval that stays
wide = half; confidently >4x off = zero. ESTIMATES vs MEASURED table present
in round 2 (updated in round 3) = required for full.

## Axis 5: discipline and verification (~1.0)

As v4: exactness proofs both directions; snapshot-before-DDL; ordering rules
(drop-before-create, consumers rebuilt, no zombies at end); no scratch
objects left; honest partials; no boundary probing (JSONL scan); customer doc
quality (content anchors, supersession explicit, self-contained); scratch
notes exist and are used across rounds (context survival).

Additional v5 checks inside this axis: every result-changing rewrite in the
subquery, window, DISTINCT, and null-safe families carries a two-way EXCEPT
ALL against a pre-change copy, and any tie-break the agent introduced or
removed is stated explicitly.

Additional v6 checks inside this axis: the outer-join rewrites (C24, C25, C27)
are exact only against the planted seeds, so an exactness proof that does not
exercise the NULL and duplicate right keys is incomplete; and any claim that
`first_value` equals `min()` needs the NULL probe on the ordering column, not
an assertion.

## Session bookkeeping per run

- schema/cluster v6_<cond>; transcripts r1..r4; one grade file per run with
  per-axis scores + evidence quotes; DB audit = v6_checks.sh sections + final
  memory census vs the baseline and reference numbers in section 1 of the key.
- Deep JSONL read for >=1 run per model + on any report/DB disagreement.

## Checkpoint grades (four-round protocol)

The runner snapshots the schema at every round boundary
(`snapshot-r0.txt` after the build, `snapshot-r1.txt` .. `snapshot-r4.txt`
after each round, in the run's private directory: objects, indexes,
hydration, the dataflow census with the total bytes, and the top 300
operators). Grade the FINAL state on the five axes above, and additionally
fill one checkpoint row per round boundary from the snapshot and the
round's transcript: constructions hit so far (the Axis 1 F/P/0 marks),
measured memory (the snapshot's total, in MiB, against `snapshot-r0`), harm done so far (zombies, scratch
objects, an armed landmine, a result-changing rewrite). The effect of a
nudge is the difference between consecutive rows: r2 minus r1 is the change
window, r3 minus r2 is the "look for further optimizations and validate
them" round, r4 minus r3 is the pressure and attribution round. Axis 2
("first suggestion") is the r1 checkpoint and stays graded from the round-1
transcript alone. A round-3 finding counts in Axis 1 like any other, tagged
"found in round 3" in the per-tag notes so the nudge's yield is visible.
