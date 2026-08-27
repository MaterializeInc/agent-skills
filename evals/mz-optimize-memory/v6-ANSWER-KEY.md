# v6 answer key

Round naming: "1a" in this file is round 1 of the four-round protocol (the read-only first package); "1b" is round 2 (the change window).

Three measurement eras are recorded here and they are kept apart on purpose.

- The **v4 subset** rows (C1 to C10, R*, proposal items 1 to 15) were
  measured on a dev rig on 2026-08-18 and corrected nine times by graded
  runs. `build_v6.py --v4` still emits that environment byte-identically,
  so those numbers remain the ground truth for the subset. Re-measured on
  a v26.38.1 Docker emulator (100cc) on 2026-08-25 the subset's total came
  out at 1,511 MB against the rig's 1,519 MB, so the rig numbers transfer
  within a few MB.
- The **v5 environment** rows (C11 to C23, proposal items 16 to 20) were
  measured on that same emulator on 2026-08-25, on a baseline and two
  reference builds that shared one `--build-ts`. Graded on 2026-08-27 by four
  three-round cells (corrections below). The v5 HEADLINE totals are superseded by the v6 ones below,
  because v6 adds objects to the same environment.
- The **v6 environment** rows (headline totals, C24 to C27, proposal items
  21 to 23) were measured on a v26.38.1 emulator on 2026-08-26, per
  construction in an isolated lab (each variant behind its own index, so
  each is its own dataflow) and end to end on a baseline and reference
  pair sharing one `--build-ts`. Graded on 2026-08-27 by the same four cells
  (corrections below).

Corrections from the v6 runs (2026-08-27, four three-round cells, every
item re-verified by the coordinator on the live schemas; details in
eval/runs-v6/MATRIX.md):

- C28g: the `IN (SELECT generate_series(a, b))` -> `BETWEEN` rewrite (former
  subqueries.md rewrite 10) was removed from the skill on 2026-08-27 (skill
  checklist E10, revisit after the first PR). The construction and its float
  herring stay in the environment; a skill-condition agent is not taught it,
  so count a C28g find as skill-independent and never deduct for missing it.
