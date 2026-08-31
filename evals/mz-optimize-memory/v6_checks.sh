#!/usr/bin/env bash
# Signature validation for the generated environment; see README.md.
# Usage: v6_checks.sh <schema> [section]
# Sections: mem c1c4 c5 c6 c7c8 c9 c10 advisor guard
#           sub win oj dist indf agg preagg comp
#           voj fv pgap sub6 delta latemat vojgap all (default all)
set -u
S="${1:?schema}"
SEC="${2:-all}"
: "${EVAL_PSQL_ARGS:=-h localhost -p 6875 -U materialize -d materialize}"
PSQL="psql $EVAL_PSQL_ARGS -qAt"

run() { timeout "${T:-120}" $PSQL -c "SET cluster = $S" -c "$1" 2>&1 \
        | grep -v 'NOTICE\|Queried\|^  \|^$\|connected\|Issue\|View doc\|Join our\|Environment\|Region\|User:\|Cluster\|Database\|Schema:\|Session'; }
runq() { timeout "${T:-120}" $PSQL -c "$1" 2>/dev/null; }

sec() { case "$SEC" in all|"$1") return 0;; *) return 1;; esac; }

if sec mem; then
echo "== per-dataflow arrangement memory (MB) =="
T=170 run "
SELECT dod.dataflow_name,
       pg_catalog.round(sum(ase.size) / 1048576.0) AS mb,
       sum(ase.records) AS records
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
GROUP BY 1 ORDER BY 2 DESC"
echo "== top 25 arrangements env-wide =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0) AS mb
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
ORDER BY ase.size DESC NULLS LAST LIMIT 25"
fi

if sec c1c4; then
echo "== C1/C4: per-dataflow join-input arrangements >= 100k records =="
T=170 run "
SELECT dod.dataflow_name, mdo.id, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0) AS mb
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE ase.records >= 100000
ORDER BY dod.dataflow_name, ase.size DESC NULLS LAST"
fi

if sec c5; then
echo "== C5: blob-heavy arrangements (bytes/row > 300) =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0) AS mb,
       pg_catalog.round(ase.size / GREATEST(ase.records, 1)) AS bytes_per_row
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE ase.size / GREATEST(ase.records, 1) > 300 AND ase.records > 1000
ORDER BY ase.size DESC NULLS LAST LIMIT 15"
fi

if sec c6; then
echo "== C6 true group sizes (max rows per group at each hinted site) =="
for spec in \
  "c6a_scans_per_anchor|SELECT max(n) FROM (SELECT delivery_id, count(*) AS n FROM materialize.$S.scans GROUP BY 1)" \
  "c6b_manifests_per_anchor|SELECT max(n) FROM (SELECT delivery_id, count(*) AS n FROM materialize.$S.manifests GROUP BY 1)" \
  "c6c_weight_checks_per_anchor|SELECT max(n) FROM (SELECT delivery_id, count(*) AS n FROM materialize.$S.weight_checks GROUP BY 1)" \
  "c6d_twin_hist_completed_max|SELECT max(n) FROM (SELECT courier_id, count(*) AS n FROM materialize.$S.deliveries WHERE phase = 'completed' AND courier_id >= 38 GROUP BY 1)" \
  "c6e_shift_logs_per_courier|SELECT max(n) FROM (SELECT courier_id, count(*) AS n FROM materialize.$S.shift_logs GROUP BY 1)" \
  "c6f_hist_per_courier_max|SELECT max(n) FROM (SELECT courier_id, count(*) AS n FROM materialize.$S.deliveries GROUP BY 1)" \
  "gw2048_calls_per_delivery|SELECT max(n) FROM (SELECT delivery_id, count(*) AS n FROM materialize.$S.gateway_calls GROUP BY 1)" \
  "ratings256_per_anchor|SELECT max(n) FROM (SELECT delivery_id, count(*) AS n FROM materialize.$S.ratings GROUP BY 1)" \
  "returns256_per_anchor|SELECT max(n) FROM (SELECT delivery_id, count(*) AS n FROM materialize.$S.return_runs GROUP BY 1)" \
  "handoffs64_per_anchor|SELECT max(n) FROM (SELECT delivery_id, count(*) AS n FROM materialize.$S.handoffs GROUP BY 1)" \
  "k1_64_per_courier_depot|SELECT max(n) FROM (SELECT courier_id, depot_id, count(*) AS n FROM materialize.$S.deliveries WHERE courier_id >= 38 GROUP BY 1, 2)" \
  "k2_64_per_courier_lane|SELECT max(n) FROM (SELECT courier_id, lane_code, count(*) AS n FROM materialize.$S.deliveries WHERE courier_id >= 38 GROUP BY 1, 2)" \
  ; do
  name="${spec%%|*}"; sql="${spec#*|}"
  echo "$name: $(runq "$sql")"
done
fi

if sec c7c8; then
echo "== C7 ratio (target ~1.1) and C8 ratio (target ~8-15) =="
A=$(runq "SELECT count(*) FROM materialize.$S.dsp_mid_fresh_24h")
C7=$(runq "SELECT count(*) FROM materialize.$S.dsp_mid_fresh_24h o
JOIN materialize.$S.delay_logs dl ON dl.delivery_id = o.delivery_id
AND dl.noted_at <= o.created_at
AND dl.noted_at > o.created_at - INTERVAL '15 minutes'")
C8=$(runq "SELECT count(*) FROM materialize.$S.dsp_mid_prior_pairs")
echo "anchors=$A c7_pairs=$C7 c8_pairs=$C8"
if [[ "$A" =~ ^[0-9]+$ && "$C7" =~ ^[0-9]+$ && "$C8" =~ ^[0-9]+$ && "$A" -gt 0 ]]; then
  python3 -c "a=$A; print('c7_ratio=%.2f c8_ratio=%.2f' % ($C7/a, $C8/a))"
else
  echo "c7c8 ratios UNAVAILABLE (a query timed out or the spine is empty): anchors='$A' c7='$C7' c8='$C8'"
fi
fi

if sec c9; then
echo "== C9 baseline: alt_ref NULL populations + plan guard placement =="
runq "SELECT count(*) FILTER (WHERE alt_ref IS NULL),
             count(*) FROM materialize.$S.deliveries"
runq "SELECT count(*) FILTER (WHERE alt_ref IS NULL),
             count(*) FROM materialize.$S.dsp_mid_fresh_24h"
echo "-- owner_risk plan filter lines mentioning alt_ref/IS NOT NULL:"
timeout 170 $PSQL -c "EXPLAIN PHYSICAL PLAN AS VERBOSE TEXT FOR
MATERIALIZED VIEW materialize.$S.dsp_pack_owner_risk" 2>/dev/null \
  | grep -n "isnull\|IS NOT NULL" | head -10
fi

if sec c10; then
echo "== C10 totality: feature-view row counts vs spine =="
A=$(runq "SELECT count(*) FROM materialize.$S.dsp_mid_fresh_24h")
LF=$(runq "SELECT count(*) FROM materialize.$S.dsp_roll_lane_first")
DB=$(runq "SELECT count(*) FROM materialize.$S.dsp_mid_delay_bands")
echo "spine=$A lane_first=$LF delay_bands=$DB (all three must be equal)"
fi

if sec advisor; then
echo "== mz_index_advice rows for $S objects =="
runq "SELECT a.object_id, o.name, a.hint, a.details
FROM mz_internal.mz_index_advice a
JOIN mz_objects o ON o.id = a.object_id
JOIN mz_schemas s ON o.schema_id = s.id
WHERE s.name = '$S'
ORDER BY o.name" | head -40
fi

if sec guard; then
echo "== empty-key-arrange guard =="
echo "-- expected: only dsp_pack_route_audit (C12/C13/C14 CrossJoins, C19)"
echo "-- and dsp_pack_lane_rank (C17's general lowering). Anything else is"
echo "-- an accidental cross join."
T=170 run "
SELECT dod.dataflow_name, count(*) AS empty_key_arranges
FROM mz_introspection.mz_lir_mapping lm
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = lm.operator_id_start
WHERE lm.operator LIKE '%empty key%'
GROUP BY 1 ORDER BY 1"
fi

# ---------------- v5 sections ----------------

if sec sub; then
echo "== C11 payload-keyed correlation: Distinct/ArrangeBy on doc_body =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN WITH (arity) AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_doc_codes" 2>/dev/null \
  | grep -c "keys=\[\[#[0-9]*{doc_body}\]\]\|Distinct project=\[#[0-9]*{doc_body}\]"
echo "-- (baseline: > 0 lines key on doc_body; reference: 0)"
echo "== C12/C13/C14 signatures in dsp_mid_ref_screen =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN WITH (arity) AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_ref_screen" 2>/dev/null \
  | grep -c "CrossJoin"
echo "-- CrossJoin count (baseline 3: NOT IN, SELECT-list IN, band inequality;"
echo "--  reference 1: only the unfixable inequality correlation)"
echo "== C11 herring: ref_known is a semijoin (no any(), no CrossJoin) =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT doc_id, ref_known FROM materialize.$S.dsp_mid_doc_codes" 2>/dev/null \
  | grep -c "CrossJoin\|any("
echo "-- (must be 0: both compared columns are NOT NULL)"
echo "== C12 populations (NULL outer rows the NOT EXISTS trap would add) =="
runq "SELECT count(*) FILTER (WHERE alt_ref IS NULL) AS spine_null_alt,
             count(*) AS spine_rows
      FROM materialize.$S.dsp_mid_fresh_24h"
runq "SELECT count(*) AS screened FROM materialize.$S.dsp_mid_ref_screen"
fi

if sec win; then
echo "== C15/C16 window gadgets: packed-row state and bytes/row =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb,
       pg_catalog.round(ase.size / GREATEST(ase.records, 1)) AS bytes_per_row
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE mdo.name LIKE '%UnnestList%'
ORDER BY ase.size DESC NULLS LAST"
echo "-- baseline packs the full 16-col wrapper (~185 B/row); the fix"
echo "-- projects first (~66 B/row for C15, ~30 B/row for C16)"
echo "== C15/C16 window partition populations =="
runq "SELECT max(n) AS max_completed_per_courier
      FROM (SELECT courier_id, count(*) AS n
            FROM materialize.$S.deliveries WHERE phase = 'completed'
            GROUP BY 1) z"
runq "SELECT max(n) AS max_failed_per_courier
      FROM (SELECT courier_id, count(*) AS n
            FROM materialize.$S.deliveries WHERE phase = 'failed'
            GROUP BY 1) z"
fi

if sec oj; then
echo "== C17 general lowering: full-width Distincts over the preserving side =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN WITH (arity) AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_hold_rates" 2>/dev/null \
  | grep -cE 'Distinct project=\[#0[^]]*\.\.=#1[0-9]'
echo "-- (baseline: 2 all-column Distincts; reference: 0)"
echo "== C17 preserving-side population =="
runq "SELECT count(*) AS on_hold_rows FROM materialize.$S.deliveries
      WHERE phase = 'on_hold'"
runq "SELECT count(*) AS unbanded FROM materialize.$S.dsp_mid_hold_rates
      WHERE band_label IS NULL"
echo "-- unbanded must be 0: the grid covers the whole load_units range,"
echo "-- which is what makes the equi rewrite exact"
echo "== known-key herring: dock_tally exports a unique key =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN WITH (keys) AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_dock_tally" 2>/dev/null \
  | grep -c 'Return.*keys: "(\[0\])"'
echo "-- (must be 1: the LEFT JOIN to it is already collapsed)"
fi

if sec dist; then
echo "== C18 DISTINCT redundancy: rows vs distinct delivery_id =="
runq "SELECT count(*) AS rows, count(DISTINCT delivery_id) AS distinct_ids
      FROM materialize.$S.dsp_mid_leg_events"
echo "-- equal => the DISTINCT is redundant and droppable"
echo "== C18 twin: leg_lanes' DISTINCT is NOT redundant =="
runq "SELECT (SELECT count(*) FROM materialize.$S.dsp_mid_leg_events) AS in_rows,
             (SELECT count(*) FROM materialize.$S.dsp_mid_leg_lanes) AS out_rows"
echo "-- out_rows << in_rows => dropping that DISTINCT changes results"
echo "== C18 per-consumer Distinct arrangements =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE mdo.name LIKE '%DistinctBy%' AND ase.records > 50000
ORDER BY ase.size DESC NULLS LAST"
fi

if sec indf; then
echo "== C19 null-safe join: CrossJoin over empty-key arranges =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_seal_match" 2>/dev/null \
  | grep -c "CrossJoin\|ArrangeBy keys=\[\[\]\]"
echo "-- (baseline: 3 = one CrossJoin + two empty-key arranges; reference: 0)"
echo "== C19 pair mass and the NULL-NULL block =="
runq "SELECT (SELECT count(*) FROM materialize.$S.seal_scans) AS scans,
             (SELECT count(*) FROM materialize.$S.seal_registry) AS registry,
             (SELECT count(*) FROM materialize.$S.seal_scans
               WHERE seal_code IS NULL) AS scan_nulls,
             (SELECT count(*) FROM materialize.$S.seal_registry
               WHERE seal_code IS NULL) AS reg_nulls"
echo "== C19 worker skew on the null-safe join (max cpu_ratio ~= workers) =="
timeout 170 $PSQL -c "SET cluster = $S" -c "
EXPLAIN ANALYZE CPU WITH SKEW FOR MATERIALIZED VIEW
materialize.$S.dsp_pack_route_audit" 2>/dev/null \
  | grep -i "differential join" | head -6
fi

if sec agg; then
echo "== C20 basic aggregate retains its full input (bytes/row ~ payload) =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb,
       pg_catalog.round(ase.size / GREATEST(ase.records, 1)) AS bytes_per_row
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE mdo.name LIKE '%Inaccumulable%'
ORDER BY ase.size DESC NULLS LAST"
echo "== C20 aggregated population =="
runq "SELECT count(*) AS digest_rows, sum(n_call_payloads) AS payloads
      FROM materialize.$S.dsp_mid_call_digest"
echo "== C21 argmax redundancy: pick value equals the sibling max =="
runq "SELECT count(*) FILTER (WHERE shift_pick_units IS DISTINCT FROM peak_units)
             AS mismatches,
             count(*) AS rows
      FROM materialize.$S.dsp_mid_shift_peak"
echo "-- mismatches must be 0: the pick's first row already carries the max"
fi

if sec preagg; then
echo "== C23 distributive site: pairs vs pre-aggregated groups =="
runq "SELECT (SELECT count(*) FROM materialize.$S.dsp_mid_fresh_24h o
               JOIN materialize.$S.dsp_deliveries_full h
                 ON h.postal_code = o.postal_code) AS join_pairs,
             (SELECT count(DISTINCT postal_code)
                FROM materialize.$S.dsp_deliveries_full) AS postal_groups"