- C4 measures about 12 MB on v6 (the 41 MB x 2 figure in the table is the
  v4 anchor's), so its saving is roughly a third of the table's estimate.
- C10 (and the former proposal item 20): the conversions change the declared nullability of `anchor_id`. NOT graded in v6.1: declared-nullability changes are a follow-up topic (skill checklist E7); note it in the per-tag notes without a deduction.
- C15: `DISTINCT ON` at a small hint with a narrow projection is a valid
  middle option (about 72 MB), between the window form and the full rewrite.
- 3d: a rebuild of a consumer resurrects the "dead" serving index (plans
  adopt at CREATE), so "dead" holds only until the next rebuild.
- C30 has a cheaper route than the key's: the delta package alone.

C7, C8, C22 and C23 are OUT OF GRADING SCOPE in v6. Their objects are still
built and still hold their memory, so they remain haystack for the census,
but the skill's first version drops pre-aggregation entirely and drops
dictionary compression because the feature is experimental. Their measured
facts are kept in section 3f, for re-basing and for the DB audit, not for
credit.

Environment: `build_v6.py <schema>` (baseline). Reference solutions:
`build_v6.py <schema> --reference` (optimal) and
`--reference-conservative` (the width-math-only variant). All three built
from ONE shared `--build-ts T0` so cross-schema EXCEPT ALL at a single
instant proves exactness (INSERT..SELECT snapshots are impossible here:
mz_now() in the chain rejects write-statement reads, and agents hit this
too, so the live temp-name/cross-env comparison is the valid route).

`--build-ts` must be at or before wall-clock now. A future anchor puts
most of the 24-hour anchor window ahead of `mz_now()`, the spine comes out
a fraction of its designed size (measured: 3,690 rows instead of 10,345
for an anchor two hours ahead), and every per-anchor construction shrinks
with it.

## 1. Headline numbers

Measured on a v26.38.1 emulator (100cc, 2 workers) on 2026-08-26, all
builds from one shared `--build-ts`.

| build | total MB | saved | note |
|---|---|---|---|
| baseline | 2,407 | - | 14 MVs + 6 serving idx + 2 dead idx |
| reference (optimal) | 1,515 | **892 MB, -37.1%** | boundaries + all fixes |
| reference-conservative | 1,632 | 775 MB, -32.2% | no boundary views/indexes |

The boundary bundle is therefore worth **+117 MB net** in v6, up from the
+111 MB measured on v5: three more spine-driven dataflows, so the spine
index and the composite boundaries dedup more again.

A fourth number sits outside that table because it is a replica property
rather than a SQL fix, and because dictionary compression is OUT OF
GRADING SCOPE in v6: with `EXPERIMENTAL ARRANGEMENT COMPRESSION = true`
the v5 baseline measured 1,886 MB against 2,006 MB (-6.0%), reversible,
with three dataflows GROWING. Section 3f says what to do if a run leaves
it on.

Census tolerance: read the totals to about +/- 30 MB and per-dataflow
lines to about +/- 10 MB. Two things move them without any change to the
environment: the 24-hour spine ages out at roughly 1%/h, and a freshly
rehydrated cluster sits at a different trace-merge state than one that has
been up for fifteen minutes.

Where the 892 MB sits: the v4-subset and v5 dataflows contribute about
587 MB net and the three v6 dataflows 305 MB (ledger_board 242 to 49,
yard_board 130 to 42, ref_probe 29 to 5).

Exactness: EXCEPT ALL both directions x 14 MVs = 0/0 for BOTH reference
variants against the baseline, at full scale, plus a `--scale 100`
mini-proof of the baseline against `--reference`. Load takes about 12 minutes on this emulator with
a second environment building alongside it, and hydration about 3 minutes
after the load returns, well inside the runner's 120 x 10 s bound.

Per-dataflow census (MB), for the DB audit:

| dataflow | baseline | reference |
|---|---|---|
| dsp_pack_saga_vector | 477 | 420 |
| dsp_pack_lane_profile | 291 | 226 |
| dsp_pack_lane_rank | 276 | 78 |
| dsp_pack_depot_profile | 245 | 130 |
| dsp_pack_ledger_board | 242 | 49 |
| dsp_pack_owner_risk | 201 | 166 |
| dsp_pack_leg_totals | 142 | 40 |
| dsp_pack_yard_board | 130 | 42 |
| dsp_pack_audit_trail | 128 | 51 |
| dsp_pack_courier_board | 57 | 46 |
| dsp_pack_route_audit | 52 | 5 |
| dsp_pack_depot_pulse | 46 | 16 |
| idx_gateway_calls_kind | 33 | dropped |
| dsp_pack_ref_probe | 29 | 5 |
| dsp_pack_ops_snapshot | 22 | 15 |
| idx_dsp_pack_saga_vector | 18 | 18 |
| idx_dsp_pack_courier_board | 5 | 5 |
| idx_dsp_mid_ident_flags | 4 | 1 |
| idx_couriers_home | 3 | dropped |
| idx_hist_by_depot | - | 106 |
| idx_hist_by_lane | - | 59 |
| idx_hist_by_alt | - | 18 |
| idx_spine | - | 4 |
| idx_ledger_runs_route / _rate / _zone | - | 3 each |

## 2. THE C1 INVERSION (grade with care: this is the deepest finding)

Static width math says REJECT the composite boundaries: idx_hist_by_depot
costs 106 MB (11-col union, 1M rows) against only ~52 MB of demand-slim
private join-input copies (13-18 MB each x 4 dataflows); idx_hist_by_lane
59 vs ~21. But the measured A/B says ADOPT: the boundary variant beats
boundary-free by **+117 MB net** (1,632 against 1,515), because the shared arrangements
restructure the multi-way join plans, the intermediate JoinStages (for
example the 714k-row 11 MB stage in depot_profile) vanish, and
`Used Indexes` shows `(differential join)` / `delta join` paths. Width
math on join inputs alone CANNOT see this. (This is the eager-delta
walk-back arc inverted: there the flag looked good and measured bad; here
the boundary looks bad and measures good.)

Third face of the inversion (measured by run v4_ob during its 1b, on the
v4 subset): adopting item 1 VERBATIM (full-width index on the 16-col
wrapper) and rebuilding depot_profile sent that dataflow 175 to 2,303 MB
and climbing (delta-flip with fat intermediates) before the agent
aborted. So: fat index verbatim = catastrophic; slim boundary + measure =
+117 net; width-math-only = leaves 117 on the table. All three faces are
measured ground truth.

Grading C1:
- FULL: mined the cross-dataflow duplicates AND settled the verdict by
  measurement (A/B or staged deploy with per-dataflow census) or by the
  delta-plan argument read from EXPLAIN.
- HALF: width-math-only rejection (disciplined, wrong stopping point) or
  boundary built with no width awareness at all.
- ZERO: no mining, or index-on-the-fat-wrapper verbatim (items 1/2)
  without slimming.

## 3. Per-construction ground truth

### 3a. The v4 subset (rig numbers, run-corrected)

| tag | measured facts | correct action | contribution | 1a-derivable? |
|---|---|---|---|---|
| C1 | K1 copies @1M in 4 dataflows (13/13/18/8 MB) + K2 in 2 (17/4); boundary A/B above | slim boundary views + composite idx + repoint, VERDICT BY MEASUREMENT | +117 MB net in v6 (bundle incl. C9-safe alt + spine idx) | mining yes; verdict needs experiment |
| C2 | fat wrapper idx measured 1.8 MB @ 481 B/row vs ~1 MB privates (couriers = 3.8k rows) | reject with width math (materiality ~0; verdict quality graded, not MB) | ~0 | yes |
| C3 | idx_gateway_calls_kind 33 MB (blob rides) + idx_couriers_home 3 MB; advisor-SILENT; catalog DROP alone frees NOTHING, replicas keep both dataflows (plan-level adoption, invisible in mz_object_dependencies; NOTICE lists pinners). In v5 the gateway index has THREE pinning MVs (saga_vector, audit_trail, and the new leg_totals), not two | drop + rebuild pinning consumers (ordered) | 36 MB | drop-reco yes; zombie mechanics surface only on deploy |
| C4 | twin JoinStages 41 MB x 2 @ 565k in saga (hxm join idv, divergent projections) | merge to one union-projection join (hist_j) | ~12 MB on v6 (the v4 anchor measured 41 MB x 2; saga -57 incl. C5a/mega hints) | yes (census shows twins) |
| C5a | gw blobs ~2.1 kB/row ride log_rows + 2048-pick ladder; raw_payload IS consumed by saga MV | extract-in-place; ONE fetch-back join on unique call_id for the blob | part of saga -57 | yes (bytes/row) |
| C5b | gw_probe passthrough NOT consumed by audit_trail | extract-in-place + DROP the passthrough | part of audit -78 | yes |
| C6 | true sizes: c6a 34 (hint 65536), c6b 10 (4096), c6c 27 (65536), c6d twin_a 186 (65536; twin_b 256 correct, landmark method to tell them apart), c6e 5,625 (256 UNDERsized), c6f un-hinted 30-day ladder (true ~14k) | retune to 64/16/64/256/8192; ADD 16384 at c6f; leave all <=16x-headroom sites alone (incl. gw 2048 vs true 402, K2 128 vs 67) | c6f ~25-30 (in depot -122); others small | yes (EXPLAIN ANALYZE HINTS) |
| C9 | 4.3% NULL alt_refs; baseline pushes IS NOT NULL below private arrangements; naive shared idx (item 7) + consumer rebuild = one-worker produce-discard grind >611 s (did not hydrate within the 10-min watch; NULL_MOD=23, ~39M closure pairs) vs 27 s clean, flat memory, introspection sluggish; recovery = drop MV FIRST (pinning), then idx | closure audit BEFORE deploy; NULL-filtered boundary (in ref bundle) | safety, not MB | danger flaggable read-only (plan closure audit) |
| C10 | lane_first & delay_bands = spine row count exactly (totality provable by SELECT). The two sites are NOT equivalent: delay_bands groups by anchor_id alone and so exports a unique key, which SemijoinIdempotence already used to collapse its diamond, while lane_first groups by (delivery_id, created_at) and projects created_at away, so no key is derived and the full equi diamond (matched-key Distinct + second join) is present | LEFT->INNER x2 in lane_profile (low-risk clause); the prize is on the lane_first site | ~2-5 | yes |
| R* | mega hx/hxm shared (single copies); single-consumer views; 65536 owner-sites correct (whale 41,666); MV 'convert' advisor rows; depots decoy row (97 rows, immaterial either way). Also: every MV's LEFT JOIN stack lowers as a VOJ, so `Threshold local` operators are everywhere and are NOT a construction. Four `count(DISTINCT ...)` sites exist (depot_history lane_code, lane_history depot_id, mega sl_90d match_key2, alt_share courier_id); each adds the arrangement pair the cost model describes, all four are honest, and none is a lever | leave alone / reject with materiality stated | 0 | yes |

### 3b. The v5 constructions (emulator numbers, 2026-08-25)

Contribution = baseline minus reference for that construction's operators,
measured per operator inside the three new dataflows.

| tag | measured facts | correct action | contribution | 1a-derivable? |
|---|---|---|---|---|
| C11 | 7 operators in route_audit at ~1,480 B/row over 4,442 documents = 43.9 MB: `Distinct project=[#0{doc_body}]`, two ArrangeBys keyed on doc_body or on the split_part expression, the Reduce, and the join-back diamond. The document IS the correlation key | extract the header code into a CTE first (or precompute the count per code and LEFT JOIN it); the correlation key shrinks from ~1.5 kB to ~8 B | **-44 MB** (43.9 to 0.1) | yes (bytes/row sweep, or `EXPLAIN ... WITH (arity)`) |
| C12 | `Union{Negate{Distinct{Filter((#0) IS NULL OR (#0 = #1)){CrossJoin` over an empty-key arrange pair; 9,881 rows survive the filter, 451 spine rows have a NULL alt_ref | keep the semantics: `alt_ref IS NOT NULL AND NOT EXISTS (...)`. Plain `NOT EXISTS` yields 10,338 rows, **452 more than the original** | ~-1.5 MB (memory is not the point) | yes |
| C13 | `Reduce group_by=[#0{alt_ref}] aggregates=[any((#0 = #1))]` over a CrossJoin, wrapped in `Map (false)` / `Map (null)` diamonds | a CTE plus `CASE WHEN alt_ref IS NULL THEN NULL ELSE ... END`. `COALESCE(..., false)` changes the same **452 rows** from NULL to false | ~-0.5 MB | yes |
| C14 | `Distinct project=[#0{load_units}]` feeding a CrossJoin with `Filter (band_lo < load_units)`: the correlation is an inequality, so no equi-join exists | measure, report as not rewritable, LEAVE ALONE. Shrinking the inputs (bucketing load_units) is the only lever and is not worth it here | 0 by design | yes |
| C15 | `Arranged FusedReduceUnnestList` 700,000 records at **185 B/row** = 123.8 MB: the gadget packs all 16 wrapper columns. Partition population: 3,824 couriers, max 33,333 (the whale) | narrow the window's input relation to the five columns the query uses: 66 B/row, 44.4 MB | **-79.4 MB** | yes (bytes/row outlier on an UnnestList operator, or the arity gap) |
| C16 | `Arranged FusedReduceUnnestList` 150,000 at 196 B/row plus its output at 176 B/row = 53.0 MB. Max partition 8,333; `created_at` spacing is irregular | slim the input relation to three columns (12.0 MB). Do NOT rewrite to a self equi-join: the spacing is irregular, so there is no window-free equivalent | **-41.0 MB** | yes |
| C17 | the general lowering, verbatim: two `Distinct project=[#0..=#14]` at 157 B/row over 50,000 preserving rows, two full-width ArrangeBys, one `ArrangeBy keys=[[]]`, 45.0 MB in all. Every row falls in a band (`band_label IS NULL` count = 0) | both fixes, both exact: pre-project the preserving side to (delivery_id, courier_id, load_units), and rewrite the ON to `band_id = floor(load_units / 10)::int4`. Pre-projection alone measured 11.5 MB, the equi rewrite alone 33.7 MB, both together 1.8 MB | **-43.2 MB** | yes (`WITH (arity)`) |
| C18 | `SELECT DISTINCT *` over a 100,000-row slice; each of the two consuming dataflows builds a `DistinctBy` + `Arranged DistinctBy` pair at 84 B/row = 16.2 MB each. Redundancy proof: rows = distinct delivery_id = 100,000 | drop the DISTINCT in dsp_mid_leg_events. Do NOT drop the one in dsp_mid_leg_lanes: 100,000 rows collapse to 5,196 there | **-32.4 MB** (both consumers) | yes (count vs count-distinct) |
| C19 | `CrossJoin type=differential` over two `ArrangeBy keys=[[]]`; 2,592 x 3,000 = 7.78M pairs for 51,765 output pairs. EXPLAIN ANALYZE CPU WITH SKEW: `Differential Join` at cpu_ratio 0.01 / **1.99** on two workers, 5.37 s of one-worker elapsed | `COALESCE(seal_code, '~unset~') = COALESCE(...)`: exact (0/0), 0.03 s, no skew. `a.seal_code = b.seal_code OR (a.seal_code IS NULL AND b.seal_code IS NULL)` is the other exact form: the planner turns it back into an equi-join and it needs no sentinel; either earns full credit. Plain `=` drops the 46,000 NULL-NULL pairs and **200 anchors lose their row entirely** | -0.8 MB memory, -5.3 s CPU | plan yes; skew needs the hydrated dataflow (still read-only) |
| C20 | `Arranged ReduceInaccumulable` 13,462 at **2,086 B/row** = 26.8 MB plus its output 9,070 at 3,078 B/row = 26.6 MB plus the join input 13,459 at 2,081 B/row = 26.7 MB: the basic aggregate retains every payload | narrow the aggregate's argument to `jsonb_build_object('m', payload ->> 'k_mode')` and read `-> 0 ->> 'm'`. Outputs identical | **-53.4 MB** | yes (bytes/row on an Inaccumulable reduce) |
| C21 | a `DISTINCT ON` pick ordered by `mark_units DESC` and a sibling un-hinted `max(mark_units)` over the same relation and key. Seven `Arranged MinsMaxesHierarchical input` levels at ~63.6k records each. Redundancy proof: 0 rows where the pick's value differs from the max, over 10,331 | delete the max aggregate and read the value from the pick (exact: mark_units is never NULL). Hinting the max instead is the lesser fix | **-10.4 MB** | yes |
| R (item 20) | dsp_mid_dock_tally groups by anchor_id alone, so `EXPLAIN ... WITH (keys)` shows `keys: "([0])"` on its read and the MV's LEFT JOIN to it lowers with the anti-join branch reusing the main join's CTE: no matched-key Distinct, no second join | reject or call immaterial. An isolated A/B measured 4.72 MB LEFT against 4.33 MB INNER, so the conversion is worth about 0.4 MB, not zero but not a lever | ~0 | yes (plan) |

### 3b2. The v6 constructions (emulator numbers, 2026-08-26)

Contribution = an isolated lab A/B: the baseline form and the reference form
of the same view, each behind its own index so each is its own dataflow, over
the same 1,000,000-row fact table on a 100cc replica.

| tag | measured facts | correct action | contribution | 1a-derivable? |
|---|---|---|---|---|
| C24 | a 3-deep LEFT JOIN stack over a 200,000-row driver, written `USING (delivery_id)` where the driver's leftmost column is `courier_id`. The first join plans a Project the VOJ collector will not walk through, so the BOTTOM join is lowered per join and `Threshold` count is **2**, not 3. 27.9 MB / 1,813,292 records | `ON d.delivery_id = r.delivery_id` on all three joins: `Threshold` count 3, 19.8 MB / 1,214,295 records. Exact both ways (0/0) including the NULL-key and duplicate-key seeds | **-8.1 MB** | yes (count Thresholds in the plan) |
| C25 | the same stack written with `ON`, but the SECOND join carries `AND k.dock_code = 'dk2'`. The lowering attempt bails: `Threshold` count **0**, and the joins below it are too few to keep a VOJ of their own. 25.3 MB / 1,812,870 records | the predicate into a derived table on the right side (`LEFT JOIN (SELECT * FROM yard_docks WHERE dock_code = 'dk2') AS k ON ...`): `Threshold` count 3, 18.0 MB. Exact both ways (0/0). Lifting it to a WHERE above the stack is NOT exact, it turns the LEFT JOIN into an inner filter | **-7.3 MB** | yes |
| C26 | `first_value(created_at) OVER (PARTITION BY courier_id ORDER BY created_at, delivery_id)` fused with `last_value(load_units)` over the same window into ONE `fused_value_window_func` gadget, over the 500,000-row heavy-load half of the history. 59.0 MB / 1,049,712 records. `created_at` has zero NULLs in the slice, and `(created_at, delivery_id)` is unique per partition | `first_value` over its own ordering column IS `min()`; `last_value` under the DEFAULT frame is the CURRENT row's value, so its only exact rewrite is the bare column. Both must go or the fused gadget survives. `min(created_at) GROUP BY courier_id` at `AGGREGATE INPUT GROUP SIZE = 1` plus `sum(load_units)`: 5.5 MB, exact (0/0) | **-53.5 MB** | yes (bytes/row on the gadget, or grep the plan for the window names) |
| C27 | an equi LEFT JOIN from the whole 1,000,000-row fact history to a 142,857-row `toll_grades` that is unique on `delivery_id` in the DATA but declares no key (a table declares none), with the consumer's `promo_code IS NOT NULL` (111,111 rows) sitting ABOVE it. The matched-key Distinct blocks the predicate: `Source materialize.<s>.deliveries` carries NO `filter=` and no `pushdown=` line, and the join input runs at history scale. 19.0 MB / 1,546,182 records | wrap the preserving side in `(SELECT * FROM dsp_deliveries_full WHERE promo_code IS NOT NULL)`: 5.1 MB / 292,214 records, and the Source gains `filter=((#13{promo_code}) IS NOT NULL)` and the matching `pushdown=`. Exact both ways (0/0). Nothing indexes the preserving relation, so no adoption competes for it. The second documented workaround is also live here: routing `toll_grades` through a `GROUP BY delivery_id` view declares the key, SemijoinIdempotence removes the Distinct, and the predicate pushes into the source read by itself | **-13.9 MB** | yes (plan reading, no experiment needed) |
| C28a | rewrite 3, a subquery in a LEFT JOIN's `ON`. The `ON` becomes a Theta predicate and forces the GENERAL lowering: `Distinct project=[#0{delivery_id}..=#15{risk_score}]` over the 16-column spine. 15.88 MB / 97,378 records | lift the subquery into a CTE that filters the right side, then LEFT JOIN on the equality alone: 1.35 MB / 41,044 records, exact (0/0) | **-14.5 MB** | yes (`WITH (arity)`) |
| C28b | rewrite 4, `IN` over an aggregating subquery in a top-level WHERE, the non-false-friend. The outer keys seed the aggregate: a `Distinct project=[#0{courier_id}]` over the SPINE, a semijoin into `shift_logs`, a `Reduce group_by=[courier_id]`, and a join back. NO CrossJoin appears on this release. 1.67 MB | hoist the subquery into a CTE and JOIN it (a `GROUP BY` key is unique, so no `DISTINCT` is needed): 0.91 MB, exact (0/0) | **-0.8 MB** | yes |
| C28c | rewrite 5, nested `IN (... IN (...))`. **MEASURED HERRING**: v26.38.1 already decorrelates it into two clean semijoins with a `Distinct` each, no CrossJoin, and the correlated-EXISTS rewrite is plan-identical (1.16 MB both ways) | measure, report as already handled, leave alone. TRAP: flattening either level into a JOIN over `carrier_links`, whose `carrier_code` repeats, yields 149,325 rows instead of 3,276, **+146,025 rows** | 0 by design | yes |
| C28d | rewrite 6, `= ANY(<list column>)`. The `Distinct` and the join-back are keyed on `[#0{lane_code}, #1{tag_list}]`, the list riding the arrangement, and a `FlatMap unnest_list` sits under it. 2.33 MB | **MEASURED HERRING on this data**: the `unnest` + `DISTINCT` rewrite measures 3.17 MB, WORSE. Measure it and keep the list form. TRAP: the same rewrite WITHOUT its `DISTINCT` adds **2,566 rows**, because each tag list repeats two fixed lanes | +0.8 MB if shipped | yes |
| C28e | rewrite 8, a correlated aggregate with an equality correlation. 1.69 MB / 61,258 records: a `Distinct` over `courier_id`, the count, and the join back | `WITH m AS (... GROUP BY courier_id) LEFT JOIN m` **plus `COALESCE(..., 0)`**: 1.29 MB, exact (0/0). TRAP: the same rewrite without the COALESCE turns 0 into NULL on the **2,142** spine rows whose courier has no `curfew_windows` row | **-0.4 MB** | yes |
| C28f | rewrite 9, the same subquery text in two UNION branches. The plan carries TWO `Reduce ... aggregates=[count(*)]` over `shift_logs`, one per branch: CSE matches only structurally identical subtrees and decorrelation gives the copies different shapes. 1.47 MB | hoist it into a CTE and join both branches to it: 0.82 MB, exact (0/0) | **-0.65 MB** | yes (count the Reduces) |
| C28g | rewrite 10, `IN (SELECT generate_series(10, 40))` on the INTEGER `depot_id`: a `Distinct` over `depot_id` feeding a `FlatMap generate_series`. 0.95 MB | `depot_id BETWEEN 10 AND 40`: 0.23 MB, exact (0/0). HERRING beside it: `dsp_mid_float_probe` runs the same shape on the FLOAT `load_units`, where `BETWEEN` is NOT equivalent (75 rows in the series, 2,997 in the range, **+2,922 rows**) | **-0.7 MB** | yes |
| C29 | a four-input join whose driver is probed on `route_code`, `rate_code` and `zone_code`. `type=differential`, and two `JoinStage` arrangements at 200,000 records hold 35.1 and 20.1 MB: the eliminable intermediates. Whole dataflow 60.3 MB | index `ledger_runs` by ALL THREE probe keys (the flip is all-or-nothing: with only two the plan stays differential and reads one index as `(*** full scan ***)`). The plan then shows `type=delta`, `(delta join lookup)` on two and `(delta join 1st input (full scan))` on the third, the JoinStages are gone, and the dataflow is 2.4 MB against 3 x 3.5 MB of index | **-47.4 MB** (60.3 to 12.9 net of the indexes) | shape yes, verdict needs the experiment |
| C30 | late materialization. `parcel_units` (150,000) joined to the WIDE `holders` (20,000 rows, eight ~42-character payload columns) and then to `carriers_wide` keyed off the holder. The payload is consumed, so projection pushdown cannot prune it: the second join's `JoinStage` holds 150,000 records at **365 B/row = 54.8 MB**. Whole dataflow 66.6 MB | a narrow `(holder_id, carrier_ref)` key-pair view, the chain routed through it, `holders` joined once by `holder_id` at the end: the wide stage becomes 2.7 MB, whole dataflow 43.4 MB, exact (0/0) | **-23.2 MB** | yes (bytes/row on a JoinStage) |
| C31 | the VOJ pushdown gap. A clean three-deep stack (`Threshold` count 3) off the `deliveries` TABLE with a 1%-selective predicate ABOVE it. The augment-key branch reads the driver unfiltered, so the dataflow holds **11,009,503 records / 70.7 MB** and `Source ... deliveries` carries NO `filter=` line | push the predicate into the driver below the stack: 119,503 records / 1.6 MB, `filter=((#15{risk_score} < 0.01))` and the matching `pushdown=` appear, exact (0/0). The right sides hold 1,000 keys each against 10,000 filtered driver rows, which is the side of the crossover where pushing down wins | **-69.1 MB** | yes (plan reading) |

### 3c. Beyond the reference (known, not built)

- **C20 residual.** The reference leaves 26.7 MB in the gateway join input,
  because the narrowed aggregate still reads `payload ->> 'k_mode'` off a
  full-width row. Extracting that field in the gateway wrapper (the
  skill's extract-in-place lever, the same move as C5) removes it. An
  agent that does both beats the reference by roughly 26 MB.
- **C15 versus the DISTINCT ON rewrite.** Measured four ways on 700,000
  rows and 3,824 partitions: window over the wide input 124.6 MB, window
  over the slim input 44.8 MB, `DISTINCT ON` with a 1024 hint 97.9 MB,
  `DISTINCT ON` with the correct 65536 hint (the whale partition holds
  33,333 rows) 125.3 MB. All four produce identical rows. The mechanical
  rewrite the skill recommends by default is a LOSS here. The projection
  fix is the win. See the rubric's C15 note.
- **C26's hint is the whole prize.** The rewritten `min()` is a
  non-monotonic hierarchical reduce, so its cost is levels times a retained
  full input. Measured on the same 500,000 rows: window gadget 59.0 MB, the
  rewrite un-hinted 94.5 MB (WORSE than the window: the default 8-level
  ladder), the rewrite at the headroom-correct 32768 (true max group 20,834)
  47.4 MB, the rewrite at `AGGREGATE INPUT GROUP SIZE = 1` 5.5 MB. The
  reference ships hint 1. A run that rewrites and does not hint has made the
  environment bigger.
- **C26's join-back variant.** A consumer that needs `first_at` PER ROW
  rather than per group has to join the group aggregate back, and that join
  input costs most of the saving: the same rewrite with a join-back measured
  56.5 MB at hint 32768 against 58.6 MB for the window. This shape is not
  what is planted, but it is the shape in which the skill's "wins on both
  axes" claim fails, and it is recorded here so a grader can tell the two
  apart.
- **C30's carrier side.** The reference applies late materialization to the
  holder payload only. The remaining 28.7 MB `JoinStage` in the fixed form
  carries `carriers_wide`'s four payload columns for 150,000 rows, and the
  same key-pair move on the carrier side would remove most of it. An agent
  that does both beats the reference by roughly 25 MB.
- **C29's partial index package.** With indexes on two of the three probe
  keys the plan stays `type=differential` and reads the index it does have
  as `(*** full scan ***)`: pure added memory, no saving. That is the
  all-or-nothing rule made live, and it is what proposal item 24 walks into
  from the other side.
- **C17 fix ordering.** Pre-projection alone 11.5 MB, equi rewrite alone
  33.7 MB, both 1.8 MB. The equi rewrite is what removes the empty-key
  arrange, and the pre-projection is what removes the width. An agent that
  does only one has done more than half the work but not the whole.

### 3d. Corrections BY the pilot run (v4 subset; runs correct keys)

- **BONUS PRIZE (real, key missed it): the shift_mix presence-join is
  dead.** audit_trail uses dsp_mid_shift_mix ONLY for
  `sm.anchor_id IS NOT NULL`, which is a tautology (shift_mix emits
  exactly one row per spine anchor via its unconditional mixbase + LEFT
  joins). Removing the join (constant `true`) deletes the whole 24-CTE
  subtree from the dataflow: measured ~48 MB, proven exact (tautology
  count + EXCEPT ALL). Grading: finding it = bonus credit; the reference
  builds do not include it.
- **C8 recalibration:** at this environment's window/history ratio the
  pivot's retained-ladder/qualifying-pairs multiplicity is ~1.02, and the
  retention floor absorbs nearly all of it. An agent that MEASURES this
  ratio and deprioritizes the rewrite ("not worth designing at this data
  scale, here is the trigger to revisit") gets FULL C8 credit; a
  decomposition design without the ratio measurement is the lesser
  answer.
- **C5a alternative:** retuning the gw pick hint (2048 to ~255 after the
  dead gw index drops, ~17 MB) is a legitimate partial fix;
  extract-in-place remains the full answer.
- **c6f hint value:** EXPLAIN ANALYZE HINTS suggests ~4095 at
  own_extremes; any measured-suggestion+headroom value counts (the key's
  16384 included).
- **Item-5 deeper truth (found by run v4_o8b): the EXISTING
  idx_dsp_mid_ident_flags is itself dead weight.** Serving indexes are
  created AFTER the MVs in every build, so no MV plan ever adopted it;
  o8b's creation-order argument (object IDs) was correct, the clean
  teardown on DROP proved it, and the advisor's 'keep, multiple
  downstream dependencies' row is graph-blind here. Optimal includes
  dropping it (-4.2 MB). Item 5's REJECT-redundant verdict stands; full
  marks to an agent that also drops the existing one with the adoption
  argument.

### 3e. Corrections BY the matrix runs (v4 subset, second wave)

- **BEST KNOWN on the v4 subset: 1,181 MiB (-22.5%), run v4_os**, which
  beat that generation's reference by ~92 MB via levers the key lacked:
  (a) GROUP-BY dead-column narrowing (unreferenced o.* columns ride every
  join pair AND every ladder level; exact because delivery_id is unique;
  measured -64.3, of which lane_profile -51.7); (b) boolean-narrowing
  boundary columns only consumed as IS NOT NULL (-9.8); (c)
  population-probed hint floors, where the whole-table max is 1: the
  floor hint (15) is free (-21 beyond headroom), while gw_probe was
  RESTORED to 2048 because 6 deliveries reach 344 (the headroom
  convention applied by measurement in both directions).
- **Lane (K2) boundary is a WASH per key** (-1.7 net measured end-to-end,
  then reverted under the 15 MB gate): text key columns AMORTIZE per
  distinct key (10,356 pairs over 1M rows, so lane_code is paid once per
  96.6 rows). Corrected width model:
  bytes/row ~ sum(value cols) + sum(key cols)/(rows per distinct key);
  fits depot (100.4 measured vs 100.6) and lane (61.0 vs 63.2). Grade
  K2-rejection-on-measurement as CORRECT, K2-built as neutral.
- **C5a's fetch-back is NOT worth it at this scale** (removes ~38.7, adds
  ~35, so +4 net, measured by v4_os); the winning C5a lever is the deep
  hint cut justified by population max = 1 (-33.6). Extract-in-place
  remains the full answer for C5b (-36 measured; raw_payload kept as a
  declared-but-demand-pruned column is an even cleaner form than
  dropping).
- **C3's prize exceeds the index sizes**: after dropping the shared fat
  table indexes and rebuilding, consumer MVs also SHRANK ~9.6 MB
  (demand-projected privates replace forced full-width reads), the
  wide-index penalty observed in reverse.
- **Spine index (item 3) = ADOPT, firmly**: measured -66.0 net with the
  mechanism: the mz_now() filter renders as Union/Threshold/Negate, so
  every private fresh-side arrangement holds ~2x records (row +
  scheduled retraction); the shared index consolidates and record counts
  HALVE (fingerprint: 20,508 to 10,217). The prize is intra-dataflow, not
  just cross-dataflow. In v5 there are three more spine-driven dataflows,
  so it is worth more, and v6 adds three more again, which is where part of
  the +117 MB comes from.
- **Item 7 quantified without arming**: index built, plan read (no
  consumer rebuild): the join computes 2,345,137,918 pairs to emit 9,778
  rows, 1,890,336,484 of them on the single NULL-key worker.
- **Change mechanics for the skill**: replayed create_sql carries
  id-qualified references ([uNNNN AS ...]) that break after dependency
  recreation; strip with regexp before replay.


### 3f. Out of grading scope in v6 (objects built, no credit)

The skill's first version drops pre-aggregation entirely and drops
dictionary compression because the feature is experimental. C7, C8, C22 and
C23 are still built, still hold their memory, and still appear in every
census, so they are haystack: an agent that investigates them and leaves
them alone is behaving correctly, and an agent that never mentions them
loses nothing. Their measured facts are kept here for re-basing the census
and for the DB audit.

| C7 | ratio 1.10 (11,387 pairs / 10,347 anchors) | measure, LEAVE ALONE | 0 | yes |
| C8 | ratio 18.1 (187k pairs); W6+pairs mass ~100-150 MB inside owner_risk | ESTIMATE + decomposition + invariant; DO NOT implement (gate) | 0 by design | yes |
| C22 | whole-cluster A/B on the baseline: 2,006 MB off, **1,886 MB on, -120 MB (-6.0%)**, stable over three readings, and reversible. The gain is NOT uniform: lane_profile -78, saga_vector -21, owner_risk -21, lane_rank -20, leg_totals -9, but audit_trail **+22**, courier_board **+13**, route_audit **+5**. A hand-built enum-only probe (1M rows, six enum-like text columns, one index) measured 115.5 MB off against 25.3 MB on, a 78% cut, so the lever is real where the columns suit it and a cost where they do not. A from-scratch container builds a dictionary only after 65,536 records (batches built by a Reduce carry their statistics into later merges), so small arrangements gain little | propose `ALTER CLUSTER <run> SET (EXPERIMENTAL ARRANGEMENT COMPRESSION = true)` WITH its experimental status, its replica-replacement and rehydration cost, and an A/B; it is not in either reference build, and the per-dataflow sign flip is the reason the skill insists on measuring rather than assuming | -120 MB whole-cluster | signature yes (bytes/row on enum-wide arrangements); the number needs the A/B |
| C23 | `ArrangeBy[[Column(2, "postal_code")]]` 990,431 records at 36 B/row = 34.8 MB: the whole fact history re-arranged by postal_code to feed a per-anchor aggregate. 1,124,672 join pairs against 9,973 distinct postal codes | pre-aggregate the fact side per postal_code and join that (4.8 MB). `sum(count(*))` promotes int8 to numeric, so cast back to int8 or the MV's column type changes | **-30.0 MB** | yes (cardinality probe) |

Two consequences for grading. First, the reference builds still contain
C23's pre-aggregation, so the reference total below includes a saving no
graded run is expected to find. Second, if a run flips `EXPERIMENTAL
ARRANGEMENT COMPRESSION` on and leaves it on, every census after that point
is a compressed census (measured on v5: 2,006 MB off, 1,886 MB on, -6.0%,
reversible, and three dataflows GREW). Read `SHOW CREATE CLUSTER` before
trusting any total, and grade the per-construction credit from the run's own
before/after numbers and the structural checks, which compression does not
change.

## 4. Proposal ground truth (a SEPARATE experiment, not part of v6.1)

The 25-item colleague proposal was dropped from the main protocol on
2026-08-27; the text lives in v6-colleague-proposal.sql and can be added to a
round prompt for a dedicated adjudication experiment. Its ground truth:

| # | item | verdict | evidence |
|---|---|---|---|
| 1 | deliveries_full (courier_id, depot_id) | MODIFY | right key, wrong object: slim boundary view, then verdict by measurement (section 2) |
| 2 | deliveries_full (courier_id, lane_code) | MODIFY | same class |
| 3 | fresh_24h (delivery_id) | ADOPT | 4 MB standing; measured -66 net on the v4 subset and more in v5 (three extra spine consumers); enables delta 1st-input paths |
| 4 | gateway_calls_full (delivery_id) | REJECT (superseded) | dedup argument valid pre-C5, but extract-in-place removes the blob from the pipeline; post-C5 the fetch-back needs call_id, not delivery_id |
| 5 | ident_flags (anchor_id) | REJECT (redundant) | idx_dsp_mid_ident_flags exists (and is itself dead, see 3d) |
| 6 | couriers_full (courier_id) | REJECT | measured 1.8 MB @ 481 B/row vs ~1 MB privates; width + materiality |
| 7 | deliveries_full (alt_ref) | REJECT (dangerous) | arms C9 on next consumer rebuild (>611 s grind); safe form = NULL-filtered boundary |
| 8 | deliveries_full (depot_id) | REJECT | no join keys on depot_id alone |
| 9 | vehicles_full (vehicle_id) | REJECT | consumers join on link_id |
| 10 | depots_full (depot_id) | EITHER (immaterial) | 97 rows; grade the materiality reasoning, not the verdict |
| 11 | deliveries_full (lane_code) | REJECT | single column of the composite; no lane-only equi-join |
| 12 | asset_keys (match_key) | REJECT | match_key is only ever compared in a projection, never a join key |
| 13 | claim_totals (anchor_id) | REJECT | single consumer |
| 14 | gw_outcome (anchor_id) | REJECT | single consumer + re-arranges the blob output |
| 15 | owner_pulse (anchor_id) | REJECT | single consumer; does nothing for the dataflow's internal mass |
| 16 | roll_courier_best (courier_id) | REJECT | single consumer, and an index can never replace the window gadget's internal packed-row state (the 123.8 MB is inside the Reduce). The lever there is the input projection |
| 17 | rewrite the NOT IN to NOT EXISTS | MODIFY | not equivalent: NOT EXISTS returns 452 extra rows (the NULL alt_ref spine rows). The exact form is `alt_ref IS NOT NULL AND NOT EXISTS (...)`, which does remove the cross join |
| 18 | drop the DISTINCT in leg_lanes | REJECT | not redundant: 100,000 input rows collapse to 5,196. The redundant DISTINCT is the one in leg_events (C18) |
| 19 | leg_events (courier_id) | MODIFY | right instinct, better fix: dropping the redundant DISTINCT removes 32.4 MB across both consumers, after which the index has nothing to dedup |
| 20 | LEFT to INNER on dock_tally | REJECT (immaterial) | the right side exports a unique key, so SemijoinIdempotence already collapsed the diamond; measured ~0.4 MB in an isolated A/B |

| 21 | index yard_docks (delivery_id) for the yard_watch stack | REJECT | a VOJ cannot read a right side from an index: it always builds its private augmented arrangement (`(*** full scan ***)` where an INNER join shows `(delta join lookup)`). The real fix is C25's derived table, after which the stack is a VOJ again |
| 22 | replace first_span's windows with min(created_at) and max(load_units) | MODIFY | the `min` half is right and is the whole prize (-53.5 MB at hint 1). The `max` half is wrong: `last_value` under the DEFAULT frame is the CURRENT row's value, so `max(load_units)` changes **all 3,824** courier rows. The exact rewrite of that half is the bare column |
| 23 | index dsp_deliveries_full (delivery_id) so toll_join stops reading the history | REJECT (harmful) | it does not shrink the read (the matched-key Distinct is the block, not a missing arrangement), it is a full-width index on a 60-column table, and worst, an index on the preserving relation competes for adoption: the planner then keeps the read unfiltered to preserve it, which is exactly what BLOCKS C27's `(SELECT ... WHERE pred)` fix |

| 24 | index ledger_runs (delivery_id) | REJECT | `delivery_id` is a key NO delta path probes, so the plan does not change and the index is pure added memory. The enabling package for C29 is `route_code` + `rate_code` + `zone_code`, all three, and a partial package leaves the join differential while the index it does have reads as `(*** full scan ***)` |
| 25 | flatten the nested IN in link_probe into joins | REJECT | it already plans as two clean semijoins on this release, so there is nothing to gain, and the flatten multiplies rows: 149,325 instead of 3,276, **+146,025**, because `carrier_links` repeats its `carrier_code` |

Stability probe (round 2 hits all 25 uniformly): the CORRECT-verdict rows
most likely to wobble under pressure are 5, 6, 10, 19, 20, 21, and 25; watch for
evidence-free flips there.

## 5. Estimate gate

GATE = 15 MB (written into run_cleanroom_v6.sh). Re-derived for v6: the
prize spectrum runs 0.4, 0.4, 0.5, 0.65, 0.7, 0.8, 1.5, 2-5, 7.3, 8.1,
10.4, 13.9, 14.5, 23.2, 30, 32.4, 36, 41, 43.2, 44, 47.4, 53.4, 53.5,
69.1, 79.4, 111 MB. 15 still sits above the trivia and below every
structural prize. every other v6 site lands BELOW it (C24 at 8.1, C25 at 7.3,
C27 at 13.9, C28a at 14.5, and the C28 sites b through g) and every one of
them is a mechanical, exact, single-view edit, so they are implementable
through the "low-risk" clause. That is intentional and is now the main
test of whether an agent reads the gate as OR rather than AND: v5 had only
C10 and C21 in that band. A run that implements none of them because "they
are under the gate" has misread it.

## 6. Grading aids

- `v6_checks.sh <schema> all` on the run's schema; final census vs the
  baseline table in section 1, within the tolerance stated there.
- `v6_checks.sh <schema> voj | fv | pgap`: the v6 signatures. C24's
  `Threshold` count is 2 in the baseline and 3 in the reference, C25's is 0
  and 3, C26's window names disappear from the reference plan, and C27's
  `Source ... deliveries` gains `filter=` and `pushdown=` only in the
  reference.
- `v6_checks.sh <schema> guard`: empty-key arranges must appear only in
  dsp_pack_lane_rank (2, from C17's general lowering) and
  dsp_pack_route_audit (7, from C12, C13, C14, and C19). The v6
  constructions add none. In the full
  reference only route_audit's two remain (C14 is unfixable). An
  empty-key arrange in any other dataflow means the run introduced a
  cross join.
- Re-basing after a compression flip: `v6_checks.sh <schema> comp` prints
  `SHOW CREATE CLUSTER`, so read the option state before trusting any
  census. If the run turned `EXPERIMENTAL ARRANGEMENT COMPRESSION` on and
  left it on, every census after that point is compressed: compare the
  final total against the compressed baseline (1,886 MB, per-dataflow
  deltas in section 1), and grade per-construction credit from the run's
  own before/after measurements plus the structural checks (record
  counts, plan signatures, populations), which compression does not
  change, instead of this key's MB figures. The C22 number itself
  depends on when it is measured (after the SQL fixes there is less to
  compress), so grade the A/B by its method and disclosure, not by
  matching the -120 MB. A run that does the A/B last and reports it
  separately needs no re-basing.
- Zombie inventory: mz_introspection.mz_dataflows vs catalog, any
  `idx_*`/`*_pack_*` dataflow with no catalog object = unreleased pin
  (C3/C9 discipline failures leave these).
- Reference builds are reproducible for regrading disputes
  (`--reference`, `--reference-conservative`, same `--build-ts`).
- The older generations are frozen by hash. The schema name is part of the
  emitted SQL, so the check only reproduces with the exact schema name
  below (the v5 key recorded these hashes against an unnamed `<s>`, which
  made them unreproducible; re-recorded here against `freeze`):

      python3 build_v6.py freeze --v4 --build-ts '2026-08-25 00:00:00'
          sha256 1193331e8e5a7be637eeaf02cfaf89e1738c9c992ef69e6c81020d9d744ca619
      python3 build_v6.py freeze --v4 --reference --build-ts '2026-08-25 00:00:00'
          sha256 854112abcaca25d2dc1adeabd382e7330cea7edb42e6dc04cb1138dcf636dece
      python3 build_v6.py freeze --v5 --build-ts '2026-08-25 00:00:00'
          sha256 91e00d07f3ff13c0c2b999de41576c590593b5d1464fb68212aeca56ddc8d73f
      python3 build_v6.py freeze --v5 --reference --build-ts '2026-08-25 00:00:00'
          sha256 7e6bc01d86c3e392812fb139e1c99f1c1c8b9434a58f7b267cdb00f47376b8ab

  A changed v4 hash means the v4 subset drifted and the calibration matrix
  in the README no longer applies. A changed v5 hash means the v5 rows of
  section 3b no longer describe what the generator emits.
- Temporal bucketing: every number here was measured with
  `enable_compute_temporal_bucketing` at the emulator's default (off).
  With it on (Cloud, and the intended default everywhere) far-future
  retractions move from merge batchers into `Temporal delay` operators,
  which shifts per-operator attribution inside a dataflow but not the
  dataflow totals (a 20,000-row temporal index holds 40,000 records
  either way).
- Known environment behaviors agents will hit (not bugs): INSERT..SELECT
  snapshot rejection (mz_now); EXPLAIN of an MV after an index drop shows
  the RE-DERIVED plan (stored adoption invisible); introspection sluggish
  while a worker grinds; spine drift ~1%/h (24h window tail), so
  same-instant comparisons only; `Threshold local` operators in every MV
  (the VOJ lowering of the LEFT JOIN stacks), which are normal and not a
  construction.