echo "-- pairs >> groups => pre-aggregating the fact side removes the"
echo "-- million-row join-input arrangement"
fi

if sec comp; then
echo "== C22 dictionary-compression candidates: big enum-heavy arrangements =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb,
       pg_catalog.round(ase.size / GREATEST(ase.records, 1)) AS bytes_per_row
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE ase.records > 65536
ORDER BY ase.size DESC NULLS LAST LIMIT 15"
echo "-- arrangements above the 65k dictionary threshold; the ones whose"
echo "-- width is enum-like text are what the cluster option compresses"
echo "== cluster option state (is the census compressed?) =="
runq "SHOW CREATE CLUSTER $S"
echo "-- EXPERIMENTAL ARRANGEMENT COMPRESSION = true means every census"
echo "-- taken since the flip is a compressed one: grade totals against"
echo "-- the compressed baseline in the key (section 1) and per-construction"
echo "-- credit from the run's own before/after numbers (key section 6)"
fi

# ---------------- v6 sections ----------------

if sec voj; then
echo "== C24 USING cut: Threshold count (baseline 2, reference 3) =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_roll_yard_chain" 2>/dev/null \
  | grep -c "Threshold"
echo "== C25 local-ON cut: Threshold count (baseline 0, reference 3) =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_roll_yard_watch" 2>/dev/null \
  | grep -c "Threshold"
echo "== C24/C25 exactness seeds: NULL and duplicate right keys =="
runq "SELECT (SELECT count(*) FROM materialize.$S.yard_moves
               WHERE delivery_id IS NULL) AS moves_null_keys,
             (SELECT count(*) FROM materialize.$S.yard_docks
               WHERE delivery_id IS NULL) AS docks_null_keys,
             (SELECT count(*) FROM materialize.$S.yard_seals
               WHERE delivery_id IS NULL) AS seals_null_keys"
runq "SELECT count(*) AS dup_keyed_rows FROM (
        SELECT delivery_id FROM materialize.$S.yard_docks
        WHERE delivery_id IS NOT NULL
        GROUP BY 1 HAVING count(*) > 1) z"
echo "-- both must be non-zero: they are what makes USING-to-ON and the"
echo "-- derived-table move provably exact rather than plausibly exact"
echo "== C24/C25 driver population and match rate =="
runq "SELECT (SELECT count(*) FROM materialize.$S.deliveries
               WHERE source_app = 'app_kiosk_terminal_v2') AS driver_rows,
             (SELECT count(*) FROM materialize.$S.yard_moves) AS moves_rows"
echo "-- a near-100% match rate is what makes the VOJ form the cheaper one"
echo "-- (outer-joins.md, 'When the VOJ lowering is the cheaper one')"
fi

if sec fv; then
echo "== C26 window gadget: fused first_value/last_value =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_roll_first_span" 2>/dev/null \
  | grep -cE "fused_value_window_func|first_value\[|last_value\["
echo "-- (baseline: > 0, one fused gadget; reference: 0)"
echo "== C26 packed-row state =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb,
       pg_catalog.round(ase.size / GREATEST(ase.records, 1)) AS bytes_per_row
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE mdo.name LIKE '%UnnestList%' OR mdo.name LIKE '%MinsMaxes%'
ORDER BY ase.size DESC NULLS LAST LIMIT 12"
echo "== C26 exactness facts: no NULL ordering column, unique order key =="
runq "SELECT count(*) FILTER (WHERE created_at IS NULL) AS null_order_col,
             count(*) AS rows
      FROM materialize.$S.deliveries WHERE load_units >= 100.0"
echo "-- null_order_col must be 0: that is what makes first_value = min()"
echo "== C26 trap: max(load_units) is NOT the last_value =="
runq "SELECT count(*) AS couriers,
             count(*) FILTER (WHERE last_sum IS DISTINCT FROM max_sum)
                 AS rows_the_max_rewrite_changes
      FROM (SELECT courier_id,
                   sum(load_units) AS last_sum,
                   count(*) * max(load_units) AS max_sum
            FROM materialize.$S.deliveries WHERE load_units >= 100.0
            GROUP BY 1) z"
echo "== C26 true max group size (for the rewrite's hint) =="
runq "SELECT max(n) FROM (SELECT courier_id, count(*) AS n
      FROM materialize.$S.deliveries WHERE load_units >= 100.0 GROUP BY 1) z"
fi

if sec pgap; then
echo "== C27 pushdown gap: filter=/pushdown= on the preserving Source =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_roll_toll_promo" 2>/dev/null \
  | grep -A 2 "Source materialize.$S.deliveries" | head -6
echo "-- baseline: the deliveries Source carries NO filter= line, so the"
echo "-- preserving side is read whole; reference: filter= and pushdown="
echo "-- on promo_code appear"
echo "== C27 populations: whole history vs the filtered slice =="
runq "SELECT count(*) AS history_rows,
             count(*) FILTER (WHERE promo_code IS NOT NULL) AS filtered_rows
      FROM materialize.$S.deliveries"
echo "== C27 right side: unique in the DATA, no DECLARED key =="
runq "SELECT count(*) AS toll_rows,
             count(DISTINCT delivery_id) AS toll_keys
      FROM materialize.$S.toll_grades"
echo "-- toll_rows = toll_keys, so the right side IS unique, but a table"
echo "-- declares no keys, so the matched-key Distinct stands and blocks"
echo "-- the predicate. Both documented workarounds are therefore live:"
echo "-- wrap the preserving side, or route the right side through a"
echo "-- GROUP BY / DISTINCT ON view that declares the key"
fi

if sec sub6; then
echo "== C28a rewrite 3: an all-column Distinct over the 16-column spine =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN WITH (arity) AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_band_probe" 2>/dev/null \
  | grep -cE 'Distinct project=\[#0[^]]*\.\.=#1[0-9]'
echo "-- (baseline: 2, the general lowering pair; reference: 0)"
echo "== C28b rewrite 4: the outer keys seed the aggregate =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_shift_probe" 2>/dev/null \
  | grep -c "Distinct project=\[#0{courier_id}\]"
echo "-- (baseline: 1, the Distinct over the OUTER key that seeds the"
echo "--  Reduce; reference: 0, the CTE aggregates once over shift_logs)"
echo "== C28c rewrite 5 herring: already two clean semijoins =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_link_probe" 2>/dev/null \
  | grep -c "CrossJoin"
echo "-- (must be 0 in both builds: no rewrite is needed)"
echo "== C28c trap: carrier_links repeats its key =="
runq "SELECT count(*) AS rows, count(DISTINCT carrier_code) AS keys
      FROM materialize.$S.carrier_links"
echo "-- rows > keys => flattening the EXISTS into a JOIN multiplies rows"
echo "== C28d rewrite 6: the arrangement key carries the list =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_tag_probe" 2>/dev/null \
  | grep -c "tag_list"
echo "-- (> 0 in both builds: the list form is the one that measured"
echo "--  smaller here, so the correct action is to measure and leave it)"
echo "== C28e rewrite 8: the empty groups the COALESCE has to cover =="
runq "SELECT (SELECT count(DISTINCT courier_id) FROM materialize.$S.curfew_windows)
             AS covered_couriers,
             (SELECT count(DISTINCT courier_id) FROM materialize.$S.dsp_mid_fresh_24h)
             AS spine_couriers"
echo "-- covered < spine => a LEFT JOIN without COALESCE yields NULL where"
echo "-- the scalar subquery yields 0"
echo "== C28f rewrite 9: the subquery built once or twice =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_union_probe" 2>/dev/null \
  | grep -c "aggregates=\[count(\*)\]"
echo "-- (baseline: 2, one per UNION branch; reference: 1, hoisted to a CTE)"
echo "== C28g rewrite 10: the series and its fractional herring =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_series_probe" 2>/dev/null \
  | grep -c "generate_series"
echo "-- (baseline: > 0; reference: 0, BETWEEN on an integer column)"
runq "SELECT (SELECT count(*) FROM materialize.$S.dsp_mid_float_probe) AS in_series,
             (SELECT count(*) FROM materialize.$S.dsp_mid_fresh_24h
               WHERE load_units BETWEEN 1 AND 60) AS in_range"
echo "-- in_range >> in_series => BETWEEN is NOT the fix on a float column"
fi

if sec delta; then
echo "== C29 join implementation and the eliminable intermediates =="
timeout 170 $PSQL -c "SET cluster = $S" -c "
EXPLAIN OPTIMIZED PLAN WITH (join implementations) AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_mid_ledger_legs" 2>/dev/null \
  | grep -E "type=(delta|differential)|delta join|full scan" | head -8
echo "-- baseline: type=differential and no index reads; reference:"
echo "-- type=delta with (delta join lookup) on two probe keys and"
echo "-- (delta join 1st input (full scan)) on the third"
echo "== C29 JoinStage intermediates (the memory the flip removes) =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE mdo.name LIKE 'JoinStage%'
ORDER BY ase.size DESC NULLS LAST LIMIT 10"
echo "== C29 expansion: driver rows vs join output rows =="
runq "SELECT (SELECT count(*) FROM materialize.$S.ledger_runs) AS driver_rows,
             (SELECT sum(ledger_n) FROM materialize.$S.dsp_mid_ledger_legs)
                 AS join_rows"
fi

if sec latemat; then
echo "== C30 late materialization: the wide payload on the intermediate =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb,
       pg_catalog.round(ase.size / GREATEST(ase.records, 1)) AS bytes_per_row
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE dod.dataflow_name LIKE '%ledger_board%'
  AND mdo.name LIKE 'JoinStage%'
ORDER BY ase.size DESC NULLS LAST LIMIT 8"
echo "-- baseline: one JoinStage at parcel scale and holder width;"
echo "-- reference: the same stage carries the key pair only"
echo "== C30 widths: what the payload costs per row =="
runq "SELECT (SELECT count(*) FROM materialize.$S.holders) AS holder_rows,
             (SELECT count(*) FROM materialize.$S.parcel_units) AS parcel_rows,
             (SELECT count(*) FROM materialize.$S.carriers_wide) AS carrier_rows"
fi

if sec vojgap; then
echo "== C31 VOJ pushdown gap: Threshold count and the driver Source =="
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_roll_relay_hot" 2>/dev/null \
  | grep -c "Threshold"
echo "-- (3 in BOTH builds: the stack is clean either way, the gap is the"
echo "--  augment-key read, not the lowering)"
timeout 170 $PSQL -c "EXPLAIN OPTIMIZED PLAN AS VERBOSE TEXT FOR
SELECT * FROM materialize.$S.dsp_roll_relay_hot" 2>/dev/null \
  | grep -A 2 "Source materialize.$S.deliveries" | head -4
echo "-- baseline: no filter= line; reference: filter= and pushdown= on"
echo "-- risk_score"
echo "== C31 Threshold-feeding record counts (the evidence for the push) =="
T=170 run "
SELECT dod.dataflow_name, mdo.name, ase.records,
       pg_catalog.round(ase.size / 1048576.0, 1) AS mb
FROM mz_introspection.mz_arrangement_sizes ase
JOIN mz_introspection.mz_dataflow_operator_dataflows dod
    ON dod.id = ase.operator_id
JOIN mz_introspection.mz_dataflow_operators mdo ON mdo.id = ase.operator_id
WHERE dod.dataflow_name LIKE '%ledger_board%'
  AND ase.records > 200000
ORDER BY ase.size DESC NULLS LAST LIMIT 10"
echo "== C31 crossover check: right-side keys vs the filtered driver =="
runq "SELECT (SELECT count(DISTINCT delivery_id) FROM materialize.$S.relay_a)
                 AS relay_a_keys,
             (SELECT count(*) FROM materialize.$S.deliveries
               WHERE risk_score < 0.01) AS filtered_driver_rows,
             (SELECT count(*) FROM materialize.$S.deliveries) AS history_rows"
echo "-- right-side keys << filtered driver rows => pushing the predicate"
echo "-- into the driver is the cheaper side of the crossover"
fi
