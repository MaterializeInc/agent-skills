#!/usr/bin/env python3
"""Build the v6 eval environment (see README.md).

Usage: build_v6.py <schema/cluster name> [--seed N] [--manifest] [--stats]
                   [--v4] [--v5]

Generates a feature-extraction pipeline (43 tables, ~57 views, 11 MVs) from
anonymized structural templates, with the constructions planted per the
manifest (--manifest). All vocabulary is invented (delivery dispatch domain).
Construction key (answer key derives from these tags):

v6 is a superset of v5, which is a superset of v4. Each generation is appended
after the previous one, so `--v4` emits the v4 subset and `--v5` the v5
environment byte-identically. The README's calibration numbers were measured on
the v4 subset. C7, C8, C22 and C23 are still built but are OUT OF GRADING SCOPE
in v6 (pre-aggregation and compression are outside the skill's first version).

  C1  composite re-keys of the fact history across 5-6 MV dataflows, two keys:
      K1=(courier_id, depot_id): W1 dsp_roll_depot_history [P2], W2
      dsp_roll_depot_recency [P2], W3 dsp_roll_depot_moment [P3], W7
      dsp_roll_owner_top3 [P8]; K2=(courier_id, lane_code): W4
      dsp_roll_lane_history [P4], W5 dsp_roll_lane_first [P4], shift_mix
      lane CTE [P8]. Correct: two narrow boundary views + composite indexes,
      repoint; P2/P4 also hold INTRA duplicates.
  C2  fat wrapper trap: dsp_couriers_full carries 3 fat text cols; 5 consumers
      join on courier_id but use 3 narrow cols. Advisor + colleague say index
      it; correct = slim boundary view + index (width math rejects the fat one).
  C3  dead wide TABLE indexes, advisor-silent, correct = verified drop:
      C3a idx_gateway_calls_kind ON gateway_calls(call_kind), full blob rows
      ride it, ~60MB, no dataflow uses it; C3b idx_couriers_home ON
      couriers(home_depot_id), tiny (2k rows), adjudication filler.
  C4  intra-dataflow CSE miss in the mega-view: hist_eff / hist_cat CTEs make
      the same expansion join with divergent projections -> double arrangement;
      correct = merge to one shared CTE (or hoist as indexed view).
  C5a dsp_mid_gw_outcome: 22 ->> extractions AND raw blob passthrough; blob
      rides the pick ladder; MV P1 consumes raw_payload -> slim the pick to
      keys, single fetch-back join for the blob at the end.
  C5b dsp_mid_gw_probe: 13 mixed ->/->> extractions + passthrough NOT consumed
      by MV P8 -> provably droppable; extract-in-place.
  C6  hint field: c6a scan_trail pick 65536 (true ~40, scans); c6b
      claim_totals first tally 4096 (true ~12, manifests); c6c dispute_marks
      first tally 65536 (true ~30, weight_checks); c6d mega twin reduces
      sl_twin_a 65536 (true ~120, flag) vs sl_twin_b 256 (true ~26, ok),
      byte-similar bodies, landmark method needed; c6e shift_mix sx_1 agg 256
      (true ~5.6k shift_logs, undersized); c6f W8 own_extremes UNHINTED
      min/max ladder over a 30-day slice of the history (add 16384/65536: the
      un-hinted default plans for 4e9 rows, i.e. 7 bucket stages).
      The K2 sites carry 128 (true ~67) and the K1 sites 64 (true ~12). Convention: hints within
      16x of true max = correct-by-headroom; C6 sites are all >=64x or
      undersized. Real-source 65536-dominant histogram is NOT reproduced
      (dishonest at this scale).
  C7  dsp_mid_route_flux: 15-min window rescan, pairs/anchors ~1.1 ->
      measure, leave alone.
  C8  dsp_roll_owner_pulse [P5]: 21-FILTER pivot over dsp_mid_prior_pairs,
      ratio ~8-10, the biggest mass -> ESTIMATE ONLY (sizing gate).
  C9  deliveries.alt_ref ~4.3% NULL (NULL_MOD=23); dsp_mid_alt_share joins
      spine->history on
      alt_ref (private plans push IS NOT NULL below the arrangement). A shared
      index ON (alt_ref) (colleague item) arms the NULL^2 produce-discard
      grind (~1-2 min one-worker hydration; pairs ~ anchors * N_DELIV /
      NULL_MOD^2 at ~180k closure pairs/s measured) on rebuild of the
      consumer MV. Signature:
      flat memory, one-worker elapsed skew, unresponsive replica
      introspection. RECOVERY ORDER: drop the consumer MV FIRST (kills the
      grinding dataflow; a dropped index stays pinned by it otherwise), then
      drop the index, then rebuild. Correct fix: closure audit before deploy;
      NULL-filtered boundary view + index.
  C10 provable LEFT->INNER: W5 dsp_roll_lane_first and dsp_mid_delay_bands are
      grouped over spine LEFT JOIN detail (total per anchor); their MV LEFT
      JOINs are convertible.
  R*  red herrings: mega expansion is correctly shared (R1); 68% of views
      single-consumer; W8/W6 65536 hints correct for the 41k-row hot courier;
      identity view already indexed; advisor 'drop'/'convert' rows on serving
      indexes.

  --- v5 additions ---
  C11 subquery correlated on a payload column: dsp_mid_doc_codes runs a scalar
      subquery whose only outer reference is manifest_docs.doc_body (~1.5 kB
      text), so the decorrelation keys its Distinct and both join-back
      arrangements by the document body. Correct: narrow the correlated column
      first (a CTE that extracts the header code), or precompute the count per
      code and LEFT JOIN it.
  C12 NOT IN on a nullable side: dsp_mid_ref_screen filters the spine with
      `alt_ref NOT IN (SELECT carrier_code ...)`. Plans as the CrossJoin +
      three-valued Union/Negate/Distinct shape. The tempting NOT EXISTS
      rewrite ADDS the NULL-alt_ref rows the original drops; the exact form is
      `alt_ref IS NOT NULL AND NOT EXISTS (...)`.
  C13 IN in a SELECT list on a nullable column: the same view's ref_listed
      column. Plans as Reduce aggregates=[any(...)] over a CrossJoin with
      Map(false)/Map(null) diamonds. COALESCE(..., false) is the tempting
      WRONG rewrite (turns NULL into false on the NULL-alt_ref rows); the
      exact form keeps the three-valued result with a CASE.
  C14 inequality-only correlation: the same view's bands_below column. No
      equi-join exists, the CrossJoin is the plan, and no rewrite fixes it.
      Correct: measure, report, leave alone (restraint probe).
  C15 window function over a wide input scope: dsp_roll_courier_best runs
      row_number() over the 16-column fact wrapper and keeps rn = 1, so the
      gadget packs all 16 columns. Correct: narrow the window's input
      relation. The mechanical DISTINCT ON rewrite measures WORSE here
      (hierarchical TopK levels beat the packed list only when the partition
      population is small; this one has a 33k-row whale).
  C16 LAG over irregular spacing on a wide input: dsp_roll_courier_gap. The
      rewrite to a self equi-join is NOT available (irregular spacing), so the
      window stays and only the input slimming applies.
  C17 general outer-join lowering: dsp_mid_hold_rates LEFT JOINs a rate-band
      table on a cross-side inequality, which forces the general shape (two
      full-width Distincts of the preserving side plus an all-column
      self-join). Correct: pre-project the preserving side, and rewrite the ON
      to the equivalent equi-join on the band grid.
  C18 DISTINCT-blocked projection pushdown: dsp_mid_leg_events is a
      `SELECT DISTINCT *` over a per-delivery slice, consumed by two
      dataflows that read three columns each. The DISTINCT is redundant
      (delivery_id is unique in the slice; count vs count-distinct proves it).
      Twin herring: dsp_mid_leg_lanes' DISTINCT is NOT redundant and dropping
      it changes results.
  C19 IS NOT DISTINCT FROM in a join: dsp_mid_seal_match joins two ~3k-row
      relations null-safely, which plans as a CrossJoin over two empty-key
      arranges and grinds one worker. Memory is negligible; the signature is
      CPU skew. Correct: a sentinel COALESCE equi-join (exact). Plain `=` is
      the trap (drops the NULL-NULL matches).
  C20 basic aggregate keeping its full input: dsp_mid_call_digest jsonb_aggs
      the gateway payloads and reads two scalars out of the array, so the
      Reduce retains every payload. Correct: narrow the aggregate's argument
      to the consumed field.
  C21 argmax redundancy: dsp_mid_shift_peak carries a DISTINCT ON pick
      ordered by mark_units DESC and a sibling un-hinted max(mark_units) over
      the same relation and key. Correct: delete the max, read the value from
      the pick.
  C22 dictionary compression: the environment's biggest arrangements are
      dominated by enum-like text columns. The cluster option EXPERIMENTAL
      ARRANGEMENT COMPRESSION is the lever; it is not part of any reference
      build (it is a replica property, measured by A/B).
  C23 distributive pre-aggregation below a join: dsp_roll_postal_load
      aggregates the join product of the spine and the whole fact history on
      postal_code. Correct: pre-aggregate the fact side to postal_code
      granularity and join that, casting the promoted sum(count) back to
      int8.

  --- v6 additions (C7, C8, C22 and C23 are still built but are OUT OF
      GRADING SCOPE: pre-aggregation and compression are outside the
      skill's first version) ---
  C24 VOJ stack cut by USING: dsp_roll_yard_chain LEFT JOINs three yard
      tables with USING (delivery_id) off a driver whose leftmost column is
      courier_id, so the first join plans a Project the VOJ collector will
      not walk through and only 2 of 3 Thresholds survive. Fix: ON l.k = r.k
      throughout (3 Thresholds). Exactness seeds: NULL and duplicate right
      keys.
  C25 VOJ stack cut by a local ON predicate: dsp_roll_yard_watch's SECOND
      join carries AND k.dock_code = 'dk2' in its ON, which makes the whole
      lowering attempt bail (0 Thresholds). Fix: the predicate into a
      derived table on the right side (3 Thresholds).
  C26 FIRST_VALUE over its own ordering column: dsp_roll_first_span runs
      first_value(created_at) ORDER BY created_at (= min, created_at is
      never NULL) fused with last_value(load_units) under the DEFAULT frame
      (= the CURRENT row's value, NOT the partition maximum). Fix: min()
      GROUP BY plus the bare column, hinted. TRAP: rewriting last_value to
      max(load_units) changes every courier row.
  C27 the equi pushdown gap: dsp_mid_toll_join LEFT JOINs an unkeyed
      toll_grades to the whole fact history, and dsp_roll_toll_promo's
      selective WHERE sits above it, so the preserving read stays
      unfiltered and Source deliveries carries no filter= line. Fix: wrap
      the preserving side in (SELECT ... WHERE promo_code IS NOT NULL);
      nothing indexes the preserving relation, so no adoption competes.
  C28 the remaining subquery rewrites of references/subqueries.md, one
      small site each: a=rewrite 3 (dsp_mid_band_probe, a subquery in a
      LEFT JOIN's ON, the general-lowering trigger), b=rewrite 4
      (dsp_mid_shift_probe, IN over an aggregating subquery in a top-level
      WHERE), c=rewrite 5 (dsp_mid_link_probe, nested IN, already handled
      on this release: a MEASURED HERRING whose trap is flattening the
      EXISTS into a JOIN over the duplicated carrier_links),
      d=rewrite 6 (dsp_mid_tag_probe, = ANY(<list column>), whose unnest
      rewrite measured BIGGER here: a second measured herring, trap =
      dropping the DISTINCT), e=rewrite 8 (dsp_mid_curfew_probe, a
      correlated aggregate with the empty-group COALESCE obligation),
      f=rewrite 9 (dsp_mid_union_probe, the same subquery text in two
      UNION branches), g=rewrite 10 (dsp_mid_series_probe, IN (SELECT
      generate_series(a, b)) on an INTEGER column, with dsp_mid_float_probe
      beside it as the fractional-column herring).
  C29 flipping a differential join to delta: dsp_mid_ledger_legs joins a
      100k-row driver to three dimensions on THREE different driver
      columns, so the differential cascade keeps two JoinStage
      intermediates. Fix = index the driver by each probe key (all three,
      the flip is all-or-nothing), verify type=delta and (delta join
      lookup). Trap: an index on a key no path probes.
  C30 late materialization: dsp_mid_parcel_profile joins a 150k-row fact
      to a WIDE holder dimension and then to a carrier dimension keyed off
      the holder, so the holder payload rides the second join's
      intermediate. Fix = a narrow (holder_id, carrier_ref) key-pair view,
      the chain routed through it, the wide relation joined once by
      primary key at the end.
  C31 the VOJ pushdown gap: dsp_mid_relay_stack is a clean three-deep VOJ
      off the deliveries TABLE and dsp_roll_relay_hot's 1%-selective
      predicate sits above it, so the augment-key read runs at
      whole-history scale and Source deliveries carries no filter= line.
      Fix = the predicate into the driver below the stack; the right sides
      hold 1,000 keys each, far fewer than the filtered driver asks about,
      which is the side of the crossover where pushing down wins.
"""

import argparse
import os
import random
import sys
from datetime import datetime, timezone

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("schema")
ap.add_argument("--seed", type=int, default=4001)
ap.add_argument("--manifest", action="store_true")
ap.add_argument("--stats", action="store_true")
ap.add_argument("--scale", type=int, default=1,
                help="divide all row counts by this (syntax-check runs)")
ap.add_argument("--reference-conservative", action="store_true",
                help="reference WITHOUT the C1/C9 boundary views+indexes: "
                     "what width-math-only discipline ships. MEASURED: 156 "
                     "MB saved vs the full reference's 247 MB, the "
                     "boundaries are net +91 MB DESPITE the static width "
                     "math (shared arrangements restructure the multi-way "
                     "join plans; intermediate JoinStages vanish). Kept "
                     "reproducible as C1 adjudication ground truth.")
ap.add_argument("--reference", action="store_true",
                help="emit the REFERENCE (fixed) environment: C1/C9 boundary "
                     "views + composite indexes + spine index, C3 dead "
                     "indexes omitted, C4 twin scans merged, c6d twins "
                     "merged, C5a slim pick + fetch-back, C5b extract-in-"
                     "place + passthrough dropped, C6 hints retuned, C10 "
                     "LEFT->INNER. C7/C8/R* untouched by design.")
ap.add_argument("--build-ts", default=None,
                help="override the data timestamp anchor (UTC, "
                     "'YYYY-MM-DD HH:MM:SS'); pass the baseline env's value "
                     "so reference and baseline hold identical data")
ap.add_argument("--v4", action="store_true",
                help="emit only the v4 subset (C1-C10 + R*), the environment "
                     "the README's calibration matrix was measured on; the "
                     "answer key records sha256 hashes of this output so "
                     "drift is detectable")
ap.add_argument("--v5", action="store_true",
                help="emit only the v5 environment (C1-C23 + R*), without the "
                     "v6 constructions; the answer key records sha256 hashes "
                     "of this output too")
args = ap.parse_args()
REF = args.reference or args.reference_conservative
REF_B = args.reference and not args.reference_conservative
V5 = not args.v4
V6 = not args.v4 and not args.v5
# New random draws come from their own generator so that adding v5 content
# cannot shift any value the v4 subset draws from `rng`.
rng5 = random.Random(args.seed + 5000)
rng6 = random.Random(args.seed + 6000)

S = args.schema
DB = "materialize"
# Replica size for the generated cluster. The default is what the Docker
# emulator ships ('100cc' = 1 process, 2 workers); a source build also
# accepts the dev size map's 'scale=1,workers=2'.
CLUSTER_SIZE = os.environ.get("EVAL_CLUSTER_SIZE", "100cc")
rng = random.Random(args.seed)
BUILD_TS = args.build_ts or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# ------------------------------------------------------------------
# Scale parameters (tuned on the dev rig; retune per rig)
# ------------------------------------------------------------------
_SC = max(args.scale, 1)
# Distribution matching: the pipeline this environment models is
# arrangement-dominated because its fact history dwarfs its 24h anchor window
# (window/history ~0.1%). The knobs below reproduce that ratio at laptop
# scale: a fact table large relative to the anchor set, so per-consumer
# re-arrangements of the history outweigh per-anchor reduce state.
N_DELIV = 1_000_000 // _SC   # fact
N_ANCHOR = 10_000 // _SC     # 24h window (the spine). N_DELIV / N_ANCHOR is
                             # THE distribution knob: it sets how much of
                             # the cluster sits in re-arrangements of the
                             # history versus in per-anchor reduce state. The
                             # modeled distribution runs this ratio at ~1000:1;
                             # 100:1 is as far as a laptop-scale fact table can
                             # go while keeping the per-anchor prizes visible.
# courier tiers: 0 = dormant whale, 1..37 hot dormant, 38.. active. The whale's
# row count is pinned near 42k (below 65536) so the 65536 owner-history hints
# stay correct-by-headroom; per-active-courier rows are pinned near 170 so the
# (courier, depot) / (courier, lane) group maxima stay at 64.
WHALE_MOD = max(12, round(N_DELIV / 41_700))
_ACTIVE_FRAC = (1 - 1 / WHALE_MOD) * (8 / 12)
# An active row is an anchor when g % ANCHOR_MOD < 3. The modulus is a prime
# near the value that yields N_ANCHOR anchors; primality keeps the anchor slice
# from resonating with the tier (12, WHALE_MOD), spread (5, 7, 8, 11, 23, 41) or
# detail-overlay moduli, any of which would skew the group maxima the hints are
# calibrated against.
def _prime_at_least(n):
    n = max(n, 5)
    while True:
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            return n
        n += 1
ANCHOR_MOD = _prime_at_least(round(N_DELIV * _ACTIVE_FRAC * 3 / N_ANCHOR))
# NOTE: the courier of an active row is 38 + (g * 7) % (N_COUR - 38), so all
# rows of one courier sit in an arithmetic progression of step (N_COUR - 38).
# That step's residues decide how many distinct lanes (g % 8), depots (g % 23),
# devices (g % 7), alt refs (g % 11), postal codes (g % 41) and apps (g % 5) one
# courier reaches, hence every per-(courier, X) group maximum the hints and the
# C8 ratio are calibrated against. Two rules: 18 mod 24 keeps the 4-lane spread
# the 64 hints assume, and the step must share no factor with the other spread
# moduli. A step divisible by 11, say, collapses a courier's rows onto ONE alt
# ref and multiplies the C8 pair ratio by an order of magnitude.
_SPREAD_MODULI = (5, 7, 11, 23, 41, ANCHOR_MOD)
def _courier_step(target):
    for d in range(0, 24 * 40):
        for cand in (target - d, target + d):
            if cand > 24 and cand % 24 == 18 \
                    and all(cand % m for m in _SPREAD_MODULI):
                return cand
    raise RuntimeError("no courier step satisfies the spread constraints")
N_COUR = 38 + _courier_step(round(N_DELIV * _ACTIVE_FRAC / 170))
N_DEPOT = 97
N_VEH = 30_000 // _SC
N_LINK = 60_000 // _SC
N_LOAN = 8_000 // _SC
N_ALT_MOD = 21_000    # alt_ref value space (shared across ~3 couriers)
NULL_MOD = 23         # alt_ref NULL when g % 23 == 0 (~4.3%; C9 grind:
                      # pairs ~ (anchors/MOD) * (N_DELIV/MOD) at MEASURED
                      # ~180k closure pairs/s => ~15M pairs ~ 1.5 min
                      # one-worker grind)
STORM_MOD_MULT = 1700  # gateway retry storms land on anchors selected by
                       # ANCHOR_MOD * STORM_MOD_MULT, so storm count follows
                       # the anchor slice instead of a fixed id list.
STORM_CALLS = 400     # calls per storm anchor (the 2048 hints stay correct)
BLOB_PAD_MIN = 1050   # jsonb payload pad: ~2.1 kB/row, matching the
BLOB_PAD_SPAN = 1200  # reference blob tail (bytes/row p99 ~2.3k)
DETAIL_SIZES = {}     # filled per table below

def q(name):
    return f"{DB}.{S}.{name}"

OUT = []

def emit(text=""):
    OUT.extend(text.split("\n"))

def obj_banner(kind, name):
    oid = rng.randint(20000, 99999)
    emit(f"-- ---------- {kind}: {name} ----------")
    emit(f"-- catalog id: u{oid}")
    emit(f"-- oid: {oid + 16384}")

# ------------------------------------------------------------------
# Vocabulary
# ------------------------------------------------------------------
P = "dsp"           # product prefix
T2 = "mid"          # tier-2 token (enrichment)
T3 = "roll"         # tier-3 token (window aggregate)
T4 = "pack"         # tier-4 token (terminal MV)
WRAP = "full"       # wrapper suffix

LANES = ["lane_north_metro_a", "lane_south_metro_a", "lane_east_ring_a",
         "lane_west_ring_a", "lane_metro_core_a", "lane_rural_far_a",
         "lane_express_hub_a", "lane_night_shift_a"]
PHASES = ("completed", "failed", "canceled", "on_hold")
TIERS = ["tier_standard_ground", "tier_plus_priority", "tier_pro_sameday",
         "tier_bulk_palletized"]
APPS = ["app_ios_native_v2", "app_android_native_v2", "app_web_portal_v2",
        "app_kiosk_terminal_v2", "app_partner_gateway_v2"]
REGIONS = [f"region_zone_rg{i:02d}_a" for i in range(12)]
DEPOT_KINDS = ["hub", "spoke", "locker", "partner"]

HEADS = ["count_of", "total", "mean", "max", "min", "seconds_since",
         "rate_of", "share_of", "has", "is", "first", "last", "dominant"]
SUBJECTS = ["completed_dropoffs", "failed_dropoffs", "canceled_runs",
            "prior_runs", "depot_visits", "lane_switches", "heavy_loads",
            "refuel_stops", "damage_flags", "hold_events", "scan_gaps",
            "night_runs", "rush_orders", "return_trips", "dock_waits",
            "seal_breaks", "reroute_events", "support_pings", "toll_hits",
            "handoff_steps", "photo_checks", "badge_taps"]
QUALS = ["same_depot", "same_lane", "other_vehicles", "this_courier",
         "before_anchor", "distinct_depots", "peak_hours", ""]
WINDOWS = ["1h", "24h", "2d", "7d", "30d", "90d", "all_time", ""]

_used_feats = set()

def feat_name():
    for _ in range(200):
        parts = [rng.choice(HEADS), rng.choice(SUBJECTS)]
        if rng.random() < 0.55:
            qv = rng.choice(QUALS)
            if qv:
                parts.append(qv)
        wv = rng.choice(WINDOWS)
        if wv:
            parts.append(wv)
        nm = "_".join(parts)
        if nm not in _used_feats:
            _used_feats.add(nm)
            return nm
    raise RuntimeError("feature name pool exhausted")

# ------------------------------------------------------------------
# Base tables
# ------------------------------------------------------------------
# Filler column machinery: (name, sqltype, insert_expr(g))
FILL_TYPES = [
    ("int", lambda m: f"(g * {rng.choice([3,7,11,13])}) % {m}"),
    ("text", lambda m: f"'t' || ((g * {rng.choice([3,7,11])}) % {m})::pg_catalog.text"),
    ("bool", lambda m: f"(g % {rng.choice([2,3,5])} = 0)"),
    ("float8", lambda m: f"((g % {m}) / 97.0)::pg_catalog.float8"),
    ("timestamp", lambda m: f"TIMESTAMP '{BUILD_TS}' - ((g * 17) % {m}) * INTERVAL '1 minute'"),
]
FILL_NAMES = ["route_id", "batch_id", "is_rush", "is_fragile", "eta_at",
    "picked_at", "dropped_at", "distance_km", "fee_units", "tip_units",
    "surge_mult", "package_count", "volume_l", "floor_level", "has_stairs",
    "needs_sig", "temp_band", "priority_rank", "retry_count", "courier_note",
    "depot_note", "gate_code", "zone_hint", "wind_delay", "rain_delay",
    "checksum_a", "checksum_b", "audit_tag", "origin_lat", "origin_lon",
    "dest_lat", "dest_lon", "insurer_code", "contract_id", "wave_id",
    "slot_id", "seal_req", "dock_pref", "weight_class", "handler_id",
    "review_flag", "escalation_lvl", "campaign_id", "ref_channel",
    "shift_code", "hub_note", "ack_state", "sync_tag", "trace_mark",
    "queue_pos", "relay_hop", "cold_chain", "twin_scan", "vault_bin",
    "yard_row", "gate_lane", "ramp_side", "berth_no", "tally_mark",
    "spot_check", "loop_count", "hop_delay", "path_cost", "grid_cell",
    "cell_load", "belt_no", "cage_id", "bay_temp", "door_side"]
_fill_idx = 0

def fill_cols(n):
    global _fill_idx
    cols = []
    for _ in range(n):
        nm = FILL_NAMES[_fill_idx % len(FILL_NAMES)]
        if _fill_idx >= len(FILL_NAMES):
            nm = f"{nm}_{_fill_idx // len(FILL_NAMES) + 1}"
        _fill_idx += 1
        ty, exprf = rng.choice(FILL_TYPES)
        cols.append((nm, ty, exprf(rng.choice([53, 89, 181, 397, 1009]))))
    return cols

def create_table(name, cols):
    obj_banner("table", name)
    emit(f"CREATE TABLE {q(name)} (")
    tymap = {"int": "pg_catalog.int4", "int8": "pg_catalog.int8",
             "text": "pg_catalog.text", "bool": "pg_catalog.bool",
             "float8": "pg_catalog.float8",
             "timestamp": "pg_catalog.timestamp",
             "jsonb": "pg_catalog.jsonb", "numeric": "pg_catalog.numeric"}
    body = []
    for cn, ty, _ in cols:
        body.append(f"    {cn} {tymap.get(ty, ty)}")
    emit(",\n".join(body))
    emit(");")
    emit()

def insert_series(name, cols, n, inner=None):
    """INSERT ... SELECT exprs FROM (inner or generate_series) t(g)."""
    emit(f"INSERT INTO {q(name)}")
    emit("SELECT")
    emit(",\n".join(f"    {expr}" for _, _, expr in cols))
    if inner:
        emit(f"FROM ({inner}) AS t;")
    else:
        emit(f"FROM generate_series(1, {n}) AS g;")
    emit()

# ---- deliveries (fact, 60 cols) ----------------------------------
# courier tiers + age computed in an inner subquery; outer refs t.g/t.cour/t.age_s
DELIV_INNER = f"""SELECT g,
        CASE WHEN g % {WHALE_MOD} = 0 THEN 0
             WHEN g % 12 < 4 THEN 1 + (g % 37)
             ELSE 38 + ((g * 7) % {N_COUR - 38}) END AS cour,
        CASE
            WHEN g % {WHALE_MOD} = 0 OR g % 12 < 4
                THEN 90000 + ((g::pg_catalog.int8 * 7919) % 7686000)
            WHEN g % {ANCHOR_MOD} < 3 THEN
                CASE WHEN g % 10 < 7 THEN (g * 13) % 7200
                     ELSE 7200 + ((g * 17) % 79200) END
            ELSE 90000 + ((g * 31) % 7686000)
        END AS age_s
    FROM generate_series(1, {N_DELIV}) AS g"""

deliv_core = [
    ("delivery_id", "int", "t.g"),
    ("courier_id", "int", "t.cour"),
    ("depot_id", "int", "((t.cour * 7) + (t.g % 23)) % 97"),
    ("link_id", "int",
     f"CASE WHEN t.g % 5 = 4 THEN NULL ELSE 1 + ((t.g * 3) % {N_LINK}) END"),
    ("created_at", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - t.age_s * INTERVAL '1 second'"),
    ("phase", "text",
     "CASE WHEN t.g % 20 < 14 THEN 'completed' WHEN t.g % 20 < 17 THEN 'failed'"
     " WHEN t.g % 20 < 19 THEN 'canceled' ELSE 'on_hold' END"),
    ("load_units", "float8", "((t.g % 8000) / 40.0)::pg_catalog.float8"),
    ("lane_code", "text",
     "(ARRAY[" + ",".join(f"'{l}'" for l in LANES) + "])[1 + t.g % 8]"),
    ("service_tier", "text",
     "(ARRAY[" + ",".join(f"'{x}'" for x in TIERS) + "])[1 + t.g % 4]"),
    ("alt_ref", "text",
     f"CASE WHEN t.g % {NULL_MOD} = 0 THEN NULL"
     f" ELSE 'AR' || ((((t.cour % 613) * 29) + (t.g % 11)) % {N_ALT_MOD})::pg_catalog.text END"),
    ("device_id", "text",
     "CASE WHEN t.g % 17 = 0 THEN NULL"
     " ELSE 'DEV' || (((t.cour * 5) + (t.g % 7)) % 9000)::pg_catalog.text"
     " || '-hw' END"),
    ("postal_code", "text",
     "'PC' || (((t.cour * 3) + (t.g % 41)) % 9973)::pg_catalog.text"
     " || '-zone'"),
    ("region_code", "text",
     "(ARRAY[" + ",".join(f"'{r}'" for r in REGIONS) + "])[1 + t.g % 12]"),
    ("promo_code", "text",
     "CASE WHEN t.g % 9 = 0 THEN 'PR' || (t.g % 400)::pg_catalog.text ELSE NULL END"),
    ("source_app", "text",
     "(ARRAY[" + ",".join(f"'{a}'" for a in APPS) + "])[1 + t.g % 5]"),
    ("risk_score", "float8", "((t.g % 1000) / 1000.0)::pg_catalog.float8"),
]
DELIV_WRAP_COLS = [c[0] for c in deliv_core]           # the 16-col wrapper set
deliv_cols = deliv_core + fill_cols(44)
# filler exprs reference g not t.g; fix up
deliv_cols = deliv_core + [(n, ty, e.replace("(g ", "(t.g ").replace("((g", "((t.g"))
                           for n, ty, e in deliv_cols[len(deliv_core):]]

# ---- couriers (owner, 65 cols) -----------------------------------
cour_core = [
    ("courier_id", "int", "g - 1"),
    ("home_depot_id", "int", "((g - 1) * 7) % 97"),
    ("joined_at", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - ((g * 13) % 1400) * INTERVAL '1 day'"),
    ("rank_grade", "int", "g % 7"),
    ("region_code", "text",
     "(ARRAY[" + ",".join(f"'{r}'" for r in REGIONS) + "])[1 + g % 12]"),
    ("lane_pref", "text",
     "(ARRAY[" + ",".join(f"'{l}'" for l in LANES) + "])[1 + g % 8]"),
    ("active_flag", "bool", "(g % 11 <> 0)"),
    ("bio_note", "text",
     "repeat('b', 120) || (g % 977)::pg_catalog.text || repeat('n', 80)"),
    ("address_full", "text",
     "repeat('a', 70) || (g % 4093)::pg_catalog.text || repeat('d', 46)"),
    ("device_fingerprint", "text",
     "repeat('f', 40) || ((g * 11) % 8191)::pg_catalog.text || repeat('p', 20)"),
    ("phone_hash", "text", "'H' || ((g * 31) % 65521)::pg_catalog.text"),
    ("vehicle_pref", "text", "'v' || (g % 6)::pg_catalog.text"),
    ("shift_pref", "text", "'s' || (g % 3)::pg_catalog.text"),
    ("rating_avg", "float8", "(30 + g % 21)::pg_catalog.float8 / 10.0"),
]
COUR_WRAP_COLS = [c[0] for c in cour_core]             # 14-col wrapper (C2)
cour_cols = cour_core + fill_cols(51)

# ---- depots ------------------------------------------------------
depot_cols = [
    ("depot_id", "int", "g - 1"),
    ("depot_kind", "text",
     "(ARRAY[" + ",".join(f"'{k}'" for k in DEPOT_KINDS) + "])[1 + g % 4]"),
    ("city_code", "text", "'C' || (g % 40)::pg_catalog.text"),
    ("region_code", "text",
     "(ARRAY[" + ",".join(f"'{r}'" for r in REGIONS) + "])[1 + g % 12]"),
    ("opened_at", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - ((g * 41) % 4000) * INTERVAL '1 day'"),
    ("dock_count", "int", "2 + g % 14"),
    ("is_247", "bool", "(g % 3 = 0)"),
] + fill_cols(21)

# ---- vehicles + links + loaners ----------------------------------
veh_cols = [
    ("vehicle_id", "int", "g"),
    ("plate_ref", "text",
     "CASE WHEN g % 13 = 0 THEN NULL ELSE 'PL' || ((g * 7) % 26000)::pg_catalog.text END"),
    ("axle_a", "text", "'ax' || (g % 900)::pg_catalog.text"),
    ("axle_b", "text", "'bx' || ((g * 3) % 700)::pg_catalog.text"),
    ("garage_id", "int", "(g * 11) % 300"),
    ("acquired_at", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - ((g * 29) % 2000) * INTERVAL '1 day'"),
    ("vclass", "text", "'k' || (g % 5)::pg_catalog.text"),
] + fill_cols(11)

link_cols = [
    ("link_id", "int", "g"),
    ("vehicle_id", "int", f"1 + ((g * 13) % {N_VEH})"),
    ("bound_at", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - ((g * 7) % 130000) * INTERVAL '1 minute'"),
    ("bind_kind", "text", "'b' || (g % 4)::pg_catalog.text"),
    ("released", "bool", "(g % 6 = 0)"),
    ("bind_note", "text", "'ln' || (g % 89)::pg_catalog.text"),
]

loan_cols = [
    ("loaner_id", "int", "g"),
    ("delivery_id", "int", f"1 + ((g * 61) % {N_DELIV})"),
    ("vehicle_ref", "text",
     "CASE WHEN g % 11 = 0 THEN NULL ELSE 'PL' || ((g * 3) % 26000)::pg_catalog.text END"),
    ("loan_kind", "text", "'lk' || (g % 3)::pg_catalog.text"),
    ("note_id", "int", "CASE WHEN g % 4 = 0 THEN NULL ELSE 1 + (g % 6000) END"),
    ("opened_at", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - ((g * 19) % 100000) * INTERVAL '1 minute'"),
    ("closed", "bool", "(g % 5 < 3)"),
    ("loan_units", "float8", "((g % 500) / 9.0)::pg_catalog.float8"),
]

loan_note_cols = [
    ("note_id", "int", "g"),
    ("noted_at", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - ((g * 23) % 90000) * INTERVAL '1 minute'"),
    ("note_kind", "text", "'nk' || (g % 5)::pg_catalog.text"),
    ("note_text", "text", "'nt' || (g % 400)::pg_catalog.text"),
    ("cleared", "bool", "(g % 7 = 0)"),
]

# ---- telemetry ---------------------------------------------------
# route_pings attach to anchor deliveries; valid_flag gates the mega (15%).
ping_cols_ddl = [("ping_id", "int"), ("delivery_id", "int"),
    ("pinged_at", "timestamp"), ("valid_flag", "bool"), ("lat_cell", "int"),
    ("lon_cell", "int"), ("speed_band", "text"), ("gap_s", "int"),
    ("battery_pct", "int")]

devmeta_cols = [
    ("device_id", "text",
     "'DEV' || (g % 9000)::pg_catalog.text || '-hw'"),
    ("courier_id", "int", f"(g * 3) % {N_COUR}"),
    ("os_kind", "text", "'os' || (g % 4)::pg_catalog.text"),
    ("first_seen", "timestamp",
     f"TIMESTAMP '{BUILD_TS}' - ((g * 37) % 700) * INTERVAL '1 day'"),
    ("is_shared", "bool", "(g % 9 = 0)"),
    ("push_ok", "bool", "(g % 4 <> 0)"),
    ("app_ver", "text", "'v' || (g % 30)::pg_catalog.text"),
    ("net_kind", "text", "'n' || (g % 3)::pg_catalog.text"),
    ("locale", "text", "'lc' || (g % 12)::pg_catalog.text"),
    ("risk_hint", "float8", "((g % 100) / 100.0)::pg_catalog.float8"),
    ("meta_note", "text", "'mn' || (g % 200)::pg_catalog.text"),
]

# ---- gateway_calls (jsonb blob) ----------------------------------
gw_cols_ddl = [("call_id", "int"), ("delivery_id", "int"), ("seq", "int"),
    ("call_kind", "text"), ("valid_flag", "bool"), ("called_at", "timestamp"),
    ("grade", "float8"), ("http_code", "int"), ("latency_ms", "int"),
    ("payload", "jsonb")]

BLOB_NUM_KEYS = [f"k_{w}" for w in ["conf", "score", "band", "load", "dwell",
                                    "churn", "swing", "drift", "pulse", "slope"]]
BLOB_TXT_KEYS = [f"k_{w}" for w in ["mode", "vendor", "route", "carrier",
                                    "handler", "origin", "signal", "grade_lbl",
                                    "cohort"]]
BLOB_OBJ_KEYS = ["nest_geo", "nest_meta", "nest_flags"]

def blob_expr(gref):
    parts = []
    for i, k in enumerate(BLOB_NUM_KEYS):
        parts.append(f"'{k}', (({gref} * {3 + i}) % 1000) / 10.0")
    for i, k in enumerate(BLOB_TXT_KEYS):
        parts.append(f"'{k}', 'x' || (({gref} * {5 + i}) % 300)::pg_catalog.text")
    parts.append(f"'nest_geo', pg_catalog.jsonb_build_object('cell', {gref} % 512, 'ring', {gref} % 7)")
    parts.append(f"'nest_meta', pg_catalog.jsonb_build_object('src', 'g' || ({gref} % 9)::pg_catalog.text, 'ver', {gref} % 40)")
    parts.append(f"'nest_flags', pg_catalog.jsonb_build_object('hot', {gref} % 2 = 0, 'gate', {gref} % 5 = 0)")
    parts.append(f"'k_ok', ({gref} % 4 <> 0)")
    parts.append(f"'pad', repeat('x', {BLOB_PAD_MIN} + {gref} % {BLOB_PAD_SPAN})")
    return "pg_catalog.jsonb_build_object(\n        " + ",\n        ".join(parts) + ")"

# ---- narrow detail tables ----------------------------------------
# (name, rows, extra cols beyond delivery/courier fk + ts)
DETAILS = [
    # per-delivery details (fk = delivery_id, mostly hit anchors via formula)
    ("scans", 40_000, "delivery"),
    ("holds", 18_000, "delivery"),
    ("claims", 14_000, "delivery"),
    ("ratings", 22_000, "delivery"),
    ("damage_reports", 9_000, "delivery"),
    ("signatures", 26_000, "delivery"),
    ("toll_events", 16_000, "delivery"),
    ("delay_logs", 24_000, "delivery"),
    ("handoffs", 12_000, "delivery"),
    ("address_checks", 15_000, "delivery"),
    ("weight_checks", 10_000, "delivery"),
    ("support_tickets", 8_000, "delivery"),
    ("callback_logs", 7_000, "delivery"),
    ("photo_logs", 20_000, "delivery"),
    ("seal_events", 9_000, "delivery"),
    ("permit_grants", 6_000, "delivery"),
    ("dock_slots", 13_000, "delivery"),
    ("manifests", 11_000, "delivery"),
    ("return_runs", 8_000, "delivery"),
    ("dispute_cases", 7_000, "delivery"),
    # per-courier details
    ("refuel_stops", 30_000, "courier"),
    ("bonus_grants", 9_000, "courier"),
    ("penalty_marks", 7_000, "courier"),
    ("shift_logs", 45_000, "courier"),
    ("training_flags", 4_000, "courier"),
    ("badge_scans", 35_000, "courier"),
    ("curfew_windows", 3_000, "courier"),
    ("depot_queues", 15_000, "delivery"),
]

def detail_cols(name, kind):
    fk = ("delivery_id", "int", f"1 + ((g * 61) % {N_DELIV})") if kind == "delivery" \
        else ("courier_id", "int", f"38 + ((g * 7) % {N_COUR - 38})")
    if name == "shift_logs":
        # half the rows cluster on 8 couriers => true per-courier group ~2.8k
        # (c6e's 256 hint is UNDERSIZED there)
        fk = ("courier_id", "int",
              "CASE WHEN g % 2 = 0 THEN 38 + (g % 8) * 245"
              f" ELSE 38 + ((g * 7) % {N_COUR - 38}) END")
    cols = [
        (f"{name[:-1] if name.endswith('s') else name}_id", "int", "g"),
        fk,
        ("noted_at", "timestamp",
         f"TIMESTAMP '{BUILD_TS}' - ((g * {rng.choice([7, 11, 13, 17])}) % 7700000) * INTERVAL '1 second'"),
        ("mark_kind", "text", f"'m' || (g % {rng.choice([5, 7, 9])})::pg_catalog.text"),
        ("mark_phase", "text",
         "CASE WHEN g % 10 < 7 THEN 'completed' WHEN g % 10 < 9 THEN 'failed' ELSE 'canceled' END"),
        ("mark_units", "float8", f"((g % {rng.choice([300, 700])}) / 7.0)::pg_catalog.float8"),
    ]
    extra = rng.randint(0, 3)
    cols += fill_cols(extra)
    return cols

# ------------------------------------------------------------------
# SQL text helpers (formatted style: one element per line)
# ------------------------------------------------------------------
def view_open(name, mat=False, cluster=None):
    obj_banner("materialized view" if mat else "view", name)
    if mat:
        emit(f"CREATE MATERIALIZED VIEW {q(name)}")
        emit(f"    IN CLUSTER {cluster}")
        emit("    WITH (REFRESH = ON COMMIT)")
        emit("    AS")
    else:
        emit(f"CREATE VIEW {q(name)} AS")

def sel_lines(cols, indent=4):
    pad = " " * indent
    return ",\n".join(f"{pad}{c}" for c in cols)

SPINE = f"{P}_{T2}_fresh_24h"
FACTW = f"{P}_deliveries_{WRAP}"
COURW = f"{P}_couriers_{WRAP}"
DEPOTW = f"{P}_depots_{WRAP}"
VEHW = f"{P}_vehicles_{WRAP}"
GWW = f"{P}_gateway_calls_{WRAP}"
KEYSPINE = f"{P}_{T2}_asset_keys"
PAIRS = f"{P}_{T2}_prior_pairs"
IDENT = f"{P}_{T2}_ident_flags"
MEGA = f"{P}_{T2}_asset_saga"

# stats tallies
STATS = {"joins": 0, "left": 0, "filters": 0, "hints": 0, "picks": 0,
         "coalesce": 0}

def J(kind, rel, alias, on):
    STATS["joins"] += 1
    if kind.startswith("LEFT"):
        STATS["left"] += 1
    return f"{kind} JOIN {rel} AS {alias}\n    ON {on}"

def OPT(hint_kind, size):
    STATS["hints"] += 1
    return f"OPTIONS ({hint_kind} INPUT GROUP SIZE = {size})"

def CO(expr, default, alias):
    STATS["coalesce"] += 1
    return (f"COALESCE(\n        {expr},\n        {default})"
            f" AS {alias}")

# output-column registry: view name -> list of exported column names
VIEW_COLS = {}

def FILT(agg, cond):
    STATS["filters"] += 1
    return f"{agg} FILTER (WHERE {cond})"

# ==================================================================
# EMISSION
# ==================================================================
_GEN = "v4 environment: generated by build_v4.py" if args.v4 \
    else ("v5 environment: generated by build_v5.py" if args.v5
          else "v6 environment: generated by build_v6.py")
emit(f"-- {_GEN} (seed {args.seed})")
emit(f"-- build timestamp (UTC): {BUILD_TS}")
emit()
emit(f"CREATE SCHEMA {S};")
emit(f"CREATE CLUSTER {S} (SIZE '{CLUSTER_SIZE}');")
emit(f"SET schema = {S};")
emit(f"SET cluster = {S};")
emit()

# ---- tables ------------------------------------------------------
create_table("deliveries", deliv_cols)
create_table("couriers", cour_cols)
create_table("depots", depot_cols)
create_table("vehicles", veh_cols)
create_table("vehicle_links", link_cols)
create_table("loaner_runs", loan_cols)
create_table("loaner_notes", loan_note_cols)
create_table("route_pings", [(n, t, None) for n, t in ping_cols_ddl])
create_table("device_meta", devmeta_cols)
create_table("gateway_calls", [(n, t, None) for n, t in gw_cols_ddl])
DETAIL_COLS = {}
for dn, drows, dkind in DETAILS:
    DETAIL_COLS[dn] = detail_cols(dn, dkind)
    DETAIL_SIZES[dn] = drows
    create_table(dn, DETAIL_COLS[dn])

# ---- data --------------------------------------------------------
emit("-- ============ data ============")
emit()
insert_series("deliveries", deliv_cols, N_DELIV, inner=DELIV_INNER)
insert_series("couriers", cour_cols, N_COUR)
insert_series("depots", depot_cols, N_DEPOT)
insert_series("vehicles", veh_cols, N_VEH)
insert_series("vehicle_links", link_cols, N_LINK)
insert_series("loaner_runs", loan_cols, N_LOAN)
insert_series("loaner_notes", loan_note_cols, 6_000)
for dn, drows, dkind in DETAILS:
    insert_series(dn, DETAIL_COLS[dn], drows // _SC)

# route_pings: rows for anchor deliveries (valid ~15%)
emit(f"""INSERT INTO {q('route_pings')}
SELECT
    d.delivery_id * 10 + s.s,
    d.delivery_id,
    d.created_at + s.s * INTERVAL '3 minute',
    (d.delivery_id % 20 < 3) AND s.s = 1,
    (d.delivery_id * 3) % 4096,
    (d.delivery_id * 7) % 4096,
    'sb' || (d.delivery_id % 5)::pg_catalog.text,
    (d.delivery_id * s.s) % 240,
    20 + (d.delivery_id % 80)
FROM {q('deliveries')} AS d,
     generate_series(1, 2) AS s(s)
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3;
""")

# gateway_calls: 1-3 calls per anchor + 5 retry storms (2000 calls each)
emit(f"""INSERT INTO {q('gateway_calls')}
SELECT
    d.delivery_id * 8 + s.s,
    d.delivery_id,
    s.s,
    CASE WHEN s.s % 2 = 1 THEN 'quote' ELSE 'verify' END,
    (d.delivery_id + s.s) % 5 <> 0,
    d.created_at + s.s * INTERVAL '20 second',
    ((d.delivery_id * s.s) % 1000) / 10.0,
    CASE WHEN (d.delivery_id + s.s) % 11 = 0 THEN 502 ELSE 200 END,
    40 + ((d.delivery_id * s.s) % 900),
    {blob_expr("(d.delivery_id + s.s)")}
FROM {q('deliveries')} AS d,
     generate_series(1, 2) AS s(s)
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3
  AND s.s <= 1 + (d.delivery_id % 3) / 2;
""")
emit(f"""INSERT INTO {q('gateway_calls')}
SELECT
    900000000 + (d.delivery_id % 100000) * 4000 + s.s,
    d.delivery_id,
    3 + s.s,
    'verify',
    s.s % 7 <> 0,
    d.created_at + s.s * INTERVAL '1 second',
    ((d.delivery_id * s.s) % 1000) / 10.0,
    CASE WHEN s.s % 3 = 0 THEN 429 ELSE 200 END,
    40 + ((d.delivery_id * s.s) % 900),
    {blob_expr("(d.delivery_id * 7 + s.s)")}
FROM {q('deliveries')} AS d,
     generate_series(1, {STORM_CALLS}) AS s(s)
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD * STORM_MOD_MULT} < 3;
""")

# C7 data: 1 delay inside each anchor's 15-min window, +10% extras
# => pairs/anchors ~1.1
DETAIL_STD = "(delivery_id, noted_at, mark_kind, mark_phase, mark_units)"

def overlay(table, idcol_unused, where_mod, where_res, series_expr, ts_off,
            base=800_000_000):
    idc = f"{table[:-1] if table.endswith('s') else table}_id"
    emit(f"""INSERT INTO {q(table)}
    ({idc}, delivery_id, noted_at, mark_kind, mark_phase, mark_units)
SELECT
    {base} + d.delivery_id * 200 + s.s,
    d.delivery_id,
    d.created_at - ({ts_off}) * INTERVAL '1 minute',
    'm' || (s.s % 4)::pg_catalog.text,
    CASE WHEN s.s % 5 = 0 THEN 'failed' ELSE 'completed' END,
    ((s.s % 90) / 3.0)::pg_catalog.float8
FROM {q('deliveries')} AS d,
     generate_series(1, 200) AS s(s)
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3
  AND d.delivery_id % {where_mod} = {where_res}
  AND s.s <= {series_expr};
""")

emit(f"""INSERT INTO {q('delay_logs')}
    (delay_log_id, delivery_id, noted_at, mark_kind, mark_phase, mark_units)
SELECT
    800000000 + d.delivery_id,
    d.delivery_id,
    d.created_at - (d.delivery_id % 13) * INTERVAL '1 minute',
    'm0',
    'completed',
    ((d.delivery_id % 300) / 7.0)::pg_catalog.float8
FROM {q('deliveries')} AS d
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3;
""")
emit(f"""INSERT INTO {q('delay_logs')}
    (delay_log_id, delivery_id, noted_at, mark_kind, mark_phase, mark_units)
SELECT
    810000000 + d.delivery_id,
    d.delivery_id,
    d.created_at - ((d.delivery_id * 3) % 14) * INTERVAL '1 minute',
    'm1',
    'completed',
    ((d.delivery_id % 200) / 5.0)::pg_catalog.float8
FROM {q('deliveries')} AS d
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3
  AND d.delivery_id % 10 = 0;
""")

# hint-truth overlays: cluster detail rows on a slice of anchors so each
# hinted site's TRUE max group size is what the manifest claims
overlay("scans", None, 16, 0, "1 + d.delivery_id % 40", "s.s % 60")       # c6a true ~40
overlay("manifests", None, 24, 8, "1 + d.delivery_id % 12", "s.s % 60")   # c6b true ~12
overlay("ratings", None, 256, 16, "100 + d.delivery_id % 50", "s.s % 200")  # 256-correct
overlay("handoffs", None, 64, 1, "1 + d.delivery_id % 40", "s.s % 60")    # 64-correct
overlay("return_runs", None, 128, 2, "80 + d.delivery_id % 40", "s.s % 200")  # 256-correct
overlay("weight_checks", None, 64, 5, "10 + d.delivery_id % 20", "s.s % 90")  # c6c true ~30
overlay("dispute_cases", None, 64, 3, "5 + d.delivery_id % 20", "s.s % 90")

# ---- pre-existing indexes (C3 dead + colleague-redundant target below) ----
emit("-- ============ pre-existing indexes ============")
if not REF:
    emit(f"CREATE INDEX idx_gateway_calls_kind ON {q('gateway_calls')} (call_kind);")
    emit(f"CREATE INDEX idx_couriers_home ON {q('couriers')} (home_depot_id);")
emit()

# ==================================================================
# Wrapper layer (8)
# ==================================================================
emit("-- ============ wrapper views ============")
emit()
view_open(FACTW)
emit("SELECT")
emit(sel_lines(DELIV_WRAP_COLS))
emit(f"FROM {q('deliveries')};")
emit()

view_open(COURW)     # C2 fat wrapper: 3 fat text cols ride along
emit("SELECT")
emit(sel_lines(COUR_WRAP_COLS))
emit(f"FROM {q('couriers')};")
emit()

view_open(DEPOTW)
emit("SELECT")
emit(sel_lines([c[0] for c in depot_cols[:8]]))
emit(f"FROM {q('depots')};")
emit()

view_open(VEHW)      # the two-table wrapper variant
emit("SELECT")
emit(sel_lines(["b.vehicle_id", "b.plate_ref", "b.axle_a", "b.axle_b",
                "b.garage_id", "b.vclass",
                "d.link_id", "d.bound_at", "d.bind_kind", "d.released"]))
emit(f"FROM {q('vehicles')} AS b")
emit(J("", q("vehicle_links"), "d", "d.vehicle_id = b.vehicle_id").replace(" JOIN", "JOIN", 1) + ";")
emit()

view_open(GWW)
emit("SELECT")
emit(sel_lines(["call_id", "delivery_id", "seq", "call_kind", "valid_flag",
                "called_at", "grade", "http_code", "payload"]))
emit(f"FROM {q('gateway_calls')};")
emit()

for wname, wtab in [("scans", "scans"), ("holds", "holds"), ("claims", "claims")]:
    view_open(f"{P}_{wname}_{WRAP}")
    emit("SELECT")
    emit(sel_lines([c[0] for c in DETAIL_COLS[wtab]]))
    emit(f"FROM {q(wtab)};")
    emit()

# ==================================================================
# Temporal spine (T2)
# ==================================================================
emit("-- ============ temporal spine ============")
emit()
view_open(SPINE)
emit("SELECT")
emit(sel_lines(DELIV_WRAP_COLS))
emit(f"FROM {q(FACTW)}")
emit("""WHERE
    mz_catalog.mz_now() >= GREATEST(
        (pg_catalog.extract('epoch', created_at) * 1000)::pg_catalog.int8,
        0)
    AND
    mz_catalog.mz_now() < GREATEST(
        (pg_catalog.extract('epoch', created_at) * 1000)::pg_catalog.int8,
        0)
        + 86400000;""")
emit()

# ---- reference boundary views (C1 K1/K2, C9 alt, spine index) ----
HB_DEPOT = "dsp_hist_by_depot" if REF_B else FACTW
HB_LANE = "dsp_hist_by_lane" if REF_B else FACTW
HB_ALT = "dsp_hist_by_alt" if REF_B else FACTW
if REF_B:
    emit("-- ============ boundary views (reference fix set) ============")
    emit()
    view_open("dsp_hist_by_depot")
    emit("SELECT")
    emit(sel_lines(["courier_id", "depot_id", "delivery_id", "created_at",
                    "phase", "load_units", "service_tier", "lane_code",
                    "source_app", "device_id", "promo_code"]))
    emit(f"FROM {q(FACTW)};")
    emit()
    view_open("dsp_hist_by_lane")
    emit("SELECT")
    emit(sel_lines(["courier_id", "lane_code", "delivery_id", "created_at",
                    "phase", "load_units", "promo_code", "source_app",
                    "depot_id"]))
    emit(f"FROM {q(FACTW)};")
    emit()
    view_open("dsp_hist_by_alt")
    emit("SELECT")
    emit(sel_lines(["alt_ref", "delivery_id", "courier_id", "created_at"]))
    emit(f"FROM {q(FACTW)}")
    emit("WHERE alt_ref IS NOT NULL;")
    emit()
    emit(f"CREATE INDEX idx_hist_by_depot ON {q('dsp_hist_by_depot')} (courier_id, depot_id);")
    emit(f"CREATE INDEX idx_hist_by_lane ON {q('dsp_hist_by_lane')} (courier_id, lane_code);")
    emit(f"CREATE INDEX idx_hist_by_alt ON {q('dsp_hist_by_alt')} (alt_ref);")
    emit(f"CREATE INDEX idx_spine ON {q(SPINE)} (delivery_id);")
    emit()

# ==================================================================
# Key spine (3A) + identity view + pair helper (3B)
# ==================================================================
emit("-- ============ key spine / identity / pairs ============")
emit()
view_open(KEYSPINE)
emit("SELECT")
emit(sel_lines([
    "f.delivery_id", "f.courier_id", "f.created_at", "f.phase",
    "f.load_units",
    "a.axle_a", "a.axle_b", "a.garage_id",
    "a.bound_at AS asset_created",
    """CASE
        WHEN NULLIF(a.plate_ref, '') IS NOT NULL
            THEN 'r|' || a.plate_ref
        WHEN NULLIF(a.axle_a, '') IS NOT NULL
                AND NULLIF(a.axle_b, '') IS NOT NULL
            THEN 'p|' || a.axle_a || '|' || a.axle_b
        ELSE 'i|' || a.vehicle_id::pg_catalog.text
    END AS match_key""",
    "false AS is_alt_channel",
    "NULL::pg_catalog.timestamp AS alt_noted_at"]))
emit(f"FROM {q(FACTW)} AS f")
emit(J("", q("vehicle_links"), "l", "l.link_id = f.link_id").lstrip())
emit(J("", q(VEHW), "a", "a.link_id = l.link_id").lstrip())
emit("UNION ALL")
emit("SELECT")
emit(sel_lines([
    "f.delivery_id", "f.courier_id", "f.created_at", "f.phase",
    "f.load_units",
    "NULL::pg_catalog.text", "NULL::pg_catalog.text", "-1",
    "COALESCE(x2.noted_at, f.created_at) AS asset_created",
    """CASE
        WHEN NULLIF(x.vehicle_ref, '') IS NOT NULL
            THEN 'r|' || x.vehicle_ref
        WHEN x.note_id IS NOT NULL
            THEN 'n|' || x.note_id::pg_catalog.text
        ELSE 'i|' || x.loaner_id::pg_catalog.text
    END AS match_key""",
    "true AS is_alt_channel",
    "x2.noted_at AS alt_noted_at"]))
emit(f"FROM {q(FACTW)} AS f")
emit(J("", q("loaner_runs"), "x", "x.delivery_id = f.delivery_id").lstrip())
emit(J("LEFT", q("loaner_notes"), "x2", "x2.note_id = x.note_id") + ";")
emit()

# identity view: mid-tier hub, 5 consumers, PRE-INDEXED (colleague-redundant)
view_open(IDENT)
emit("WITH")
emit("""    dev AS (
        SELECT
            o.delivery_id AS anchor_id,
            pg_catalog.bool_or(m.is_shared) AS dev_shared,
            pg_catalog.bool_or(m.courier_id <> o.courier_id) AS dev_foreign,
            pg_catalog.max(m.risk_hint) AS dev_risk
        FROM """ + q(SPINE) + """ AS o
        JOIN """ + q("device_meta") + """ AS m
            ON m.device_id = o.device_id
        GROUP BY o.delivery_id
    ),
    loan AS (
        SELECT
            o.delivery_id AS anchor_id,
            pg_catalog.count(*) AS loan_n,
            pg_catalog.bool_or(NOT lr.closed) AS loan_open
        FROM """ + q(SPINE) + """ AS o
        JOIN """ + q("loaner_runs") + """ AS lr
            ON lr.delivery_id = o.delivery_id
        GROUP BY o.delivery_id
    )""")
STATS["joins"] += 2
emit("SELECT")
emit(sel_lines([
    "o.delivery_id AS anchor_id",
    "o.courier_id",
    "o.alt_ref",
    CO("dev.dev_shared", "false", "ident_dev_shared"),
    CO("dev.dev_foreign", "false", "ident_dev_foreign"),
    CO("dev.dev_risk", "0.0", "ident_dev_risk"),
    CO("loan.loan_n", "0", "ident_loan_n"),
    CO("loan.loan_open", "false", "ident_loan_open"),
    """CASE
        WHEN COALESCE(dev.dev_risk, 0.0) > 0.8 THEN 'high'
        WHEN COALESCE(dev.dev_shared, false) THEN 'watch'
        ELSE 'clear'
    END AS ident_risk_band"""]))
emit(f"FROM {q(SPINE)} AS o")
emit(J("LEFT", "dev", "dev0", "o.delivery_id = dev0.anchor_id").replace("dev0", "dev"))
emit(J("LEFT", "loan", "loan0", "o.delivery_id = loan0.anchor_id").replace("loan0", "loan") + ";")
emit()

# pairs (3B): 4 match-strategy arms, GROUP BY dedup; single consumer = C8 pivot
view_open(PAIRS)
emit("WITH arms AS (")
emit("""    SELECT
        o.delivery_id AS anchor_id,
        h.delivery_id AS prior_id
    FROM """ + q(SPINE) + """ AS o
    JOIN """ + q(HB_DEPOT) + """ AS h
        ON h.courier_id = o.courier_id
        AND h.depot_id = o.depot_id
        AND h.created_at < o.created_at
    UNION ALL
    SELECT
        o.delivery_id,
        h.delivery_id
    FROM """ + q(SPINE) + """ AS o
    JOIN """ + q(DEPOTW) + """ AS td
        ON td.depot_id = o.depot_id
        AND td.depot_kind = 'hub'
    JOIN """ + q(FACTW) + """ AS h
        ON h.courier_id = o.courier_id
        AND h.alt_ref = o.alt_ref
        AND h.created_at < o.created_at
    WHERE o.alt_ref IS NOT NULL
    UNION ALL
    SELECT
        o.delivery_id,
        h.delivery_id
    FROM """ + q(SPINE) + """ AS o
    JOIN """ + q(DEPOTW) + """ AS td
        ON td.depot_id = o.depot_id
        AND td.depot_kind = 'spoke'
    JOIN """ + q(FACTW) + """ AS h
        ON h.courier_id = o.courier_id
        AND h.device_id = o.device_id
        AND h.created_at < o.created_at
    WHERE o.device_id IS NOT NULL
    UNION ALL
    SELECT
        o.delivery_id,
        h.delivery_id
    FROM """ + q(SPINE) + """ AS o
    JOIN """ + q(DEPOTW) + """ AS td
        ON td.depot_id = o.depot_id
        AND td.depot_kind = 'locker'
    JOIN """ + q(FACTW) + """ AS h
        ON h.courier_id = o.courier_id
        AND h.postal_code = o.postal_code
        AND h.service_tier = o.service_tier
        AND h.created_at < o.created_at
)""")
STATS["joins"] += 7
emit("SELECT")
emit("    anchor_id,")
emit("    prior_id")
emit("FROM arms")
emit("GROUP BY")
emit("    anchor_id,")
emit("    prior_id;")
emit()

# ==================================================================
# Enrichment tier (T4 template instances)
# ==================================================================
emit("-- ============ enrichment views ============")
emit()

COURIER_TABLES = {"refuel_stops", "bonus_grants", "penalty_marks",
                  "shift_logs", "training_flags", "badge_scans",
                  "curfew_windows"}

def _jc(d):
    return "courier_id" if d in COURIER_TABLES else "delivery_id"

def std_enrichment(name, details, npick=1, nmark=1, ntally=1,
                   pick_hint=None, extra_feats=16, consume_ident=False,
                   consume_cour=False, tally_hint=None, filters=0):
    """Stamp a T4 join-spine -> per-anchor reduce -> LEFT-JOIN assembly view.
    details: list of detail table names to draw CTE inputs from. Hints are
    emitted only where explicitly given (hint-truthfulness: C6's 'rest
    correct' field must hold at this data scale). Records exported column
    names in VIEW_COLS[name] as (colname, kind)."""
    view_open(name)
    emit("WITH")
    ctes = []
    body = []
    di = 0
    for i in range(npick):
        d = details[di % len(details)]; di += 1
        cn = f"pick_{i}" if npick > 1 else "picked"
        ctes.append((cn, "pick", d))
        STATS["picks"] += 1
        STATS["joins"] += 1
        hint_line = ""
        if pick_hint and i == 0:
            hint_line = f"\n        OPTIONS (DISTINCT ON INPUT GROUP SIZE = {pick_hint})"
            STATS["hints"] += 1
        body.append(f"""    {cn} AS (
        SELECT DISTINCT ON (o.delivery_id)
            o.delivery_id AS anchor_id,
            d.mark_kind,
            d.mark_units,
            d.noted_at
        FROM {q(SPINE)} AS o
        JOIN {q(d)} AS d
            ON d.{_jc(d)} = o.{_jc(d)}{hint_line}
        ORDER BY
            o.delivery_id,
            d.noted_at DESC,
            d.{d[:-1] if d.endswith('s') else d}_id DESC
    )""")
    for i in range(nmark):
        d = details[di % len(details)]; di += 1
        cn = f"marked_{i}" if nmark > 1 else "marked"
        ctes.append((cn, "mark", d))
        STATS["joins"] += 1
        b2_join = ""
        b2_agg = ""
        if i % 2 == 1 and len(details) > 1:
            d2 = details[(di + 1) % len(details)]
            STATS["joins"] += 1
            b2_join = f"""
        LEFT JOIN {q(d2)} AS b2
            ON b2.{_jc(d2)} = o.{_jc(d2)}
            AND b2.mark_kind = b.mark_kind"""
            b2_agg = """
            pg_catalog.bool_or(b2.mark_phase = 'failed') AS has_echo,"""
            STATS["left"] += 1
        body.append(f"""    {cn} AS (
        SELECT
            o.delivery_id AS anchor_id,
            pg_catalog.bool_or(b.mark_phase = 'failed') AS has_bad,
            pg_catalog.bool_or(b.mark_kind = 'm1') AS has_kind,{b2_agg}
            pg_catalog.count(*) AS n_marks
        FROM {q(SPINE)} AS o
        JOIN {q(d)} AS b
            ON b.{_jc(d)} = o.{_jc(d)}{b2_join}
        GROUP BY o.delivery_id
    )""")
    for i in range(ntally):
        d = details[di % len(details)]; di += 1
        cn = f"tallied_{i}" if ntally > 1 else "tallied"
        ctes.append((cn, "tally", d))
        STATS["joins"] += 1
        hint_line = ""
        if tally_hint and i == 0:
            hint_line = f"\n        OPTIONS (AGGREGATE INPUT GROUP SIZE = {tally_hint})"
            STATS["hints"] += 1
        fl = ""
        if filters:
            fparts = []
            for fi in range(filters):
                fparts.append(
                    f"            pg_catalog.count(*) FILTER (WHERE c.mark_kind = 'm{fi % 4}') AS n_k{fi},")
                STATS["filters"] += 1
            fl = "\n" + "\n".join(fparts)
        STATS["filters"] += 1
        dim_join = ""
        dim_agg = ""
        if i % 2 == 0:
            STATS["joins"] += 1
            dim_join = f"""
        JOIN {q('depots')} AS td
            ON td.depot_id = o.depot_id"""
            dim_agg = """
            pg_catalog.max(td.dock_count) AS v_dock,
            pg_catalog.bool_or(td.is_247) AS v_247,"""
        body.append(f"""    {cn} AS (
        SELECT
            o.delivery_id AS anchor_id,{fl}{dim_agg}
            pg_catalog.sum(c.mark_units)::pg_catalog.float8 AS v_sum,
            pg_catalog.avg(c.mark_units)::pg_catalog.float8 AS v_avg,
            pg_catalog.min(c.noted_at) AS v_first_at,
            pg_catalog.max(c.noted_at) AS v_last_at,
            pg_catalog.count(*) FILTER
                (WHERE c.mark_phase = 'failed') AS v_bad_n,
            pg_catalog.count(*) > 0 AS v_any
        FROM {q(SPINE)} AS o
        JOIN {q(d)} AS c
            ON c.{_jc(d)} = o.{_jc(d)}{dim_join}
        GROUP BY o.delivery_id{hint_line}
    )""")
    emit(",\n".join(body))
    outcols = ["o.delivery_id AS anchor_id"]
    exported = [("anchor_id", "key")]
    def outp(expr_fn, kind):
        nm = feat_name()
        outcols.append(expr_fn(nm))
        exported.append((nm, kind))
    for cn, kind, _ in ctes:
        if kind == "pick":
            outp(lambda nm: CO(f"{cn}.mark_kind", "''", nm), "pick_kind")
            outp(lambda nm: CO(f"{cn}.mark_units", "0.0", nm), "pick_units")
            outp(lambda nm: CO(f"{cn}.noted_at", "o.created_at", nm),
                 "pick_at")
        elif kind == "mark":
            outp(lambda nm: CO(f"{cn}.has_bad", "false", nm), "mark_flag")
            def label(nm, cn=cn):
                STATS["coalesce"] += 1
                return f"""CASE
        WHEN NOT COALESCE({cn}.has_kind, false) THEN 'none'
        WHEN o.phase = 'canceled' THEN 'late'
        ELSE 'live'
    END AS {nm}"""
            outp(label, "mark_label")
            outp(lambda nm: CO(f"{cn}.n_marks", "0", nm), "mark_n")
        elif kind == "mark2":
            pass
        else:
            outp(lambda nm: CO(f"{cn}.v_sum", "0.0", nm), "tally_sum")
            outp(lambda nm: CO(f"{cn}.v_avg", "0.0", nm), "tally_avg")
            outp(lambda nm, cn=cn:
                 f"""pg_catalog.extract('epoch',
        o.created_at - COALESCE({cn}.v_first_at, o.created_at))
        ::pg_catalog.float8 AS {nm}""", "tally_age")
            outp(lambda nm, cn=cn:
                 f"""pg_catalog.extract('epoch',
        COALESCE({cn}.v_last_at, o.created_at)
            - COALESCE({cn}.v_first_at, o.created_at))
        ::pg_catalog.float8 AS {nm}""", "tally_span")
            outp(lambda nm: CO(f"{cn}.v_bad_n", "0", nm), "tally_bad")
            outp(lambda nm: CO(f"{cn}.v_any", "false", nm), "tally_any")
            if filters:
                for fi in range(filters):
                    outp(lambda nm, cn=cn, fi=fi:
                         CO(f"{cn}.n_k{fi}", "0", nm), "tally_f")
    if consume_ident:
        outcols.append("id.ident_risk_band")
        exported.append(("ident_risk_band", "ident_band"))
        outp(lambda nm: CO("id.ident_dev_shared", "false", nm), "ident_flag")
    if consume_cour:
        outp(lambda nm: CO("cw.rank_grade", "0", nm), "cour_grade")
        outp(lambda nm: CO("cw.region_code = o.region_code", "false", nm),
             "cour_region_match")
        outp(lambda nm, _n=name: f"""pg_catalog.extract('epoch',
        o.created_at - COALESCE(cw.joined_at, o.created_at))
        ::pg_catalog.float8 AS {nm}""", "cour_tenure")
    for fi in range(extra_feats):
        src = rng.choice(["o.load_units", "o.risk_score"])
        style = fi % 3
        if style == 0:
            outp(lambda nm, src=src: f"""CASE
        WHEN {src} > 50.0 THEN 'heavy'
        WHEN {src} > 10.0 THEN 'mid'
        ELSE 'light'
    END AS {nm}""", "extra")
        elif style == 1:
            outp(lambda nm, src=src: f"""COALESCE(
        NULLIF({src}, 0.0),
        -1.0)::pg_catalog.float8 AS {nm}""", "extra")
        else:
            outp(lambda nm, src=src:
                 f"({src} * 100.0)::pg_catalog.float8 AS {nm}", "extra")
    emit("SELECT")
    emit(sel_lines(outcols))
    emit(f"FROM {q(SPINE)} AS o")
    for cn, _, _ in ctes:
        emit(J("LEFT", cn, cn + "_x", f"o.delivery_id = {cn}_x.anchor_id")
             .replace(f" AS {cn}_x", "").replace(f"{cn}_x.", f"{cn}."))
    if consume_ident:
        emit(J("LEFT", q(IDENT), "id", "o.delivery_id = id.anchor_id"))
    if consume_cour:
        emit(J("LEFT", q(COURW), "cw", "o.courier_id = cw.courier_id"))
    OUT[-1] = OUT[-1] + ";"
    emit()
    VIEW_COLS[name] = exported

def vcol(view, kind, idx=0):
    """Name of the idx-th exported column of `view` with the given kind."""
    hits = [n for n, k in VIEW_COLS[view] if k == kind]
    return hits[idx]

# 1-4: small chains for the wide MV (P6)
std_enrichment(f"{P}_{T2}_scan_trail", ["scans", "photo_logs"], npick=1,
               nmark=2, ntally=2, pick_hint=(64 if REF else 65536))                # c6a oversized (true ~40)
std_enrichment(f"{P}_{T2}_hold_flags",
               ["holds", "dock_slots", "depot_queues"], npick=1,
               nmark=2, ntally=2)
std_enrichment(f"{P}_{T2}_claim_totals", ["claims", "manifests"], npick=1,
               nmark=2, ntally=2, tally_hint=(16 if REF else 4096))                 # c6b oversized (true ~12)
std_enrichment(f"{P}_{T2}_rating_pick", ["ratings", "signatures"], npick=1,
               nmark=2, ntally=2, pick_hint=256)                   # correct (true ~150)

# 5: C5a jsonb view (22 ->> extractions + consumed passthrough)
def gw_view(name, kind_val, n_extract, mixed, consumed_note, keep_blob=True):
    """jsonb enrichment view. Baseline: extraction AFTER the pick, full-blob
    passthrough rides log_rows + the pick ladder. Reference: extract-in-place
    (fields computed in log_rows, payload dropped from the pipeline); the
    consumed passthrough (keep_blob) is recovered by ONE fetch-back join on
    the unique call_id; the unconsumed one (C5b) is dropped outright.
    Output column names are identical across modes (grading depends on it)."""
    # extraction spec: (alias, baseline_expr_on_b_payload, logrows_expr_on_g)
    nnum = min(n_extract // 2 + 1, len(BLOB_NUM_KEYS))
    ntxt = min(n_extract - nnum, len(BLOB_TXT_KEYS))
    specs = []
    for i in range(nnum):
        k = BLOB_NUM_KEYS[i]
        if mixed and i % 3 == 2:
            e = "(payload -> 'nest_geo' ->> 'cell')::pg_catalog.float8"
        else:
            e = f"(payload ->> '{k}')::pg_catalog.float8"
        specs.append((f"feat_{k}", e, "-1.0"))
    for i in range(ntxt):
        k = BLOB_TXT_KEYS[i]
        if mixed and i % 3 == 1:
            specs.append((f"feat_{k}_src",
                          "payload -> 'nest_meta' ->> 'src'", "''"))
        else:
            specs.append((f"feat_{k}", f"payload ->> '{k}'", "''"))
    specs.append(("feat_ok_flag",
                  "(payload ->> 'k_ok')::pg_catalog.bool", "false"))

    view_open(name)
    emit("WITH")
    STATS["joins"] += 2
    STATS["picks"] += 1
    STATS["hints"] += 1
    if REF:
        lr_cols = ["o.delivery_id AS anchor_id", "g.call_id", "g.seq",
                   "g.valid_flag", "g.grade"]
        lr_cols += [f"{e.replace('payload', 'g.payload')} AS x_{a}"
                    for a, e, _ in specs]
        best_cols = ["anchor_id", "call_id", "grade"] +                     [f"x_{a}" for a, _, _ in specs]
    else:
        lr_cols = ["o.delivery_id AS anchor_id", "g.call_id", "g.seq",
                   "g.valid_flag", "g.grade", "g.payload"]
        best_cols = ["anchor_id", "call_id", "grade", "payload"]
    emit("    log_rows AS (")
    emit("        SELECT")
    emit(sel_lines(lr_cols, indent=12))
    emit(f"""        FROM {q(SPINE)} AS o
        JOIN {q(GWW)} AS g
            ON g.delivery_id = o.delivery_id
            AND g.call_kind = '{kind_val}'
    ),
    any_valid AS (
        SELECT
            anchor_id,
            pg_catalog.bool_or(valid_flag) AS ok_any,
            pg_catalog.count(*) AS n_calls
        FROM log_rows
        GROUP BY anchor_id
    ),
    best AS (
        SELECT DISTINCT ON (anchor_id)""")
    emit(sel_lines(best_cols, indent=12))
    emit("""        FROM log_rows
        WHERE valid_flag
        OPTIONS (DISTINCT ON INPUT GROUP SIZE = 2048)
        ORDER BY
            anchor_id,
            seq DESC
    )""")
    outcols = [
        "o.delivery_id AS anchor_id",
        """CASE
        WHEN av.ok_any IS NULL THEN 'no_call'
        WHEN NOT av.ok_any THEN 'all_failed'
        WHEN b.grade >= 70.0 THEN 'strong_pass'
        WHEN b.grade >= 40.0 THEN 'weak_pass'
        ELSE 'reject'
    END AS """ + feat_name(),
        CO("b.grade::pg_catalog.float8", "-1.0", feat_name()),
        CO("av.n_calls", "0", feat_name()),
    ]
    if REF:
        if keep_blob:
            outcols.append(CO("fb.payload", "'{}'::pg_catalog.jsonb",
                              "raw_payload"))
        for a, _, d in specs[:-1]:
            outcols.append(CO(f"b.x_{a}", d, a))
    else:
        outcols.append(CO("b.payload", "'{}'::pg_catalog.jsonb",
                          "raw_payload"))
        for a, e, d in specs[:-1]:
            outcols.append(CO(e.replace("payload", "b.payload"), d, a))
    last_a, last_e, last_d = specs[-1]
    if REF:
        outcols.append(CO(f"b.x_{last_a}", last_d, feat_name()))
    else:
        outcols.append(CO(last_e.replace("payload", "b.payload"), last_d,
                          feat_name()))
    emit("SELECT")
    emit(sel_lines(outcols))
    emit(f"FROM {q(SPINE)} AS o")
    emit(J("LEFT", "any_valid", "av", "o.delivery_id = av.anchor_id"))
    emit(J("LEFT", "best", "b", "o.delivery_id = b.anchor_id"))
    if REF and keep_blob:
        emit(J("LEFT", q(GWW), "fb", "fb.call_id = b.call_id"))
    OUT[-1] = OUT[-1] + ";"
    emit(f"-- {consumed_note}")
    emit()

gw_view(f"{P}_{T2}_gw_outcome", "quote", 22, mixed=False,
        consumed_note="", keep_blob=True)                                          # C5a
gw_view(f"{P}_{T2}_gw_probe", "verify", 13, mixed=True,
        consumed_note="", keep_blob=False)                                          # C5b

# 7: C7 leave-alone window rescan (ratio ~1.1)
view_open(f"{P}_{T2}_route_flux")
STATS["joins"] += 1
emit(f"""SELECT
    o.delivery_id AS anchor_id,
    pg_catalog.count(*) AS n_delays,
    pg_catalog.max(dl.mark_units)::pg_catalog.float8 AS worst_delay,
    pg_catalog.min(dl.noted_at) AS first_delay_at
FROM {q(SPINE)} AS o
JOIN {q('delay_logs')} AS dl
    ON dl.delivery_id = o.delivery_id
    AND dl.noted_at <= o.created_at
    AND dl.noted_at > o.created_at - INTERVAL '15 minutes'
GROUP BY o.delivery_id;""")
emit()

# 8-16: more chains
std_enrichment(f"{P}_{T2}_refuel_stats", ["refuel_stops", "badge_scans"],
               npick=1, nmark=2, ntally=3, extra_feats=8, consume_cour=True)
std_enrichment(f"{P}_{T2}_damage_marks", ["damage_reports", "weight_checks"],
               npick=2, nmark=2, ntally=2, extra_feats=8, consume_cour=True)
std_enrichment(f"{P}_{T2}_toll_totals", ["toll_events", "curfew_windows"],
               npick=1, nmark=2, ntally=3, filters=2, extra_feats=8)

# delay_bands: C10b, grouped over spine LEFT JOIN detail => total per anchor
view_open(f"{P}_{T2}_delay_bands")
STATS["joins"] += 1
STATS["left"] += 1
STATS["filters"] += 2
STATS["coalesce"] += 1
emit(f"""SELECT
    o.delivery_id AS anchor_id,
    pg_catalog.count(dl.delay_log_id) AS n_delay_rows,
    pg_catalog.count(*) FILTER (WHERE dl.mark_phase = 'failed') AS n_delay_bad,
    pg_catalog.count(*) FILTER (WHERE dl.mark_units > 20.0) AS n_delay_big,
    CASE
        WHEN pg_catalog.count(dl.delay_log_id) = 0 THEN 'clean'
        WHEN pg_catalog.count(*) FILTER (WHERE dl.mark_units > 20.0) > 2
            THEN 'rough'
        ELSE 'minor'
    END AS delay_band
FROM {q(SPINE)} AS o
LEFT JOIN {q('delay_logs')} AS dl
    ON dl.delivery_id = o.delivery_id
GROUP BY o.delivery_id;""")
emit()

std_enrichment(f"{P}_{T2}_handoff_pick", ["handoffs", "photo_logs"], npick=2,
               nmark=1, ntally=2, pick_hint=64)                    # correct (true ~40)
std_enrichment(f"{P}_{T2}_addr_checks", ["address_checks", "signatures"],
               npick=2, nmark=2, ntally=2, consume_ident=True)
std_enrichment(f"{P}_{T2}_seal_flags", ["seal_events", "dock_slots"],
               npick=1, nmark=2, ntally=2)
std_enrichment(f"{P}_{T2}_permit_pick", ["permit_grants", "manifests"],
               npick=2, nmark=2, ntally=2, consume_ident=True)
std_enrichment(f"{P}_{T2}_return_totals", ["return_runs", "support_tickets"],
               npick=1, nmark=2, ntally=2, pick_hint=256, extra_feats=8)          # correct (true ~120)

# 17: extreme #1, dispute_marks (11 CTEs, ~18 joins) with c6c oversized hint
std_enrichment(f"{P}_{T2}_dispute_marks",
               ["dispute_cases", "support_tickets", "callback_logs",
                "weight_checks", "manifests", "dock_slots"],
               npick=4, nmark=5, ntally=5, extra_feats=24,
               tally_hint=(64 if REF else 65536), filters=3, consume_cour=True)                        # c6c oversized (true ~30)

# 18: extreme #2, shift_mix (20 CTEs, ~32 joins incl. a K2 lane CTE) c6e
view_open(f"{P}_{T2}_shift_mix")
emit("WITH")
parts = []
for i in range(24):
    d = ["badge_scans", "shift_logs", "bonus_grants", "penalty_marks",
         "training_flags", "curfew_windows", "refuel_stops", "photo_logs"][i % 8]
    kcol = "courier_id" if d in ("shift_logs", "badge_scans", "bonus_grants",
                                 "penalty_marks", "training_flags",
                                 "curfew_windows", "refuel_stops") else "delivery_id"
    ocol = "courier_id" if kcol == "courier_id" else "delivery_id"
    STATS["joins"] += 1
    if i % 4 == 0:
        STATS["picks"] += 1
        STATS["hints"] += 1
        parts.append(f"""    sx_{i} AS (
        SELECT DISTINCT ON (o.delivery_id)
            o.delivery_id AS anchor_id,
            d.mark_kind AS k_{i},
            d.mark_units AS u_{i}
        FROM {q(SPINE)} AS o
        JOIN {q(d)} AS d
            ON d.{kcol} = o.{ocol}
        OPTIONS (DISTINCT ON INPUT GROUP SIZE = 256)
        ORDER BY
            o.delivery_id,
            d.noted_at DESC
    )""")
    else:
        hint = ""
        if i == 1:
            # c6e: 256 UNDERSIZED (true per-courier group ~4k for shift_logs)
            hint = ("\n        OPTIONS (AGGREGATE INPUT GROUP SIZE = 8192)"
                    if REF else
                    "\n        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)")
            STATS["hints"] += 1
        fparts = []
        for fi in range(1 if i % 3 else 2):
            STATS["filters"] += 1
            fparts.append(f"            pg_catalog.count(*) FILTER (WHERE d.mark_phase = 'failed') AS f_{i}_{fi},")
        parts.append(f"""    sx_{i} AS (
        SELECT
            o.delivery_id AS anchor_id,
{chr(10).join(fparts)}
            pg_catalog.sum(d.mark_units)::pg_catalog.float8 AS u_{i},
            pg_catalog.count(*) AS n_{i}
        FROM {q(SPINE)} AS o
        JOIN {q(d)} AS d
            ON d.{kcol} = o.{ocol}
        GROUP BY o.delivery_id{hint}
    )""")
# K2 lane CTE (C1/K2 member inside P8's dataflow)
STATS["joins"] += 1
STATS["hints"] += 1
parts.append(f"""    lane_hist AS (
        SELECT
            o.delivery_id AS anchor_id,
            pg_catalog.count(*) AS lane_n,
            pg_catalog.sum(h.load_units)::pg_catalog.float8 AS lane_load,
            pg_catalog.max(h.created_at) AS lane_last
        FROM {q(SPINE)} AS o
        JOIN {q(HB_LANE)} AS h
            ON h.courier_id = o.courier_id
            AND h.lane_code = o.lane_code
            AND h.created_at < o.created_at
        GROUP BY o.delivery_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    )""")
STATS["joins"] += 2
parts.append(f"""    idflag AS (
        SELECT
            i.anchor_id,
            i.ident_risk_band,
            i.ident_loan_open
        FROM {q(IDENT)} AS i
    ),
    courattr AS (
        SELECT
            o.delivery_id AS anchor_id,
            cw.rank_grade,
            cw.lane_pref = o.lane_code AS lane_pref_match
        FROM {q(SPINE)} AS o
        JOIN {q(COURW)} AS cw
            ON cw.courier_id = o.courier_id
    ),
    mixbase AS (
        SELECT
            o.delivery_id AS anchor_id,
            o.courier_id,
            o.load_units,
            o.phase
        FROM {q(SPINE)} AS o
    )""")
emit(",\n".join(parts))
outcols = ["mb.anchor_id"]
for i in range(24):
    if i % 4 == 0:
        outcols.append(CO(f"sx_{i}.k_{i}", "''", feat_name()))
        outcols.append(CO(f"sx_{i}.u_{i}", "0.0", feat_name()))
    else:
        outcols.append(CO(f"sx_{i}.u_{i}", "0.0", feat_name()))
        outcols.append(CO(f"sx_{i}.n_{i}", "0", feat_name()))
        outcols.append(CO(f"sx_{i}.f_{i}_0", "0", feat_name()))
outcols.append(CO("lh.lane_n", "0", feat_name()))
outcols.append(CO("lh.lane_load", "0.0", feat_name()))
outcols.append(CO("idf.ident_risk_band", "'clear'", feat_name()))
outcols.append(CO("ca.rank_grade", "0", feat_name()))
outcols.append(CO("ca.lane_pref_match", "false", feat_name()))
emit("SELECT")
emit(sel_lines(outcols))
emit("FROM mixbase AS mb")
for i in range(24):
    emit(J("LEFT", f"sx_{i}", f"sx{i}", f"mb.anchor_id = sx{i}.anchor_id")
         .replace(f" AS sx{i}", "").replace(f"sx{i}.", f"sx_{i}."))
emit(J("LEFT", "lane_hist", "lh", "mb.anchor_id = lh.anchor_id"))
emit(J("LEFT", "courattr", "ca", "mb.anchor_id = ca.anchor_id"))
emit(J("LEFT", "idflag", "idf", "mb.anchor_id = idf.anchor_id") + ";")
emit()

# 19: C9 consumer, alt_ref history share (spine-driven, planner pushes
# IS NOT NULL below the private arrangement at baseline)
view_open(f"{P}_{T2}_alt_share")
STATS["joins"] += 1
emit(f"""SELECT
    o.delivery_id AS anchor_id,
    pg_catalog.count(*) AS alt_n,
    pg_catalog.count(DISTINCT h.courier_id) AS alt_couriers,
    pg_catalog.bool_or(h.courier_id <> o.courier_id) AS alt_foreign,
    pg_catalog.max(h.created_at) AS alt_last
FROM {q(SPINE)} AS o
JOIN {q(HB_ALT)} AS h
    ON h.alt_ref = o.alt_ref
    AND h.delivery_id <> o.delivery_id
GROUP BY o.delivery_id;""")
emit()

# ==================================================================
# Window tier (T5 instances, dsp_roll_*)
# ==================================================================
emit("-- ============ window views ============")
emit()

def pivot_filters(n, alias="h", oalias="o", stride=1):
    """Return n FILTER-conditioned aggregate column strings.

    `stride` walks the condition list in steps rather than in order, so a site
    that takes only a few conditions still touches several history columns.
    That column spread is what fixes the width of the history arrangement the
    site builds (the modeled arrangements sit at 26-87 bytes/row)."""
    conds = [
        f"{alias}.phase = 'completed'",
        f"{alias}.phase = 'failed'",
        f"{alias}.phase = 'canceled'",
        f"{alias}.phase = 'completed' AND {alias}.created_at > {oalias}.created_at - INTERVAL '2 days'",
        f"{alias}.phase = 'completed' AND {alias}.created_at >= {oalias}.created_at - INTERVAL '1 hour'",
        f"{alias}.phase = 'failed' AND {alias}.created_at > {oalias}.created_at - INTERVAL '7 days'",
        f"{alias}.created_at > {oalias}.created_at - INTERVAL '30 days'",
        f"{alias}.created_at > {oalias}.created_at - INTERVAL '90 days'",
        f"{alias}.load_units > 75.0",
        f"{alias}.service_tier = {oalias}.service_tier",
        f"{alias}.lane_code = {oalias}.lane_code",
        f"{alias}.delivery_id <> {oalias}.delivery_id AND {alias}.phase = 'completed'",
        f"{alias}.promo_code IS NOT NULL",
        f"{alias}.source_app = {oalias}.source_app",
        f"{alias}.created_at > {oalias}.created_at - INTERVAL '1 day'",
        f"{alias}.phase = 'on_hold'",
        f"{alias}.region_code = {oalias}.region_code",
        f"{alias}.load_units > {oalias}.load_units",
        f"{alias}.created_at > {oalias}.created_at - INTERVAL '14 days'",
        f"{alias}.phase = 'completed' AND {alias}.load_units > 50.0",
        f"{alias}.device_id IS NOT NULL",
    ]
    aggs = []
    for i in range(n):
        c = conds[(i * stride) % len(conds)]
        kind = ["pg_catalog.count(*)",
                f"pg_catalog.sum({alias}.load_units)",
                f"pg_catalog.max({alias}.load_units)",
                f"pg_catalog.min({alias}.load_units)"][i % 4]
        base = FILT(kind, c)
        if i % 4 in (1, 2, 3):
            aggs.append(
                f"COALESCE({base}, 0)::pg_catalog.float8 AS {feat_name()}")
            STATS["coalesce"] += 1
        else:
            aggs.append(f"{base} AS {feat_name()}")
    return aggs

# W1: K1 depot-history pivot (P2)
view_open(f"{P}_{T3}_depot_history")
STATS["joins"] += 1
STATS["hints"] += 1
cols = ["o.delivery_id AS anchor_id",
        "pg_catalog.count(*) + 1 AS n_all",
        """(COALESCE(pg_catalog.sum(h.load_units), 0)
        + o.load_units)::pg_catalog.float8 AS v_total"""]
STATS["coalesce"] += 1
cols += pivot_filters(10, stride=13)
cols.append("""COALESCE(pg_catalog.extract('epoch',
        o.created_at - pg_catalog.max(h.created_at)),
        0.0)::pg_catalog.float8 AS s_last""")
STATS["coalesce"] += 1
cols.append("""COALESCE(pg_catalog.extract('epoch',
        o.created_at - pg_catalog.max(h.created_at)
            FILTER (WHERE h.phase = 'failed')),
        9999.0 * 86400.0)::pg_catalog.float8 AS s_last_bad""")
STATS["coalesce"] += 1
STATS["filters"] += 1
cols.append("""COALESCE(pg_catalog.extract('epoch',
        o.created_at - pg_catalog.min(h.created_at)),
        0.0)::pg_catalog.float8 AS s_first""")
cols.append("""((COALESCE(pg_catalog.sum(h.load_units), 0)
        + o.load_units)
     / (pg_catalog.count(*) + 1))::pg_catalog.float8 AS run_avg_load""")
cols.append("""CASE
        WHEN pg_catalog.count(*) = 0 THEN 'first_here'
        WHEN pg_catalog.min(h.created_at)
            >= o.created_at - INTERVAL '5 days' THEN 'recent_pair'
        ELSE 'seasoned_pair'
    END AS pair_age_band""")
cols.append("""(pg_catalog.count(DISTINCT h.lane_code) > 2)
        AS multi_lane_pair""")
cols.append("""pg_catalog.count(*) FILTER (WHERE hd.is_247)
        AS pair_n_always_open""")
cols.append("""pg_catalog.count(*) FILTER (WHERE hd.depot_kind = 'hub')
        AS pair_n_hub""")
STATS["filters"] += 2
STATS["joins"] += 1
STATS["coalesce"] += 3
emit("SELECT")
emit(sel_lines(cols))
emit(f"FROM {q(SPINE)} AS o")
emit(f"""JOIN {q(HB_DEPOT)} AS h
    ON h.courier_id = o.courier_id
    AND h.depot_id = o.depot_id
    AND h.created_at < o.created_at
JOIN {q(DEPOTW)} AS hd
    ON hd.depot_id = h.depot_id""")
emit("GROUP BY")
emit(sel_lines(["o.delivery_id", "o.created_at", "o.load_units",
                "o.service_tier", "o.lane_code", "o.source_app",
                "o.region_code", "o.delivery_id", "o.promo_code",
                "o.device_id"][:7]))
emit("OPTIONS (AGGREGATE INPUT GROUP SIZE = 64);")
emit()

# W2: K1 most-recent-prior pick (P2)
view_open(f"{P}_{T3}_depot_recency")
STATS["joins"] += 1
STATS["picks"] += 1
STATS["hints"] += 1
emit(f"""SELECT DISTINCT ON (o.delivery_id)
    o.delivery_id AS anchor_id,
    h.phase AS prev_phase,
    h.created_at AS prev_at,
    h.load_units AS prev_load,
    h.service_tier AS prev_tier
FROM {q(SPINE)} AS o
JOIN {q(HB_DEPOT)} AS h
    ON h.courier_id = o.courier_id
    AND h.depot_id = o.depot_id
    AND h.created_at < o.created_at
OPTIONS (DISTINCT ON INPUT GROUP SIZE = 64)
ORDER BY
    o.delivery_id,
    h.created_at DESC,
    h.delivery_id DESC;""")
emit()

# W3: K1 moment sketch (P3); consumes W2 for fallback ts (tier3->tier3 edge)
view_open(f"{P}_{T3}_depot_moment")
STATS["joins"] += 2
STATS["left"] += 1
STATS["hints"] += 1
emit(f"""WITH sk AS (
    SELECT
        o.delivery_id AS anchor_id,
        pg_catalog.count(*) AS n_rows,
        pg_catalog.sum(h.load_units) AS sum_v,
        pg_catalog.sum(h.load_units * h.load_units) AS sum_sq
    FROM {q(SPINE)} AS o
    JOIN {q(HB_DEPOT)} AS h
        ON h.courier_id = o.courier_id
        AND h.depot_id = o.depot_id
        AND h.created_at < o.created_at
    GROUP BY o.delivery_id
    OPTIONS (AGGREGATE INPUT GROUP SIZE = 64)
)
SELECT
    o.delivery_id AS anchor_id,
    ((COALESCE(sk.sum_v, 0) + o.load_units)
        / (COALESCE(sk.n_rows, 0) + 1))::pg_catalog.float8
        AS run_mean,
    pg_catalog.sqrt(GREATEST(
        (COALESCE(sk.sum_sq, 0)
            + o.load_units * o.load_units
            - pg_catalog.power(
                COALESCE(sk.sum_v, 0) + o.load_units, 2)
                / (COALESCE(sk.n_rows, 0) + 1))
        / (COALESCE(sk.n_rows, 0) + 1),
        0.0))::pg_catalog.float8 AS run_std,
    COALESCE(r.prev_at, o.created_at) AS moment_anchor_at
FROM {q(SPINE)} AS o
LEFT JOIN sk
    ON o.delivery_id = sk.anchor_id
LEFT JOIN {q(f"{P}_{T3}_depot_recency")} AS r
    ON o.delivery_id = r.anchor_id;""")
STATS["coalesce"] += 7
emit()

# W4: K2 lane pivot (P4)
view_open(f"{P}_{T3}_lane_history")
STATS["joins"] += 1
STATS["hints"] += 1
cols = ["o.delivery_id AS anchor_id",
        "pg_catalog.count(*) + 1 AS lane_n_all"]
cols += pivot_filters(7, stride=11)
cols.append("""(CASE WHEN pg_catalog.count(*) FILTER (WHERE h.phase = 'completed') = 0
          THEN 0.0
          ELSE (pg_catalog.count(*) FILTER (WHERE h.phase = 'completed') + 1)
               / (pg_catalog.extract('epoch', o.created_at
                    - pg_catalog.min(h.created_at)
                        FILTER (WHERE h.phase = 'completed'))
                  / 60.0)
     END)::pg_catalog.float8 AS per_min_rate""")
STATS["filters"] += 3
cols.append("(pg_catalog.count(*) FILTER (WHERE h.delivery_id <> o.delivery_id) = 0) AS is_first_ever")
STATS["filters"] += 1
cols.append("""COALESCE(pg_catalog.extract('epoch',
        o.created_at - pg_catalog.max(h.created_at)),
        0.0)::pg_catalog.float8 AS lane_s_last""")
cols.append("""((COALESCE(pg_catalog.sum(h.load_units), 0)
        + o.load_units)
     / (pg_catalog.count(*) + 1))::pg_catalog.float8 AS lane_avg_load""")
cols.append("""CASE
        WHEN pg_catalog.count(*) = 0 THEN 'lane_new'
        WHEN pg_catalog.count(*) > 40 THEN 'lane_heavy'
        ELSE 'lane_mid'
    END AS lane_use_band""")
cols.append("""(pg_catalog.count(DISTINCT h.depot_id) > 3)
        AS lane_multi_depot""")
cols.append("""pg_catalog.count(*) FILTER (WHERE hd.dock_count > 8)
        AS lane_n_big_dock""")
cols.append("""pg_catalog.count(*) FILTER (WHERE hd.depot_kind = 'locker')
        AS lane_n_locker""")
STATS["filters"] += 2
STATS["joins"] += 1
STATS["coalesce"] += 2
emit("SELECT")
emit(sel_lines(cols))
emit(f"FROM {q(SPINE)} AS o")
emit(f"""JOIN {q(HB_LANE)} AS h
    ON h.courier_id = o.courier_id
    AND h.lane_code = o.lane_code
    AND h.created_at < o.created_at
JOIN {q(DEPOTW)} AS hd
    ON hd.depot_id = h.depot_id""")
emit("GROUP BY")
emit(sel_lines(["o.delivery_id", "o.created_at", "o.load_units",
                "o.service_tier", "o.lane_code", "o.source_app",
                "o.region_code"]))
emit("OPTIONS (AGGREGATE INPUT GROUP SIZE = 128);")
emit()

# W5: K2 lane first-use, C10a (grouped over spine LEFT JOIN => total)
view_open(f"{P}_{T3}_lane_first")
STATS["joins"] += 1
STATS["left"] += 1
STATS["hints"] += 1
STATS["coalesce"] += 2
emit(f"""SELECT
    o.delivery_id AS anchor_id,
    pg_catalog.extract('epoch',
        o.created_at - COALESCE(
            pg_catalog.min(h.created_at),
            o.created_at))::pg_catalog.float8 AS s_since_first_lane,
    pg_catalog.count(h.delivery_id) AS lane_prior_n,
    COALESCE(
        pg_catalog.max(h.load_units),
        0.0)::pg_catalog.float8 AS lane_max_load
FROM {q(SPINE)} AS o
LEFT JOIN {q(HB_LANE)} AS h
    ON h.courier_id = o.courier_id
    AND h.lane_code = o.lane_code
    AND h.created_at < o.created_at
GROUP BY
    o.delivery_id,
    o.created_at
OPTIONS (AGGREGATE INPUT GROUP SIZE = 128);""")
emit()

# W6: C8, the 21-FILTER pivot over PAIRS (estimate-only target)
view_open(f"{P}_{T3}_owner_pulse")
STATS["joins"] += 2
STATS["hints"] += 1
cols = ["o.delivery_id AS anchor_id",
        "pg_catalog.count(*) + 1 AS pulse_n_all",
        """(COALESCE(pg_catalog.sum(h.load_units), 0)
        + o.load_units)::pg_catalog.float8 AS pulse_total"""]
STATS["coalesce"] += 1
cols += pivot_filters(21)
cols.append("""COALESCE(pg_catalog.extract('epoch',
        o.created_at - pg_catalog.max(h.created_at)),
        0.0)::pg_catalog.float8 AS pulse_s_last""")
STATS["coalesce"] += 1
emit("SELECT")
emit(sel_lines(cols))
emit(f"FROM {q(SPINE)} AS o")
emit(f"""JOIN {q(PAIRS)} AS pp
    ON pp.anchor_id = o.delivery_id""")
emit(f"""JOIN {q(FACTW)} AS h
    ON h.delivery_id = pp.prior_id""")
emit("GROUP BY")
emit(sel_lines(["o.delivery_id", "o.created_at", "o.load_units",
                "o.service_tier", "o.lane_code", "o.source_app",
                "o.region_code", "o.promo_code", "o.device_id"]))
emit("OPTIONS (AGGREGATE INPUT GROUP SIZE = 64);")
emit()

# W7: the LATERAL earliest-K over K1-composite history (P8)
view_open(f"{P}_{T3}_owner_top3")
STATS["joins"] += 2
STATS["hints"] += 1
emit(f"""WITH grp AS (
    SELECT
        o.delivery_id AS anchor_id,
        o.courier_id,
        o.depot_id,
        o.created_at
    FROM {q(SPINE)} AS o
)
SELECT
    grp.anchor_id,
    GREATEST(pg_catalog.max(l.load_units), 0.0)
        ::pg_catalog.float8 AS top3_max_load,
    pg_catalog.min(l.created_at) AS top3_first_at,
    pg_catalog.count(*) AS top3_n
FROM grp,
    LATERAL (
        SELECT
            h.load_units,
            h.created_at
        FROM {q(HB_DEPOT)} AS h
        WHERE h.courier_id = grp.courier_id
          AND h.depot_id = grp.depot_id
          AND h.created_at < grp.created_at
        OPTIONS (LIMIT INPUT GROUP SIZE = 64)
        ORDER BY
            h.created_at ASC,
            h.delivery_id ASC
        LIMIT 3
    ) AS l
GROUP BY grp.anchor_id;""")
emit()

# W8: owner-history reduce; 65536 correct + c6f UN-hinted big ladder
C6F_HINT = ("\n    OPTIONS (AGGREGATE INPUT GROUP SIZE = 16384)"
            if REF else "")
view_open(f"{P}_{T3}_owner_tally")
STATS["joins"] += 3
STATS["left"] += 2
STATS["hints"] += 1
STATS["coalesce"] += 4
emit(f"""WITH per_owner AS (
    SELECT
        h.courier_id,
        pg_catalog.count(*) AS own_n,
        pg_catalog.sum(h.load_units)::pg_catalog.float8 AS own_load,
        pg_catalog.count(*) FILTER (WHERE h.phase = 'failed') AS own_bad
    FROM {q(FACTW)} AS h
    GROUP BY h.courier_id
    OPTIONS (AGGREGATE INPUT GROUP SIZE = 65536)
),
own_extremes AS (
    SELECT
        h.courier_id,
        pg_catalog.min(h.created_at) AS own_first_at,
        pg_catalog.max(h.load_units) AS own_peak_load
    FROM {q(FACTW)} AS h
    WHERE h.created_at > TIMESTAMP '{BUILD_TS}' - INTERVAL '30 days'
    GROUP BY h.courier_id{C6F_HINT}
)
SELECT
    o.delivery_id AS anchor_id,
    COALESCE(po.own_n, 0) AS owner_lifetime_n,
    COALESCE(po.own_load, 0.0) AS owner_lifetime_load,
    COALESCE(po.own_bad, 0) AS owner_lifetime_bad,
    COALESCE(oe.own_peak_load, 0.0)::pg_catalog.float8
        AS owner_peak_load,
    pg_catalog.extract('epoch',
        o.created_at - COALESCE(oe.own_first_at, o.created_at))
        ::pg_catalog.float8 AS owner_tenure_s,
    CASE
        WHEN COALESCE(po.own_n, 0) = 0 THEN 'fresh'
        WHEN oe.own_first_at >= o.created_at - INTERVAL '5 days' THEN 'young'
        ELSE 'seasoned'
    END AS owner_age_band,
    COALESCE(cw.rank_grade, 0) AS owner_rank_grade,
    COALESCE(cw.region_code = o.region_code, false) AS owner_home_region
FROM {q(SPINE)} AS o
LEFT JOIN per_owner AS po
    ON po.courier_id = o.courier_id
LEFT JOIN own_extremes AS oe
    ON oe.courier_id = o.courier_id
LEFT JOIN {q(COURW)} AS cw
    ON cw.courier_id = o.courier_id;""")
STATS["filters"] += 1
emit()

# ==================================================================
# Mega-view (39 CTEs; hosts C4 + c6d twins)
# ==================================================================
emit("-- ============ mega view ============")
emit()
view_open(MEGA)
emit("WITH")
mega = []

# 1 alias import
mega.append(f"""    idv AS (
        SELECT *
        FROM {q(IDENT)}
    )""")
# 2 current-context: spine JOIN telem, WHERE valid (shrinks anchors ~15%)
STATS["joins"] += 1
mega.append(f"""    cur AS (
        SELECT
            o.delivery_id,
            o.courier_id,
            o.depot_id,
            o.created_at,
            o.phase,
            o.load_units,
            o.lane_code,
            o.service_tier,
            o.link_id,
            o.alt_ref,
            o.device_id
        FROM {q(SPINE)} AS o
        JOIN {q('route_pings')} AS rp
            ON rp.delivery_id = o.delivery_id
            AND rp.valid_flag
    )""")
# 3 history expansion (shared hub; R1 when shared correctly)
STATS["joins"] += 1
mega.append("""    hx AS (
        SELECT
            c.delivery_id AS anchor_id,
            c.created_at AS o_ts,
            c.load_units AS o_load,
            c.link_id AS o_link,
            k.delivery_id AS delivery_id2,
            k.created_at AS created_at2,
            k.phase AS phase2,
            k.load_units AS load_units2,
            k.match_key AS match_key2,
            k.axle_a AS axle_a2,
            k.axle_b AS axle_b2,
            k.asset_created AS asset_created2,
            k.is_alt_channel AS is_alt2
        FROM cur AS c
        JOIN """ + q(KEYSPINE) + """ AS k
            ON k.courier_id = c.courier_id
            AND k.created_at < c.created_at
            AND k.created_at >= c.created_at - INTERVAL '30 days'
    )""")
# 4 marker annotation
STATS["joins"] += 2
mega.append(f"""    own_key AS (
        SELECT
            c.delivery_id,
            k.match_key
        FROM cur AS c
        JOIN {q(KEYSPINE)} AS k
            ON k.delivery_id = c.delivery_id
    ),
    hxm AS (
        SELECT
            h.*,
            (h.match_key2 = ok.match_key) AS same_asset
        FROM hx AS h
        JOIN own_key AS ok
            ON ok.delivery_id = h.anchor_id
    )""")
# 5 C4: divergent-projection twin JOINS of hxm against idv (the CSE miss:
# same join, same key, divergent projections -> hxm arranged twice).
# Reference: ONE union-projection join (hist_j) + thin selects, so hxm and
# idv are arranged once; downstream CTE references stay unchanged.
if REF:
    STATS["joins"] += 1
    mega.append("""    hist_j AS (
        SELECT
            h.anchor_id,
            h.o_ts,
            h.created_at2,
            h.load_units2,
            h.match_key2,
            h.axle_a2,
            h.is_alt2,
            h.same_asset,
            h.phase2,
            i.ident_loan_open AS loan_open,
            i.ident_risk_band AS risk_band
        FROM hxm AS h
        JOIN idv AS i
            ON i.anchor_id = h.anchor_id
        WHERE h.phase2 <> 'canceled'
    ),
    hist_eff AS (
        SELECT
            anchor_id,
            o_ts,
            created_at2,
            load_units2,
            same_asset,
            phase2,
            loan_open
        FROM hist_j
    ),
    hist_cat AS (
        SELECT
            anchor_id,
            o_ts,
            created_at2,
            load_units2,
            match_key2,
            axle_a2,
            is_alt2,
            same_asset,
            risk_band
        FROM hist_j
    )""")
else:
    STATS["joins"] += 2
    mega.append("""    hist_eff AS (
        SELECT
            h.anchor_id,
            h.o_ts,
            h.created_at2,
            h.load_units2,
            h.same_asset,
            h.phase2,
            i.ident_loan_open AS loan_open
        FROM hxm AS h
        JOIN idv AS i
            ON i.anchor_id = h.anchor_id
        WHERE h.phase2 <> 'canceled'
    ),
    hist_cat AS (
        SELECT
            h.anchor_id,
            h.o_ts,
            h.created_at2,
            h.load_units2,
            h.match_key2,
            h.axle_a2,
            h.is_alt2,
            h.same_asset,
            i.ident_risk_band AS risk_band
        FROM hxm AS h
        JOIN idv AS i
            ON i.anchor_id = h.anchor_id
        WHERE h.phase2 <> 'canceled'
    )""")  # noqa: E122, else-branch of the C4 reference switch
# 5b current-vs-prior asset pair + dedup pick
STATS["joins"] += 2
STATS["picks"] += 1
STATS["hints"] += 1
mega.append(f"""    prior_assets AS (
        SELECT
            h.anchor_id,
            h.axle_a2 AS part_a,
            h.axle_b2 AS part_b,
            h.asset_created2 AS t_start,
            h.o_ts
        FROM hxm AS h
        WHERE NOT h.is_alt2
    ),
    current_asset AS (
        SELECT
            c.delivery_id AS anchor_id,
            a.axle_a AS part_a,
            a.axle_b AS part_b,
            a.bound_at AS t_start,
            c.created_at AS o_ts
        FROM cur AS c
        JOIN {q(VEHW)} AS a
            ON a.link_id = c.link_id
        WHERE c.link_id IS NOT NULL
    ),
    asset_union AS (
        SELECT * FROM prior_assets
        UNION ALL
        SELECT * FROM current_asset
    ),
    asset_pick AS (
        SELECT DISTINCT ON (anchor_id, part_a, part_b)
            anchor_id,
            part_a,
            part_b,
            t_start
        FROM asset_union
        ORDER BY
            anchor_id,
            part_a,
            part_b,
            COALESCE(t_start, o_ts)
    ),
    asset_one AS (
        SELECT DISTINCT ON (anchor_id)
            anchor_id,
            part_a,
            part_b,
            t_start
        FROM asset_pick
        OPTIONS (DISTINCT ON INPUT GROUP SIZE = 256)
        ORDER BY
            anchor_id,
            t_start DESC
    )""")
STATS["picks"] += 1
STATS["hints"] += 1
STATS["coalesce"] += 1
# 6 ten first-use CTEs (identifier levels; all join keys bounded so the
# anchor x match volume stays laptop-scale; hints sized to TRUE groups)
FIRST_USE = [
    # (name, mode, params)
    ("fu_plate", "pick", ("axle_a", "part_a", "acquired_at", 256)),
    ("fu_axleb", "pick", ("axle_b", "part_b", "acquired_at", 256)),
    ("fu_postal", "redeliv", ("postal_code", 64)),
    ("fu_device", "redeliv", ("device_id", 64)),
    ("fu_alt", "cur", ("dsp_hist_by_alt" if REF_B else "deliveries",
                       "alt_ref", "alt_ref", "created_at", 64)),
    ("fu_promo", "redeliv", ("promo_code", 256)),
    ("fu_devmeta", "cur", ("device_meta", "device_id", "device_id",
                           "first_seen", None)),
    ("fu_link", "cur", ("vehicle_links", "link_id", "link_id", "bound_at",
                        None)),
    ("fu_ping", "cur", ("route_pings", "delivery_id", "delivery_id",
                        "pinged_at", None)),
    ("fu_badge", "cur", ("badge_scans", "courier_id", "courier_id",
                         "noted_at", 64)),
    ("fu_scan", "cur", ("scans", "delivery_id", "delivery_id",
                        "noted_at", 64)),
    ("fu_hold", "cur", ("holds", "delivery_id", "delivery_id",
                        "noted_at", None)),
    ("fu_toll", "cur", ("toll_events", "delivery_id", "delivery_id",
                        "noted_at", None)),
    ("fu_refuel", "cur", ("refuel_stops", "courier_id", "courier_id",
                          "noted_at", 64)),
]
for nm, mode, prm in FIRST_USE:
    STATS["joins"] += 1
    if mode == "pick":
        bcol, pcol, tscol, hint = prm
        STATS["hints"] += 1
        mega.append(f"""    {nm} AS (
        SELECT
            ap.anchor_id,
            pg_catalog.min(b.{tscol}) AS first_at
        FROM asset_one AS ap
        JOIN {q('vehicles')} AS b
            ON b.{bcol} = ap.{pcol}
        GROUP BY ap.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = {hint})
    )""")
    elif mode == "redeliv":
        keycol, hint = prm
        STATS["joins"] += 1
        STATS["hints"] += 1
        mega.append(f"""    {nm} AS (
        SELECT
            c2.delivery_id AS anchor_id,
            pg_catalog.min(b.created_at) AS first_at
        FROM (
            SELECT
                c.delivery_id,
                c.created_at,
                d0.{keycol}
            FROM cur AS c
            JOIN {q('deliveries')} AS d0
                ON d0.delivery_id = c.delivery_id
        ) AS c2
        JOIN {q('deliveries')} AS b
            ON b.{keycol} = c2.{keycol}
            AND b.created_at < c2.created_at
        GROUP BY c2.delivery_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = {hint})
    )""")
    else:
        tab, bcol, ccol, tscol, hint = prm
        hint_line = ""
        if hint:
            hint_line = f"\n        OPTIONS (AGGREGATE INPUT GROUP SIZE = {hint})"
            STATS["hints"] += 1
        mega.append(f"""    {nm} AS (
        SELECT
            c.delivery_id AS anchor_id,
            pg_catalog.min(b.{tscol}) AS first_at
        FROM cur AS c
        JOIN {q(tab)} AS b
            ON b.{bcol} = c.{ccol}
        GROUP BY c.delivery_id{hint_line}
    )""")
# 7 existence markers
STATS["joins"] += 2
STATS["picks"] += 1
STATS["hints"] += 1
mega.append(f"""    mark_perm AS (
        SELECT DISTINCT ON (c.delivery_id)
            c.delivery_id AS anchor_id,
            true AS has_permit
        FROM cur AS c
        JOIN {q('permit_grants')} AS pg0
            ON pg0.delivery_id = c.delivery_id
        ORDER BY c.delivery_id
    ),
    mark_train AS (
        SELECT
            c.delivery_id AS anchor_id,
            pg_catalog.bool_or(tf.mark_kind = 'm1') AS has_training
        FROM cur AS c
        JOIN {q('training_flags')} AS tf
            ON tf.courier_id = c.courier_id
        GROUP BY c.delivery_id
    )""")
# 8 most-recent trio over hist_eff/hist_cat
for nm, src, cond in [("rc_eff", "hist_eff", "h.same_asset"),
                      ("rc_bad", "hist_eff", "h.phase2 = 'failed'"),
                      ("rc_any", "hist_cat", "true")]:
    STATS["picks"] += 1
    STATS["hints"] += 1
    pcols = "h.created_at2 AS at2,\n            h.load_units2 AS load2" \
        if src == "hist_eff" else "h.created_at2 AS at2,\n            h.match_key2 AS mk2"
    mega.append(f"""    {nm} AS (
        SELECT DISTINCT ON (h.anchor_id)
            h.anchor_id,
            {pcols}
        FROM {src} AS h
        WHERE {cond}
        OPTIONS (DISTINCT ON INPUT GROUP SIZE = 256)
        ORDER BY
            h.anchor_id,
            h.created_at2 DESC
    )""")
TWIN_A_HINT = 256 if REF else 65536
# 9 windowed slices + c6d twin reduces: byte-identical direct owner-history
# scans (true per-anchor group ~170); twin_a's 65536 is the mis-size, twin_b's
# 256 is correct, telling WHICH is which needs the landmark method.
STATS["joins"] += 2
mega.append(f"""    sl_hour AS (
        SELECT
            h.anchor_id,
            pg_catalog.count(*) AS n_1h,
            pg_catalog.min(h.created_at2) AS min_1h_at
        FROM hist_eff AS h
        WHERE h.created_at2 >= h.o_ts - INTERVAL '1 hour'
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    sl_day AS (
        SELECT
            h.anchor_id,
            pg_catalog.sum(h.load_units2)::pg_catalog.float8 AS load_24h
        FROM hist_eff AS h
        WHERE h.same_asset
          AND h.phase2 = 'completed'
          AND h.created_at2 >= h.o_ts - INTERVAL '24 hours'
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    sl_twin_a AS (
        SELECT
            c.delivery_id AS anchor_id,
            pg_catalog.count(*) AS twin_n,
            pg_catalog.max(h.load_units) AS twin_peak
        FROM cur AS c
        JOIN {q(FACTW)} AS h
            ON h.courier_id = c.courier_id
            AND h.created_at < c.created_at
        WHERE h.phase = 'completed'
        GROUP BY c.delivery_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = {TWIN_A_HINT})
    ),
    sl_twin_b AS (
        SELECT
            c.delivery_id AS anchor_id,
            pg_catalog.count(*) AS twin_n,
            pg_catalog.max(h.load_units) AS twin_peak
        FROM cur AS c
        JOIN {q(FACTW)} AS h
            ON h.courier_id = c.courier_id
            AND h.created_at < c.created_at
        WHERE h.phase = 'failed'
        GROUP BY c.delivery_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    sl_2d_other AS (
        SELECT
            h.anchor_id,
            pg_catalog.count(*) AS n_other_bad_2d
        FROM hist_cat AS h
        WHERE NOT h.same_asset
          AND h.created_at2 >= h.o_ts - INTERVAL '2 days'
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    sl_7d AS (
        SELECT
            h.anchor_id,
            pg_catalog.count(*) AS n_7d,
            pg_catalog.sum(h.load_units2)::pg_catalog.float8 AS load_7d,
            pg_catalog.count(*) FILTER (WHERE h.phase2 = 'failed') AS bad_7d
        FROM hist_eff AS h
        WHERE h.created_at2 >= h.o_ts - INTERVAL '7 days'
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    sl_30d AS (
        SELECT
            h.anchor_id,
            pg_catalog.count(*) AS n_30d,
            pg_catalog.max(h.load_units2) AS peak_30d
        FROM hist_eff AS h
        WHERE h.created_at2 >= h.o_ts - INTERVAL '30 days'
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    sl_90d AS (
        SELECT
            h.anchor_id,
            pg_catalog.count(*) AS n_90d,
            pg_catalog.count(DISTINCT h.match_key2) AS assets_90d
        FROM hist_cat AS h
        WHERE h.created_at2 >= h.o_ts - INTERVAL '90 days'
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    sl_same_asset AS (
        SELECT
            h.anchor_id,
            pg_catalog.count(*) AS n_same,
            pg_catalog.min(h.created_at2) AS first_same_at
        FROM hist_cat AS h
        WHERE h.same_asset
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    ),
    mark_curfew AS (
        SELECT
            c.delivery_id AS anchor_id,
            pg_catalog.bool_or(cw.mark_phase = 'failed') AS curfew_hit
        FROM cur AS c
        JOIN {q('curfew_windows')} AS cw
            ON cw.courier_id = c.courier_id
        GROUP BY c.delivery_id
    ),
    mark_photo AS (
        SELECT DISTINCT ON (c.delivery_id)
            c.delivery_id AS anchor_id,
            true AS has_photo
        FROM cur AS c
        JOIN {q('photo_logs')} AS ph
            ON ph.delivery_id = c.delivery_id
        ORDER BY c.delivery_id
    )""")
STATS["hints"] += 10
STATS["joins"] += 2
STATS["picks"] += 1
STATS["filters"] += 1
# 10 moment sketch
mega.append("""    momt AS (
        SELECT
            h.anchor_id,
            pg_catalog.count(*) AS n_rows,
            pg_catalog.sum(h.load_units2) AS sum_v,
            pg_catalog.sum(h.load_units2 * h.load_units2) AS sum_sq
        FROM hist_eff AS h
        WHERE h.same_asset
          AND h.phase2 = 'completed'
        GROUP BY h.anchor_id
        OPTIONS (AGGREGATE INPUT GROUP SIZE = 256)
    )""")
STATS["hints"] += 1
emit(",\n".join(mega))
# 11 final assembly
outcols = ["c.delivery_id AS anchor_id"]
outcols.append(CO("sl_hour.n_1h", "0", "runs_last_hour"))
outcols.append(CO("sl_day.load_24h", "0.0", "asset_load_24h"))
outcols.append(CO("sl_twin_a.twin_n", "0", "eff_runs_2d"))
outcols.append(CO("sl_twin_b.twin_n", "0", "cat_runs_2d"))
outcols.append(CO("sl_twin_a.twin_peak", "0.0", "eff_peak_2d"))
outcols.append(CO("sl_twin_b.twin_peak", "0.0", "cat_peak_2d"))
outcols.append(CO("sl_2d_other.n_other_bad_2d", "0", "other_asset_runs_2d"))
outcols.append(CO("sl_7d.n_7d", "0", "eff_runs_7d"))
outcols.append(CO("sl_7d.load_7d", "0.0", "eff_load_7d"))
outcols.append(CO("sl_7d.bad_7d", "0", "bad_runs_7d"))
outcols.append(CO("sl_30d.n_30d", "0", "eff_runs_30d"))
outcols.append(CO("sl_30d.peak_30d", "0.0", "peak_load_30d"))
outcols.append(CO("sl_90d.n_90d", "0", "cat_runs_90d"))
outcols.append(CO("sl_90d.assets_90d", "0", "distinct_assets_90d"))
outcols.append(CO("sl_same_asset.n_same", "0", "same_asset_runs_all"))
outcols.append("""pg_catalog.extract('epoch',
        c.created_at - COALESCE(sl_same_asset.first_same_at, c.created_at))
        ::pg_catalog.float8 AS s_since_first_same_asset""")
outcols.append(CO("mark_curfew.curfew_hit", "false", "curfew_hit_mark"))
outcols.append(CO("mark_photo.has_photo", "false", "has_photo_mark"))
outcols.append("""CASE
        WHEN idv.ident_loan_open THEN NULL
        ELSE rc_eff.load2
    END AS last_eff_load""")
outcols.append("""COALESCE(pg_catalog.extract('epoch',
        c.created_at - rc_bad.at2),
        9999.0 * 86400.0)::pg_catalog.float8 AS s_since_bad""")
STATS["coalesce"] += 1
outcols.append("""COALESCE(pg_catalog.extract('epoch',
        c.created_at - rc_any.at2),
        9999.0 * 86400.0)::pg_catalog.float8 AS s_since_any""")
STATS["coalesce"] += 1
for nm, _, _ in FIRST_USE:
    outcols.append(f"""pg_catalog.extract('epoch',
        c.created_at - COALESCE({nm}.first_at, c.created_at))
        ::pg_catalog.float8 AS s_first_{nm[3:]}""")
    STATS["coalesce"] += 1
outcols.append(CO("mark_perm.has_permit", "false", "has_permit_mark"))
outcols.append(CO("mark_train.has_training", "false", "has_training_mark"))
outcols.append("""((COALESCE(momt.sum_v, 0) + c.load_units)
        / (COALESCE(momt.n_rows, 0) + 1))::pg_catalog.float8
        AS asset_run_mean""")
outcols.append("""pg_catalog.sqrt(GREATEST(
        (COALESCE(momt.sum_sq, 0)
            + c.load_units * c.load_units
            - pg_catalog.power(
                COALESCE(momt.sum_v, 0) + c.load_units, 2)
                / (COALESCE(momt.n_rows, 0) + 1))
        / (COALESCE(momt.n_rows, 0) + 1),
        0.0))::pg_catalog.float8 AS asset_run_std""")
STATS["coalesce"] += 18
outcols.append("""(CASE WHEN COALESCE(sl_hour.n_1h, 0) = 0
          THEN 0.0
          ELSE (sl_hour.n_1h + 1)
               / (pg_catalog.extract('epoch',
                    c.created_at - sl_hour.min_1h_at)
                  / 60.0)
     END)::pg_catalog.float8 AS asset_per_min_rate""")
STATS["coalesce"] += 1
outcols.append(CO("asset_one.part_a", "''", "active_part_a"))
outcols.append("idv.ident_risk_band")
emit("SELECT")
emit(sel_lines(outcols))
emit("FROM cur AS c")
for j in ["sl_hour", "sl_day", "sl_twin_a", "sl_twin_b", "sl_2d_other",
          "sl_7d", "sl_30d", "sl_90d", "sl_same_asset",
          "rc_eff", "rc_bad", "rc_any", "momt", "mark_perm", "mark_train",
          "mark_curfew", "mark_photo",
          "asset_one"] + [nm for nm, *_ in FIRST_USE]:
    emit(J("LEFT", j, j + "0", f"c.delivery_id = {j}0.anchor_id")
         .replace(f" AS {j}0", "").replace(f"{j}0.", f"{j}."))
emit(J("LEFT", "idv", "idv0", "c.delivery_id = idv0.anchor_id")
     .replace(" AS idv0", "").replace("idv0.", "idv.") + ";")
emit()

# ==================================================================
# Terminal MVs (T6) + serving indexes
# ==================================================================
emit("-- ============ terminal materialized views ============")
emit()

def mv(name, feats, joins, note=None, inner_aliases=()):
    """feats: list of column strings; joins: list of (view, alias).
    inner_aliases: aliases to emit as INNER joins (reference C10: provable
    LEFT->INNER where the feature view is total per anchor)."""
    view_open(name, mat=True, cluster=S)
    emit("SELECT")
    emit(sel_lines(feats))
    emit(f"FROM {q(SPINE)} AS o")
    for v, a in joins:
        kind = "" if (REF and a in inner_aliases) else "LEFT"
        line = J(kind, q(v), a, f"o.delivery_id = {a}.anchor_id")
        emit(line.lstrip() if kind == "" else line)
    OUT[-1] = OUT[-1] + ";"
    if note:
        emit(f"-- {note}")
    emit()

# P1: mega + gw_outcome (2 joins), consumes raw_payload (C5a)
mv(f"{P}_{T4}_saga_vector",
   ["o.delivery_id AS anchor_id",
    CO("mg.runs_last_hour", "0", "runs_last_hour"),
    CO("mg.asset_load_24h", "0.0", "asset_load_24h"),
    CO("mg.eff_runs_2d", "0", "eff_runs_2d"),
    CO("mg.cat_runs_2d", "0", "cat_runs_2d"),
    CO("mg.eff_peak_2d", "0.0", "eff_peak_2d"),
    CO("mg.other_asset_runs_2d", "0", "other_asset_runs_2d"),
    "mg.last_eff_load",
    CO("mg.s_since_bad", "9999.0 * 86400.0", "s_since_bad"),
    CO("mg.s_since_any", "9999.0 * 86400.0", "s_since_any"),
    CO("mg.s_first_plate", "0.0", "s_first_plate"),
    CO("mg.s_first_postal", "0.0", "s_first_postal"),
    CO("mg.s_first_device", "0.0", "s_first_device"),
    CO("mg.has_permit_mark", "false", "has_permit_mark"),
    CO("mg.asset_run_mean", "0.0", "asset_run_mean"),
    CO("mg.asset_run_std", "0.0", "asset_run_std"),
    CO("mg.asset_per_min_rate", "0.0", "asset_per_min_rate"),
    CO("mg.eff_runs_7d", "0", "eff_runs_7d"),
    CO("mg.eff_load_7d", "0.0", "eff_load_7d"),
    CO("mg.bad_runs_7d", "0", "bad_runs_7d"),
    CO("mg.eff_runs_30d", "0", "eff_runs_30d"),
    CO("mg.peak_load_30d", "0.0", "peak_load_30d"),
    CO("mg.cat_runs_90d", "0", "cat_runs_90d"),
    CO("mg.distinct_assets_90d", "0", "distinct_assets_90d"),
    CO("mg.same_asset_runs_all", "0", "same_asset_runs_all"),
    CO("mg.s_since_first_same_asset", "0.0", "s_since_first_same_asset"),
    CO("mg.curfew_hit_mark", "false", "curfew_hit_mark"),
    CO("mg.has_photo_mark", "false", "has_photo_mark"),
    CO("mg.s_first_alt", "0.0", "s_first_alt"),
    CO("mg.s_first_link", "0.0", "s_first_link"),
    CO("mg.s_first_badge", "0.0", "s_first_badge"),
    CO("mg.active_part_a", "''", "active_part_a"),
    CO("mg.ident_risk_band", "'clear'", "ident_risk_band"),
    CO("gw.raw_payload", "'{}'::pg_catalog.jsonb", "raw_payload"),
    "gw.feat_k_conf", "gw.feat_k_score", "gw.feat_k_mode"],
   [(MEGA, "mg"), (f"{P}_{T2}_gw_outcome", "gw")])

# P2: depot profile (4 joins; W1+W2 = K1 intra pair)
mv(f"{P}_{T4}_depot_profile",
   ["o.delivery_id AS anchor_id",
    CO("w1.n_all", "1", "depot_n_all"),
    CO("w1.v_total", "o.load_units::pg_catalog.float8", "depot_v_total"),
    CO("w1.s_last", "0.0", "depot_s_last"),
    CO("w1.s_last_bad", "9999.0 * 86400.0", "depot_s_last_bad"),
    CO("w2.prev_phase", "''", "depot_prev_phase"),
    CO("w2.prev_load", "0.0", "depot_prev_load"),
    CO("w8.owner_lifetime_n", "0", "owner_lifetime_n"),
    CO("w8.owner_lifetime_load", "0.0", "owner_lifetime_load"),
    CO("w8.owner_peak_load", "0.0", "owner_peak_load"),
    CO("w8.owner_tenure_s", "0.0", "owner_tenure_s"),
    CO("w8.owner_age_band", "'fresh'", "owner_age_band"),
    CO(f"rf.{vcol(f'{P}_{T2}_refuel_stats', 'tally_sum')}", "0.0",
       "refuel_units_sum"),
    f"rf.{vcol(f'{P}_{T2}_refuel_stats', 'tally_any')} AS refuel_seen"],
   [(f"{P}_{T3}_depot_history", "w1"), (f"{P}_{T3}_depot_recency", "w2"),
    (f"{P}_{T3}_owner_tally", "w8"), (f"{P}_{T2}_refuel_stats", "rf")])

# P3: depot pulse (2 joins)
mv(f"{P}_{T4}_depot_pulse",
   ["o.delivery_id AS anchor_id",
    CO("w3.run_mean", "0.0", "depot_run_mean"),
    CO("w3.run_std", "0.0", "depot_run_std"),
    "w3.moment_anchor_at",
    CO("fx.n_delays", "0", "recent_delay_n"),
    CO("fx.worst_delay", "0.0", "recent_worst_delay"),
    "fx.first_delay_at"],
   [(f"{P}_{T3}_depot_moment", "w3"), (f"{P}_{T2}_route_flux", "fx")])

# P4: lane profile (4 joins; W4+W5 = K2 intra pair; C10a on W5, C10b delay_bands)
mv(f"{P}_{T4}_lane_profile",
   ["o.delivery_id AS anchor_id",
    CO("w4.lane_n_all", "1", "lane_n_all"),
    CO("w4.per_min_rate", "0.0", "lane_per_min_rate"),
    CO("w4.is_first_ever", "true", "lane_is_first_ever"),
    CO("w5.s_since_first_lane", "0.0", "s_since_first_lane"),
    CO("w5.lane_prior_n", "0", "lane_prior_n"),
    CO("w5.lane_max_load", "0.0", "lane_max_load"),
    CO("db.n_delay_rows", "0", "n_delay_rows"),
    CO("db.delay_band", "'clean'", "delay_band"),
    CO("idn.ident_risk_band", "'clear'", "ident_risk_band"),
    CO("idn.ident_loan_n", "0", "ident_loan_n")],
   [(f"{P}_{T3}_lane_history", "w4"), (f"{P}_{T3}_lane_first", "w5"),
    (f"{P}_{T2}_delay_bands", "db"), (IDENT, "idn")],
   inner_aliases=("w5", "db"))

# P5: owner risk (2 joins; C8 + C9 consumers)
mv(f"{P}_{T4}_owner_risk",
   ["o.delivery_id AS anchor_id",
    CO("w6.pulse_n_all", "1", "pulse_n_all"),
    CO("w6.pulse_total", "o.load_units::pg_catalog.float8", "pulse_total"),
    CO("w6.pulse_s_last", "0.0", "pulse_s_last"),
    CO("alt.alt_n", "0", "alt_share_n"),
    CO("alt.alt_couriers", "0", "alt_share_couriers"),
    CO("alt.alt_foreign", "false", "alt_share_foreign")],
   [(f"{P}_{T3}_owner_pulse", "w6"), (f"{P}_{T2}_alt_share", "alt")])

# P6: courier board (9 joins, the wide COALESCE re-wrap)
p6joins = [(f"{P}_{T2}_scan_trail", "j1"), (f"{P}_{T2}_hold_flags", "j2"),
           (f"{P}_{T2}_claim_totals", "j3"), (f"{P}_{T2}_rating_pick", "j4"),
           (f"{P}_{T2}_damage_marks", "j5"), (f"{P}_{T2}_toll_totals", "j6"),
           (f"{P}_{T2}_handoff_pick", "j7"), (f"{P}_{T2}_seal_flags", "j8"),
           (f"{P}_{T2}_return_totals", "j9")]
p6feats = ["o.delivery_id AS anchor_id", "o.phase", "o.lane_code"]
for v, a in p6joins:
    kinds = {k for _, k in VIEW_COLS[v]}
    if "tally_sum" in kinds:
        p6feats.append(CO(f"{a}.{vcol(v, 'tally_sum')}", "0.0", feat_name()))
        p6feats.append(CO(f"{a}.{vcol(v, 'tally_any')}", "false", feat_name()))
    if "tally_avg" in kinds:
        p6feats.append(CO(f"{a}.{vcol(v, 'tally_avg')}", "0.0", feat_name()))
    if "tally_age" in kinds:
        p6feats.append(CO(f"{a}.{vcol(v, 'tally_age')}", "0.0", feat_name()))
    if "mark_flag" in kinds:
        p6feats.append(CO(f"{a}.{vcol(v, 'mark_flag')}", "false", feat_name()))
    if "mark_n" in kinds:
        p6feats.append(CO(f"{a}.{vcol(v, 'mark_n')}", "0", feat_name()))
    if "mark_label" in kinds:
        p6feats.append(CO(f"{a}.{vcol(v, 'mark_label')}", "'none'", feat_name()))
    if "pick_kind" in kinds:
        p6feats.append(CO(f"{a}.{vcol(v, 'pick_kind')}", "''", feat_name()))
        p6feats.append(CO(f"{a}.{vcol(v, 'pick_units')}", "0.0", feat_name()))
mv(f"{P}_{T4}_courier_board", p6feats, p6joins)

# P7: ops snapshot (1 join)
mv(f"{P}_{T4}_ops_snapshot",
   ["o.delivery_id AS anchor_id", "o.phase", "o.service_tier",
    CO(f"dm.{vcol(f'{P}_{T2}_dispute_marks', 'tally_sum')}", "0.0",
       "dispute_units_sum"),
    CO(f"dm.{vcol(f'{P}_{T2}_dispute_marks', 'tally_any')}", "false",
       "dispute_seen"),
    CO(f"dm.{vcol(f'{P}_{T2}_dispute_marks', 'pick_kind')}", "''",
       "dispute_last_kind"),
    CO(f"dm.{vcol(f'{P}_{T2}_dispute_marks', 'mark_flag')}", "false",
       "dispute_flagged")],
   [(f"{P}_{T2}_dispute_marks", "dm")])

# P8: audit trail (5 joins; gw_probe raw_payload NOT selected, C5b)
mv(f"{P}_{T4}_audit_trail",
   ["o.delivery_id AS anchor_id",
    "sm.anchor_id IS NOT NULL AS shift_mix_present",
    CO("gp.feat_k_conf", "-1.0", "probe_conf"),
    CO("gp.feat_k_mode", "''", "probe_mode"),
    "ac.ident_risk_band AS addr_risk_band",
    CO(f"ac.{vcol(f'{P}_{T2}_addr_checks', 'pick_kind')}", "''",
       "addr_check_kind"),
    CO(f"pp2.{vcol(f'{P}_{T2}_permit_pick', 'tally_sum')}", "0.0",
       "permit_units_sum"),
    CO("w7.top3_max_load", "0.0", "top3_max_load"),
    CO("w7.top3_n", "0", "top3_n")],
   [(f"{P}_{T2}_shift_mix", "sm"), (f"{P}_{T2}_gw_probe", "gp"),
    (f"{P}_{T2}_addr_checks", "ac"), (f"{P}_{T2}_permit_pick", "pp2"),
    (f"{P}_{T3}_owner_top3", "w7")])

# ---- serving indexes (advisor seeding) + identity index ----------
emit("-- ============ serving indexes ============")
emit(f"CREATE INDEX idx_{P}_{T4}_saga_vector ON {q(f'{P}_{T4}_saga_vector')} (anchor_id);")
emit(f"CREATE INDEX idx_{P}_{T4}_lane_profile ON {q(f'{P}_{T4}_lane_profile')} (anchor_id);")
emit(f"CREATE INDEX idx_{P}_{T4}_courier_board ON {q(f'{P}_{T4}_courier_board')} (anchor_id);")
emit(f"CREATE INDEX idx_{P}_{T4}_depot_profile ON {q(f'{P}_{T4}_depot_profile')} (anchor_id);")
emit(f"CREATE INDEX idx_{P}_{T4}_owner_risk ON {q(f'{P}_{T4}_owner_risk')} (anchor_id);")
emit(f"CREATE INDEX idx_{P}_{T2}_ident_flags ON {q(IDENT)} (anchor_id);")
emit()

# ==================================================================
# v5 constructions (C11-C23), appended so the v4 subset above stays
# byte-identical under --v4
# ==================================================================
DOCS = f"{P}_manifest_docs_{WRAP}"
DOCSIG = f"{P}_{T2}_doc_signal"
SCREEN = f"{P}_{T2}_ref_screen"
SEALM = f"{P}_{T2}_seal_match"
BEST = f"{P}_{T3}_courier_best"
GAP = f"{P}_{T3}_courier_gap"
HOLDR = f"{P}_{T2}_hold_rates"
HOLDROLL = f"{P}_{T3}_hold_bands"
PEAK = f"{P}_{T2}_shift_peak"
DOCK = f"{P}_{T2}_dock_tally"
LEGS = f"{P}_{T2}_leg_events"
LEGLANES = f"{P}_{T2}_leg_lanes"
LEGCOUR = f"{P}_{T3}_leg_courier"
LEGLANE = f"{P}_{T3}_leg_lane"
LANETIER = f"{P}_{T3}_lane_tiers"
DIGEST = f"{P}_{T2}_call_digest"
POSTAL = f"{P}_{T3}_postal_load"

# Sub-slice moduli for the v5 fact-derived tables. Each is coprime with
# ANCHOR_MOD and with the spread moduli, so a slice never resonates with the
# anchor selection or with one courier's arithmetic progression.
DOC_MOD, DOC_RES = 7, 3        # ~3/7 of the anchors carry a manifest document
SEAL_MOD, SEAL_RES = 4, 0      # ~1/4 of the anchors carry a seal scan
N_SEALREG = 3_000 // _SC       # seal registry rows (the null-safe join's RHS)
N_CARRIER = 300                # carrier code dimension
N_BANDS = 20                   # rate bands: a uniform 10-unit grid

if V5:
    emit("-- ============ v5 base tables ============")
    emit()

    def v5_table(name, coldefs):
        """coldefs: list of 'colname type [NOT NULL]' strings, already
        catalog-qualified. create_table() cannot express NOT NULL, and the
        nullability of carrier_codes/manifest_docs is load-bearing (C13's
        red-herring twin needs a NOT NULL compared column)."""
        obj_banner("table", name)
        emit(f"CREATE TABLE {q(name)} (")
        emit(",\n".join(f"    {c}" for c in coldefs))
        emit(");")
        emit()

    v5_table("carrier_codes", [
        "code_id pg_catalog.int4 NOT NULL",
        "carrier_code pg_catalog.text NOT NULL",
        "code_class pg_catalog.text",
        "code_weight pg_catalog.float8"])
    v5_table("rate_bands", [
        "band_id pg_catalog.int4",
        "band_lo pg_catalog.float8",
        "band_hi pg_catalog.float8",
        "band_label pg_catalog.text",
        "band_note pg_catalog.text"])
    v5_table("manifest_docs", [
        "doc_id pg_catalog.int4 NOT NULL",
        "delivery_id pg_catalog.int4 NOT NULL",
        "doc_ref pg_catalog.text NOT NULL",
        "doc_body pg_catalog.text"])
    v5_table("seal_scans", [
        "seal_id pg_catalog.int4",
        "delivery_id pg_catalog.int4",
        "seal_code pg_catalog.text",
        "seal_kind pg_catalog.text",
        "seal_units pg_catalog.float8"])
    v5_table("seal_registry", [
        "reg_id pg_catalog.int4",
        "seal_code pg_catalog.text",
        "seal_class pg_catalog.text",
        "reg_note pg_catalog.text"])

    emit("-- ============ v5 data ============")
    emit()
    emit(f"""INSERT INTO {q('carrier_codes')}
SELECT
    g,
    'cc' || (g - 1)::pg_catalog.text,
    'class_' || (g % 5)::pg_catalog.text,
    ((g % 17) / 3.0)::pg_catalog.float8
FROM generate_series(1, {N_CARRIER}) AS g;
""")
    emit(f"""INSERT INTO {q('rate_bands')}
SELECT
    g - 1,
    ((g - 1) * 10)::pg_catalog.float8,
    (g * 10)::pg_catalog.float8,
    'band_' || (g - 1)::pg_catalog.text,
    'note_' || (g % 4)::pg_catalog.text
FROM generate_series(1, {N_BANDS}) AS g;
""")
    # manifest documents: one ~1.5 kB body per selected anchor. The header
    # segment carries the carrier code that C11's subquery correlates on.
    emit(f"""INSERT INTO {q('manifest_docs')}
SELECT
    d.delivery_id * 4 + 1,
    d.delivery_id,
    'cc' || ((d.delivery_id * 11) % {N_CARRIER})::pg_catalog.text,
    'hdr|' || 'cc' || ((d.delivery_id * 3) % {N_CARRIER})::pg_catalog.text
        || '|' || repeat('m', 700)
        || ((d.delivery_id * 7) % 991)::pg_catalog.text
        || repeat('q', 760)
FROM {q('deliveries')} AS d
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3
  AND d.delivery_id % {DOC_MOD} < {DOC_RES};
""")
    # seal scans on a quarter of the anchors; ~8% of codes NULL on each side,
    # which is what makes the null-safe join's NULL-NULL block real. The NULL
    # modulus must be coprime with 12: deliveries with g % 12 < 4 belong to
    # the dormant courier tier and never reach a slice filtered on
    # courier_id >= 38, so a NULL rule on a multiple of 12 selects exactly the
    # rows the slice already excluded and the NULL population comes out empty.
    emit(f"""INSERT INTO {q('seal_scans')}
SELECT
    d.delivery_id * 3 + 1,
    d.delivery_id,
    CASE WHEN d.delivery_id % 13 = 5 THEN NULL
         ELSE 'SC' || ((d.delivery_id * 7) % 1150)::pg_catalog.text END,
    'sk' || (d.delivery_id % 4)::pg_catalog.text,
    ((d.delivery_id % 400) / 8.0)::pg_catalog.float8
FROM {q('deliveries')} AS d
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3
  AND d.delivery_id % {SEAL_MOD} = {SEAL_RES};
""")
    emit(f"""INSERT INTO {q('seal_registry')}
SELECT
    g,
    CASE WHEN g % 13 = 0 THEN NULL
         ELSE 'SC' || ((g * 3) % 1150)::pg_catalog.text END,
    'cl' || (g % 6)::pg_catalog.text,
    'rn' || (g % 25)::pg_catalog.text
FROM generate_series(1, {N_SEALREG}) AS g;
""")

    emit("-- ============ v5 wrapper ============")
    emit()
    view_open(DOCS)
    emit("SELECT")
    emit(sel_lines(["doc_id", "delivery_id", "doc_ref", "doc_body"]))
    emit(f"FROM {q('manifest_docs')};")
    emit()

    emit("-- ============ v5 enrichment views ============")
    emit()

    # ---- C11: subquery correlated on a payload column ----------------
    # Baseline correlates on doc_body itself, so the Distinct and both
    # join-back arrangements are keyed by the ~1.5 kB document. Reference
    # extracts the header code first; the correlation key becomes a short
    # text and the same rows come out.
    view_open(f"{P}_{T2}_doc_codes")
    STATS["joins"] += 2
    if REF:
        emit(f"""WITH doc_head AS (
    SELECT
        m.doc_id,
        m.delivery_id,
        m.doc_ref,
        pg_catalog.split_part(m.doc_body, '|', 2) AS body_code
    FROM {q(DOCS)} AS m
)
SELECT
    d.doc_id,
    d.delivery_id AS anchor_id,
    (
        SELECT pg_catalog.count(*)
        FROM {q('carrier_codes')} AS r
        WHERE r.carrier_code = d.body_code
    ) AS code_hits,
    (
        d.doc_ref IN (
            SELECT c.carrier_code
            FROM {q('carrier_codes')} AS c)
    ) AS ref_known
FROM doc_head AS d;""")
    else:
        emit(f"""SELECT
    m.doc_id,
    m.delivery_id AS anchor_id,
    (
        SELECT pg_catalog.count(*)
        FROM {q('carrier_codes')} AS r
        WHERE r.carrier_code = pg_catalog.split_part(m.doc_body, '|', 2)
    ) AS code_hits,
    (
        m.doc_ref IN (
            SELECT c.carrier_code
            FROM {q('carrier_codes')} AS c)
    ) AS ref_known
FROM {q(DOCS)} AS m;""")
    emit()

    view_open(DOCSIG)
    emit(f"""SELECT
    anchor_id,
    pg_catalog.sum(code_hits) AS doc_code_hits,
    pg_catalog.bool_or(ref_known) AS doc_ref_known,
    pg_catalog.count(*) AS doc_n
FROM {q(f'{P}_{T2}_doc_codes')}
GROUP BY anchor_id;""")
    emit()

    # ---- C12 + C13 + C14: the subquery screening view -----------------
    view_open(SCREEN)
    STATS["joins"] += 3
    _c13 = f"""    CASE
        WHEN o.alt_ref IS NULL THEN NULL
        ELSE h.code IS NOT NULL
    END AS ref_listed,""" if REF else f"""    (
        o.alt_ref IN (
            SELECT c.carrier_code
            FROM {q('carrier_codes')} AS c)
    ) AS ref_listed,"""
    _c12 = f"""WHERE o.alt_ref IS NOT NULL
  AND NOT EXISTS (
        SELECT 1
        FROM {q('carrier_codes')} AS c
        WHERE c.carrier_code = o.alt_ref)""" if REF else f"""WHERE o.alt_ref NOT IN (
    SELECT c.carrier_code
    FROM {q('carrier_codes')} AS c)"""
    _c13cte = f"""WITH hits AS (
    SELECT DISTINCT c.carrier_code AS code
    FROM {q('carrier_codes')} AS c
)
""" if REF else ""
    _c13join = f"""
LEFT JOIN hits AS h
    ON h.code = o.alt_ref""" if REF else ""
    emit(f"""{_c13cte}SELECT
    o.delivery_id AS anchor_id,
    o.alt_ref,
{_c13}
    (
        SELECT pg_catalog.count(*)
        FROM {q('rate_bands')} AS b
        WHERE b.band_lo < o.load_units
    ) AS bands_below
FROM {q(SPINE)} AS o{_c13join}
{_c12};""")
    emit()

    # ---- C19: null-safe join ------------------------------------------
    view_open(SEALM)
    STATS["joins"] += 1
    _indf = ("COALESCE(s.seal_code, '~unset~')\n"
             "    = COALESCE(r.seal_code, '~unset~')") if REF \
        else "s.seal_code IS NOT DISTINCT FROM r.seal_code"
    emit(f"""SELECT
    s.delivery_id AS anchor_id,
    pg_catalog.count(*) AS seal_reg_n,
    pg_catalog.min(r.seal_class) AS seal_first_class,
    pg_catalog.sum(s.seal_units)::pg_catalog.float8 AS seal_units_sum
FROM {q('seal_scans')} AS s
JOIN {q('seal_registry')} AS r
    ON {_indf}
GROUP BY s.delivery_id;""")
    emit()

    # ---- C17: general outer-join lowering ------------------------------
    view_open(HOLDR)
    STATS["joins"] += 1
    STATS["left"] += 1
    if REF:
        emit(f"""SELECT
    o.anchor_id,
    o.courier_id,
    b.band_label,
    b.band_note
FROM (
    SELECT
        delivery_id AS anchor_id,
        courier_id,
        load_units
    FROM {q(FACTW)}
    WHERE phase = 'on_hold'
) AS o
LEFT JOIN {q('rate_bands')} AS b
    ON b.band_id
        = pg_catalog.floor(o.load_units / 10.0)::pg_catalog.int4;""")
    else:
        emit(f"""SELECT
    o.delivery_id AS anchor_id,
    o.courier_id,
    b.band_label,
    b.band_note
FROM {q(FACTW)} AS o
LEFT JOIN {q('rate_bands')} AS b
    ON b.band_lo <= o.load_units
    AND o.load_units < b.band_hi
WHERE o.phase = 'on_hold';""")
    emit()

    view_open(HOLDROLL)
    emit(f"""SELECT
    courier_id,
    pg_catalog.count(*) AS hold_n,
    pg_catalog.count(*) FILTER (WHERE band_label = 'band_5') AS hold_n_b5,
    pg_catalog.bool_or(band_note = 'note_1') AS hold_note1
FROM {q(HOLDR)}
GROUP BY courier_id;""")
    STATS["filters"] += 1
    emit()

    # ---- C21: argmax redundancy ---------------------------------------
    view_open(PEAK)
    STATS["joins"] += 2
    STATS["picks"] += 1
    STATS["hints"] += 1
    STATS["left"] += 1
    _peak_cte = "" if REF else f""",
    peak AS (
        SELECT
            o.delivery_id AS anchor_id,
            pg_catalog.max(s.mark_units) AS peak_units
        FROM {q(SPINE)} AS o
        JOIN {q('shift_logs')} AS s
            ON s.courier_id = o.courier_id
        GROUP BY o.delivery_id
    )"""
    _peak_col = "p.mark_units AS peak_units" if REF else "k.peak_units"
    _peak_join = "" if REF else """
LEFT JOIN peak AS k
    ON k.anchor_id = o.delivery_id"""
    if not REF:
        STATS["joins"] += 1
        STATS["left"] += 1
    emit(f"""WITH picked AS (
        SELECT DISTINCT ON (o.delivery_id)
            o.delivery_id AS anchor_id,
            s.mark_units,
            s.mark_kind
        FROM {q(SPINE)} AS o
        JOIN {q('shift_logs')} AS s
            ON s.courier_id = o.courier_id
        OPTIONS (DISTINCT ON INPUT GROUP SIZE = 4096)
        ORDER BY
            o.delivery_id,
            s.mark_units DESC,
            s.shift_log_id DESC
    ){_peak_cte}
SELECT
    o.delivery_id AS anchor_id,
    p.mark_kind AS shift_pick_kind,
    p.mark_units AS shift_pick_units,
    {_peak_col}
FROM {q(SPINE)} AS o
LEFT JOIN picked AS p
    ON p.anchor_id = o.delivery_id{_peak_join};""")
    emit()

    # ---- known-key LEFT JOIN herring (proposal item 20) ----------------
    view_open(DOCK)
    STATS["joins"] += 1
    STATS["left"] += 1
    emit(f"""SELECT
    o.delivery_id AS anchor_id,
    pg_catalog.count(ds.dock_slot_id) AS dock_n,
    pg_catalog.bool_or(ds.mark_phase = 'failed') AS dock_bad
FROM {q(SPINE)} AS o
LEFT JOIN {q('dock_slots')} AS ds
    ON ds.delivery_id = o.delivery_id
GROUP BY o.delivery_id;""")
    emit()

    # ---- C18: DISTINCT-blocked projection pushdown ---------------------
    view_open(LEGS)
    emit("SELECT" + ("" if REF else " DISTINCT"))
    emit(sel_lines(["delivery_id", "courier_id", "created_at", "lane_code",
                    "phase", "load_units", "service_tier", "region_code"]))
    emit(f"FROM {q(FACTW)}")
    emit("WHERE phase = 'canceled';")
    emit()

    view_open(LEGLANES)     # NOT redundant: dropping this DISTINCT changes rows
    emit("SELECT DISTINCT")
    emit(sel_lines(["courier_id", "lane_code", "service_tier"]))
    emit(f"FROM {q(LEGS)};")
    emit()

    view_open(LEGCOUR)
    emit(f"""SELECT
    courier_id,
    pg_catalog.count(*) AS leg_n,
    pg_catalog.sum(load_units)::pg_catalog.float8 AS leg_load
FROM {q(LEGS)}
GROUP BY courier_id;""")
    emit()

    view_open(LEGLANE)
    emit(f"""SELECT
    lane_code,
    pg_catalog.count(*) AS lane_leg_n,
    pg_catalog.sum(load_units)::pg_catalog.float8 AS lane_leg_load
FROM {q(LEGS)}
GROUP BY lane_code;""")
    emit()

    view_open(LANETIER)
    emit(f"""SELECT
    lane_code,
    pg_catalog.count(*) AS lane_tier_n
FROM {q(LEGLANES)}
GROUP BY lane_code;""")
    emit()

    # ---- C20: basic aggregate keeping its full input -------------------
    view_open(DIGEST)
    STATS["joins"] += 1
    _agg = ("""pg_catalog.jsonb_agg(
               pg_catalog.jsonb_build_object(
                   'm', g.payload ->> 'k_mode')
               ORDER BY g.seq, g.call_id)""" if REF
            else "pg_catalog.jsonb_agg(g.payload ORDER BY g.seq, g.call_id)")
    _key = "'m'" if REF else "'k_mode'"
    emit(f"""SELECT
    anchor_id,
    calls_json -> 0 ->> {_key} AS first_call_mode,
    pg_catalog.jsonb_array_length(calls_json) AS n_call_payloads
FROM (
    SELECT
        o.delivery_id AS anchor_id,
        {_agg} AS calls_json
    FROM {q(SPINE)} AS o
    JOIN {q(GWW)} AS g
        ON g.delivery_id = o.delivery_id
        AND g.valid_flag
    GROUP BY o.delivery_id
) AS d;""")
    emit()

    # ---- C15 / C16: the two window gadgets -----------------------------
    emit("-- ============ v5 window views ============")
    emit()
    view_open(BEST)
    _best_from = f"""(
        SELECT
            courier_id,
            delivery_id,
            load_units,
            lane_code,
            created_at
        FROM {q(FACTW)}
        WHERE phase = 'completed'
    ) AS h""" if REF else f"""{q(FACTW)} AS h
    WHERE h.phase = 'completed'"""
    emit(f"""SELECT
    courier_id,
    delivery_id AS best_delivery_id,
    load_units AS best_load,
    lane_code AS best_lane,
    created_at AS best_at
FROM (
    SELECT
        h.*,
        pg_catalog.row_number() OVER (
            PARTITION BY h.courier_id
            ORDER BY h.load_units DESC, h.delivery_id DESC) AS rn
    FROM {_best_from}
) AS ranked
WHERE rn = 1;""")
    emit()

    view_open(GAP)
    _gap_from = f"""(
        SELECT
            courier_id,
            delivery_id,
            created_at
        FROM {q(FACTW)}
        WHERE phase = 'failed'
    ) AS h""" if REF else f"""{q(FACTW)} AS h
    WHERE h.phase = 'failed'"""
    emit(f"""SELECT
    courier_id,
    pg_catalog.count(*) AS gap_n,
    pg_catalog.avg(gap_s)::pg_catalog.float8 AS gap_avg_s,
    pg_catalog.sum(gap_s)::pg_catalog.float8 AS gap_total_s
FROM (
    SELECT
        courier_id,
        pg_catalog.extract('epoch', created_at - prev_at)
            ::pg_catalog.float8 AS gap_s
    FROM (
        SELECT
            h.*,
            pg_catalog.lag(h.created_at) OVER (
                PARTITION BY h.courier_id
                ORDER BY h.created_at, h.delivery_id) AS prev_at
        FROM {_gap_from}
    ) AS lagged
    WHERE prev_at IS NOT NULL
) AS gaps
GROUP BY courier_id;""")
    emit()

    # ---- C23: distributive pre-aggregation below a join ----------------
    view_open(POSTAL)
    STATS["joins"] += 1
    if REF:
        emit(f"""WITH per_postal AS (
    SELECT
        postal_code,
        pg_catalog.sum(load_units)::pg_catalog.float8 AS pl,
        pg_catalog.count(*) AS pn,
        pg_catalog.count(*) FILTER (WHERE phase = 'failed') AS pbad,
        pg_catalog.sum(risk_score)::pg_catalog.float8 AS prisk
    FROM {q(FACTW)}
    GROUP BY postal_code
)
SELECT
    o.delivery_id AS anchor_id,
    pg_catalog.sum(p.pl)::pg_catalog.float8 AS postal_load,
    pg_catalog.sum(p.pn)::pg_catalog.int8 AS postal_n,
    pg_catalog.sum(p.pbad)::pg_catalog.int8 AS postal_bad,
    pg_catalog.sum(p.prisk)::pg_catalog.float8 AS postal_risk
FROM {q(SPINE)} AS o
JOIN per_postal AS p
    ON p.postal_code = o.postal_code
GROUP BY o.delivery_id;""")
    else:
        emit(f"""SELECT
    o.delivery_id AS anchor_id,
    pg_catalog.sum(h.load_units)::pg_catalog.float8 AS postal_load,
    pg_catalog.count(*) AS postal_n,
    pg_catalog.count(*) FILTER (WHERE h.phase = 'failed') AS postal_bad,
    pg_catalog.sum(h.risk_score)::pg_catalog.float8 AS postal_risk
FROM {q(SPINE)} AS o
JOIN {q(FACTW)} AS h
    ON h.postal_code = o.postal_code
GROUP BY o.delivery_id;""")
    STATS["filters"] += 1
    emit()

    # ---- terminal MVs -------------------------------------------------
    emit("-- ============ v5 terminal materialized views ============")
    emit()

    def mv5(name, feats, joins):
        """joins: list of (view, alias, on-expression)."""
        view_open(name, mat=True, cluster=S)
        emit("SELECT")
        emit(sel_lines(feats))
        emit(f"FROM {q(SPINE)} AS o")
        for v, a, on in joins:
            STATS["joins"] += 1
            STATS["left"] += 1
            emit(f"LEFT JOIN {q(v)} AS {a}")
            emit(f"    ON {on}")
        OUT[-1] = OUT[-1] + ";"
        emit()

    # P9: the subquery family
    mv5(f"{P}_{T4}_route_audit",
        ["o.delivery_id AS anchor_id",
         CO("dc.doc_code_hits", "0", "doc_code_hits"),
         CO("dc.doc_ref_known", "false", "doc_ref_known"),
         CO("dc.doc_n", "0", "doc_n"),
         "rs.ref_listed AS screen_ref_listed",
         CO("rs.bands_below", "0", "screen_bands_below"),
         CO("sm.seal_reg_n", "0", "seal_reg_n"),
         CO("sm.seal_first_class", "''", "seal_first_class"),
         CO("sm.seal_units_sum", "0.0", "seal_units_sum")],
        [(DOCSIG, "dc", "o.delivery_id = dc.anchor_id"),
         (SCREEN, "rs", "o.delivery_id = rs.anchor_id"),
         (SEALM, "sm", "o.delivery_id = sm.anchor_id")])

    # P10: windows, the general outer join, the argmax pair, the herring
    mv5(f"{P}_{T4}_lane_rank",
        ["o.delivery_id AS anchor_id",
         CO("cb.best_delivery_id", "0", "courier_best_delivery"),
         CO("cb.best_load", "0.0", "courier_best_load"),
         CO("cb.best_lane", "''", "courier_best_lane"),
         CO("cg.gap_n", "0", "courier_gap_n"),
         CO("cg.gap_avg_s", "0.0", "courier_gap_avg_s"),
         CO("cg.gap_total_s", "0.0", "courier_gap_total_s"),
         CO("hb.hold_n", "0", "hold_n"),
         CO("hb.hold_n_b5", "0", "hold_n_b5"),
         CO("hb.hold_note1", "false", "hold_note1"),
         CO("sp.shift_pick_kind", "''", "shift_pick_kind"),
         CO("sp.shift_pick_units", "0.0", "shift_pick_units"),
         CO("sp.peak_units", "0.0", "shift_peak_units"),
         CO("dt.dock_n", "0", "dock_n"),
         CO("dt.dock_bad", "false", "dock_bad"),
         CO("lc.leg_n", "0", "leg_courier_n"),
         CO("lc.leg_load", "0.0", "leg_courier_load")],
        [(BEST, "cb", "cb.courier_id = o.courier_id"),
         (GAP, "cg", "cg.courier_id = o.courier_id"),
         (HOLDROLL, "hb", "hb.courier_id = o.courier_id"),
         (PEAK, "sp", "o.delivery_id = sp.anchor_id"),
         (DOCK, "dt", "o.delivery_id = dt.anchor_id"),
         (LEGCOUR, "lc", "lc.courier_id = o.courier_id")])

    # P11: the DISTINCT family, the basic aggregate, the distributive pivot
    mv5(f"{P}_{T4}_leg_totals",
        ["o.delivery_id AS anchor_id",
         CO("ll.lane_leg_n", "0", "lane_leg_n"),
         CO("ll.lane_leg_load", "0.0", "lane_leg_load"),
         CO("lz.lane_tier_n", "0", "lane_tier_n"),
         CO("cd.first_call_mode", "''", "first_call_mode"),
         CO("cd.n_call_payloads", "0", "n_call_payloads"),
         CO("pl.postal_load", "0.0", "postal_load"),
         CO("pl.postal_n", "0", "postal_n"),
         CO("pl.postal_bad", "0", "postal_bad"),
         CO("pl.postal_risk", "0.0", "postal_risk")],
        [(LEGLANE, "ll", "ll.lane_code = o.lane_code"),
         (LANETIER, "lz", "lz.lane_code = o.lane_code"),
         (DIGEST, "cd", "o.delivery_id = cd.anchor_id"),
         (POSTAL, "pl", "o.delivery_id = pl.anchor_id")])

    emit("-- ============ v5 serving index ============")
    emit(f"CREATE INDEX idx_{P}_{T4}_route_audit "
         f"ON {q(f'{P}_{T4}_route_audit')} (anchor_id);")
    emit()

# ==================================================================
# v6 constructions (C24-C27), appended so the v5 environment above
# stays byte-identical under --v5
# ==================================================================
CHAIN = f"{P}_{T3}_yard_chain"
WATCH = f"{P}_{T3}_yard_watch"
SPAN = f"{P}_{T3}_first_span"
TOLLJ = f"{P}_{T2}_toll_join"
TOLLR = f"{P}_{T3}_toll_promo"

# The yard tables cover the kiosk-app slice of the fact history (one row per
# delivery, plus a duplicate-key tail and a NULL-key tail). The duplicates and
# the NULLs are the exactness seeds the USING-to-ON and the local-predicate
# rewrites have to survive.
YARD_MOD, YARD_RES = 5, 3           # source_app = APPS[3] is g % 5 = 3
YARD_APP = APPS[3]
C26_FLOOR = "100.0"                 # load_units >= this: half the history
C26_HINT = 1                        # zero hierarchy levels: the cheapest
                                    # rendering, and the same whole-partition
                                    # recompute the window form already had,
                                    # so it is no freshness regression against
                                    # what it replaces. Measured on the rig:
                                    # hint 1 = 5.5 MB, hint 32768 (the true
                                    # max group is 20,834, so that is the
                                    # headroom-correct value) = 47.4 MB,
                                    # the window gadget = 59.0 MB.
TOLL_STRIDE = 7                     # one toll row per 7 deliveries
N_LEDGER_ROUTE = 300                # ledger dimension sizes. The route
N_LEDGER_RATE = 317                 # dimension carries two rows per key, so
N_LEDGER_ZONE = 211                 # the first join stage already expands.
N_HOLDERS = 20_000 // _SC           # wide holder dimension (late
N_CARRIER_W = 3_000 // _SC          # materialization) and its carrier side
C31_CUT = "0.01"                    # 1% of the history: the selective driver
N_RELAY_KEYS = 1_000 // _SC         # predicate, against 1,000-key right sides

if V6:
    emit("-- ============ v6 base tables ============")
    emit()
    v6_table = v5_table
    v6_table("yard_moves", [
        "delivery_id pg_catalog.int4",
        "move_kind pg_catalog.text",
        "move_units pg_catalog.float8"])
    v6_table("yard_docks", [
        "delivery_id pg_catalog.int4",
        "dock_code pg_catalog.text",
        "dock_units pg_catalog.float8"])
    v6_table("yard_seals", [
        "delivery_id pg_catalog.int4",
        "seal_grade pg_catalog.text",
        "seal_units pg_catalog.float8"])
    v6_table("toll_grades", [
        "delivery_id pg_catalog.int4",
        "toll_grade pg_catalog.text",
        "toll_units pg_catalog.float8"])

    emit("-- ============ v6 data ============")
    emit()
    for tbl, kindcol, unitcol, kpfx, kmod, nullmod, dupmod, dcode, umod, udiv in [
            ("yard_moves", "move_kind", "move_units", "mk", 6, 997, 211,
             "mk9", 400, 7.0),
            ("yard_docks", "dock_code", "dock_units", "dk", 5, 1013, 223,
             "dk2", 300, 5.0),
            ("yard_seals", "seal_grade", "seal_units", "sg", 7, 1019, 227,
             "sg9", 500, 9.0)]:
        emit(f"""INSERT INTO {q(tbl)}
SELECT
    CASE WHEN g % {nullmod} = {YARD_RES} THEN NULL ELSE g END,
    '{kpfx}' || (g % {kmod})::pg_catalog.text,
    ((g % {umod}) / {udiv})::pg_catalog.float8
FROM generate_series(1, {N_DELIV}) AS g
WHERE g % {YARD_MOD} = {YARD_RES};
""")
        emit(f"""INSERT INTO {q(tbl)}
SELECT
    g,
    '{dcode}',
    1.5::pg_catalog.float8
FROM generate_series(1, {N_DELIV}) AS g
WHERE g % {YARD_MOD} = {YARD_RES}
  AND g % {dupmod} = 0;
""")
    emit(f"""INSERT INTO {q('toll_grades')}
SELECT
    g * {TOLL_STRIDE},
    'tg' || (g % 9)::pg_catalog.text,
    ((g % 700) / 11.0)::pg_catalog.float8
FROM generate_series(1, {N_DELIV // TOLL_STRIDE}) AS g;
""")

    emit("-- ============ v6 yard views ============")
    emit()

    # ---- C24: a VOJ stack cut by USING --------------------------------
    # The driver's leftmost column is courier_id and the join column is
    # delivery_id, so the first USING join plans a Project the VOJ collector
    # will not walk through: the bottom join drops to the per-join equi shape
    # and only two Thresholds survive. Writing ON restores all three.
    view_open(CHAIN)
    STATS["joins"] += 3
    STATS["left"] += 3
    STATS["filters"] += 1
    _chain_j = (
        """LEFT JOIN {m} AS m
    ON m.delivery_id = d.delivery_id
LEFT JOIN {k} AS k
    ON k.delivery_id = d.delivery_id
LEFT JOIN {s} AS s
    ON s.delivery_id = d.delivery_id""" if REF else
        """LEFT JOIN {m} AS m
    USING (delivery_id)
LEFT JOIN {k} AS k
    USING (delivery_id)
LEFT JOIN {s} AS s
    USING (delivery_id)""").format(m=q("yard_moves"), k=q("yard_docks"),
                                   s=q("yard_seals"))
    emit(f"""SELECT
    d.courier_id,
    pg_catalog.count(*) AS yard_n,
    pg_catalog.sum(
        COALESCE(m.move_units, 0)
        + COALESCE(k.dock_units, 0)
        + COALESCE(s.seal_units, 0))::pg_catalog.float8 AS yard_units,
    pg_catalog.count(*) FILTER (WHERE m.move_kind IS NULL) AS yard_nomove
FROM (
    SELECT
        courier_id,
        delivery_id,
        load_units
    FROM {q(FACTW)}
    WHERE source_app = '{YARD_APP}'
) AS d
{_chain_j}
GROUP BY d.courier_id;""")
    emit()

    # ---- C25: a VOJ stack cut by a local ON predicate ------------------
    # The SECOND join's ON carries a local predicate on its own side, which
    # makes the whole lowering attempt bail: no Threshold survives at all.
    # Pushing the predicate into a derived table restores all three.
    view_open(WATCH)
    STATS["joins"] += 3
    STATS["left"] += 3
    _watch_k = (f"""LEFT JOIN (
    SELECT *
    FROM {q('yard_docks')}
    WHERE dock_code = 'dk2'
) AS k
    ON k.delivery_id = d.delivery_id""" if REF else
                f"""LEFT JOIN {q('yard_docks')} AS k
    ON k.delivery_id = d.delivery_id
    AND k.dock_code = 'dk2'""")
    emit(f"""SELECT
    d.courier_id,
    pg_catalog.count(*) AS watch_n,
    pg_catalog.sum(
        COALESCE(m.move_units, 0)
        + COALESCE(k.dock_units, 0)
        + COALESCE(s.seal_units, 0))::pg_catalog.float8 AS watch_units
FROM (
    SELECT
        courier_id,
        delivery_id,
        load_units
    FROM {q(FACTW)}
    WHERE source_app = '{YARD_APP}'
) AS d
LEFT JOIN {q('yard_moves')} AS m
    ON m.delivery_id = d.delivery_id
{_watch_k}
LEFT JOIN {q('yard_seals')} AS s
    ON s.delivery_id = d.delivery_id
GROUP BY d.courier_id;""")
    emit()

    # ---- C26: FIRST_VALUE over its own ordering column -----------------
    # first_value(created_at) ORDER BY created_at is min(created_at), and
    # created_at carries no NULLs. last_value(load_units) under the DEFAULT
    # frame is the CURRENT row's value, not the partition maximum, so its
    # only exact rewrite is the bare column. The two fuse into one gadget, so
    # the gadget disappears only when both are rewritten.
    view_open(SPAN)
    if REF:
        emit(f"""SELECT
    courier_id,
    pg_catalog.count(*) AS span_n,
    pg_catalog.min(created_at) AS span_first_at,
    pg_catalog.sum(load_units)::pg_catalog.float8 AS span_last_load
FROM (
    SELECT
        courier_id,
        delivery_id,
        created_at,
        load_units
    FROM {q(FACTW)}
    WHERE load_units >= {C26_FLOOR}
) AS h
GROUP BY courier_id
OPTIONS (AGGREGATE INPUT GROUP SIZE = {C26_HINT});""")
        STATS["hints"] += 1
    else:
        emit(f"""SELECT
    courier_id,
    pg_catalog.count(*) AS span_n,
    pg_catalog.min(first_at) AS span_first_at,
    pg_catalog.sum(run_last)::pg_catalog.float8 AS span_last_load
FROM (
    SELECT
        h.courier_id,
        pg_catalog.first_value(h.created_at) OVER (
            PARTITION BY h.courier_id
            ORDER BY h.created_at, h.delivery_id) AS first_at,
        pg_catalog.last_value(h.load_units) OVER (
            PARTITION BY h.courier_id
            ORDER BY h.created_at, h.delivery_id) AS run_last
    FROM (
        SELECT
            courier_id,
            delivery_id,
            created_at,
            load_units
        FROM {q(FACTW)}
        WHERE load_units >= {C26_FLOOR}
    ) AS h
) AS z
GROUP BY courier_id;""")
    emit()

    # ---- C27: the equi pushdown gap (preserving side) ------------------
    # The consumer's WHERE sits above the LEFT JOIN, and the matched-key
    # Distinct blocks it from reaching the preserving read, so the join reads
    # the whole fact history and `Source deliveries` carries no filter= line.
    # Nothing indexes the preserving relation, so wrapping it in a filtered
    # derived table is the exact fix.
    view_open(TOLLJ)
    STATS["joins"] += 1
    STATS["left"] += 1
    _toll_pre = (f"""(
    SELECT *
    FROM {q(FACTW)}
    WHERE promo_code IS NOT NULL
) AS o""" if REF else f"""{q(FACTW)} AS o""")
    emit(f"""SELECT
    o.delivery_id,
    o.courier_id,
    o.promo_code,
    o.load_units,
    t.toll_grade,
    t.toll_units
FROM {_toll_pre}
LEFT JOIN {q('toll_grades')} AS t
    ON t.delivery_id = o.delivery_id;""")
    emit()

    view_open(TOLLR)
    STATS["filters"] += 1
    emit(f"""SELECT
    courier_id,
    pg_catalog.count(*) AS toll_n,
    pg_catalog.sum(COALESCE(toll_units, 0))::pg_catalog.float8 AS toll_units,
    pg_catalog.count(*) FILTER (WHERE toll_grade IS NULL) AS toll_missing
FROM {q(TOLLJ)}
WHERE promo_code IS NOT NULL
GROUP BY courier_id;""")
    emit()

    emit("-- ============ v6 terminal materialized view ============")
    emit()
    mv5(f"{P}_{T4}_yard_board",
        ["o.delivery_id AS anchor_id",
         CO("yc.yard_n", "0", "yard_n"),
         CO("yc.yard_units", "0.0", "yard_units"),
         CO("yc.yard_nomove", "0", "yard_nomove"),
         CO("yw.watch_n", "0", "watch_n"),
         CO("yw.watch_units", "0.0", "watch_units"),
         CO("fs.span_n", "0", "span_n"),
         "fs.span_first_at AS span_first_at",
         CO("fs.span_last_load", "0.0", "span_last_load"),
         CO("tp.toll_n", "0", "toll_n"),
         CO("tp.toll_units", "0.0", "toll_units"),
         CO("tp.toll_missing", "0", "toll_missing")],
        [(CHAIN, "yc", "yc.courier_id = o.courier_id"),
         (WATCH, "yw", "yw.courier_id = o.courier_id"),
         (SPAN, "fs", "fs.courier_id = o.courier_id"),
         (TOLLR, "tp", "tp.courier_id = o.courier_id")])
    emit("-- ============ v6 subquery-rewrite tables ============")
    emit()
    v6_table("band_allow", ["band_id pg_catalog.int4"])
    v6_table("carrier_links", [
        "link_id pg_catalog.int4",
        "carrier_code pg_catalog.text",
        "class_name pg_catalog.text"])
    v6_table("route_tags", [
        "delivery_id pg_catalog.int4",
        "tag_list pg_catalog.text[]"])
    emit(f"""INSERT INTO {q('band_allow')}
SELECT (g - 1) * 2
FROM generate_series(1, 10) AS g;
""")
    # carrier_links repeats each carrier_code, which is what makes flattening
    # the nested EXISTS into a JOIN a row-multiplying mistake rather than a
    # style choice.
    emit(f"""INSERT INTO {q('carrier_links')}
SELECT
    g,
    'AR' || ((g * 3) % {N_ALT_MOD})::pg_catalog.text,
    'class_' || (g % 5)::pg_catalog.text
FROM generate_series(1, {9_000 // _SC}) AS g;
""")
    emit(f"""INSERT INTO {q('carrier_links')}
SELECT
    100000 + g,
    'AR' || ((g * 3) % {N_ALT_MOD})::pg_catalog.text,
    'class_' || ((g + 2) % 5)::pg_catalog.text
FROM generate_series(1, {3_000 // _SC}) AS g;
""")
    # Every tag list repeats two fixed lanes, so the row's own lane can appear
    # twice: that is the duplicate the unnest rewrite has to DISTINCT away.
    emit(f"""INSERT INTO {q('route_tags')}
SELECT
    d.delivery_id,
    ARRAY[
        '{LANES[0]}',
        '{LANES[1]}',
        (ARRAY[{','.join(f"'{l}'" for l in LANES)}])[1 + d.delivery_id % 8],
        'tag_generic']
FROM {q('deliveries')} AS d
WHERE d.courier_id >= 38
  AND d.delivery_id % {ANCHOR_MOD} < 3;
""")

    emit("-- ============ v6 subquery probe views ============")
    emit()

    # ---- C28a: a subquery in a LEFT JOIN's ON (rewrite 3) --------------
    # The subquery makes the ON a Theta predicate, which forces the GENERAL
    # outer-join lowering: an all-column Distinct over the 16-column spine.
    view_open(f"{P}_{T2}_band_probe")
    STATS["joins"] += 1
    STATS["left"] += 1
    if REF:
        emit(f"""WITH allowed AS (
    SELECT
        b.band_id,
        b.band_label
    FROM {q('rate_bands')} AS b
    WHERE b.band_id IN (
        SELECT a.band_id
        FROM {q('band_allow')} AS a)
)
SELECT
    o.delivery_id AS anchor_id,
    a.band_label AS probe_band
FROM {q(SPINE)} AS o
LEFT JOIN allowed AS a
    ON a.band_id
        = pg_catalog.floor(o.load_units / 10.0)::pg_catalog.int4;""")
    else:
        emit(f"""SELECT
    o.delivery_id AS anchor_id,
    b.band_label AS probe_band
FROM {q(SPINE)} AS o
LEFT JOIN {q('rate_bands')} AS b
    ON b.band_id
        = pg_catalog.floor(o.load_units / 10.0)::pg_catalog.int4
    AND b.band_id IN (
        SELECT a.band_id
        FROM {q('band_allow')} AS a);""")
    emit()

    # ---- C28b: IN over an aggregating subquery (rewrite 4) -------------
    # A top-level WHERE conjunct that is NOT the false friend: the outer keys
    # seed the aggregate, so the plan carries a Distinct over the outer key,
    # a semijoin into the aggregate's input, and a join back.
    view_open(f"{P}_{T2}_shift_probe")
    STATS["joins"] += 1
    if REF:
        emit(f"""WITH busy AS (
    SELECT s.courier_id
    FROM {q('shift_logs')} AS s
    GROUP BY s.courier_id
    HAVING pg_catalog.count(*) > 4
)
SELECT
    o.delivery_id AS anchor_id,
    o.courier_id AS probe_courier
FROM {q(SPINE)} AS o
JOIN busy AS b
    ON b.courier_id = o.courier_id;""")
    else:
        emit(f"""SELECT
    o.delivery_id AS anchor_id,
    o.courier_id AS probe_courier
FROM {q(SPINE)} AS o
WHERE o.courier_id IN (
    SELECT s.courier_id
    FROM {q('shift_logs')} AS s
    GROUP BY s.courier_id
    HAVING pg_catalog.count(*) > 4);""")
    emit()

    # ---- C28c: nested IN (rewrite 5), a MEASURED HERRING ---------------
    # v26.38.1 already decorrelates the nested IN into two clean semijoins,
    # so the correlated-EXISTS rewrite is plan-identical and measures 0.
    # The lesson is the trap: flattening either level into a JOIN over
    # carrier_links, whose carrier_code repeats, multiplies rows.
    view_open(f"{P}_{T2}_link_probe")
    emit(f"""SELECT
    o.delivery_id AS anchor_id,
    o.alt_ref AS probe_alt_ref
FROM {q(SPINE)} AS o
WHERE o.alt_ref IN (
    SELECT cl.carrier_code
    FROM {q('carrier_links')} AS cl
    WHERE cl.class_name IN (
        SELECT c.code_class
        FROM {q('carrier_codes')} AS c
        WHERE c.code_weight > 3.0));""")
    emit()

    # ---- C28d: = ANY(<list column>) (rewrite 6), a MEASURED HERRING ----
    # The Distinct and the join-back are keyed on (lane_code, tag_list), so
    # the list rides the arrangement, which is the signature the skill
    # teaches. Measured on this data the unnest rewrite is BIGGER, so the
    # correct action is to measure it and leave the list form in place. The
    # trap is the rewrite WITHOUT its DISTINCT.
    view_open(f"{P}_{T2}_tag_probe")
    STATS["joins"] += 1
    emit(f"""SELECT
    o.delivery_id AS anchor_id,
    o.lane_code AS probe_lane
FROM {q(SPINE)} AS o
JOIN {q('route_tags')} AS rt
    ON rt.delivery_id = o.delivery_id
WHERE o.lane_code = ANY(rt.tag_list);""")
    emit()

    # ---- C28e: correlated aggregate, equality correlation (rewrite 8) --
    # curfew_windows covers only part of the courier population, so the
    # empty groups are real: the scalar subquery yields 0 where a plain
    # LEFT JOIN yields NULL.
    view_open(f"{P}_{T2}_curfew_probe")
    if REF:
        STATS["joins"] += 1
        STATS["left"] += 1
        emit(f"""WITH m AS (
    SELECT
        cw.courier_id,
        pg_catalog.count(*) AS curfew_n
    FROM {q('curfew_windows')} AS cw
    GROUP BY cw.courier_id
)
SELECT
    o.delivery_id AS anchor_id,
    COALESCE(m.curfew_n, 0) AS probe_curfew_n
FROM {q(SPINE)} AS o
LEFT JOIN m
    ON m.courier_id = o.courier_id;""")
        STATS["coalesce"] += 1
    else:
        emit(f"""SELECT
    o.delivery_id AS anchor_id,
    (
        SELECT pg_catalog.count(*)
        FROM {q('curfew_windows')} AS cw
        WHERE cw.courier_id = o.courier_id
    ) AS probe_curfew_n
FROM {q(SPINE)} AS o;""")
    emit()

    # ---- C28f: the same subquery text in two UNION branches (rewrite 9) -
    # CSE matches structurally identical subtrees, and decorrelation gives
    # the two copies different shapes, so the aggregate is built twice.
    view_open(f"{P}_{T2}_union_probe")
    _u_sub = f"""(
    SELECT s.courier_id
    FROM {q('shift_logs')} AS s
    GROUP BY s.courier_id
    HAVING pg_catalog.count(*) > 4)"""
    if REF:
        STATS["joins"] += 2
        emit(f"""WITH heavy AS (
    SELECT s.courier_id
    FROM {q('shift_logs')} AS s
    GROUP BY s.courier_id
    HAVING pg_catalog.count(*) > 4
)
SELECT
    'completed' AS probe_arm,
    o.delivery_id AS anchor_id
FROM {q(SPINE)} AS o
JOIN heavy AS h
    ON h.courier_id = o.courier_id
WHERE o.phase = 'completed'
UNION ALL
SELECT
    'failed',
    o.delivery_id
FROM {q(SPINE)} AS o
JOIN heavy AS h
    ON h.courier_id = o.courier_id
WHERE o.phase = 'failed';""")
    else:
        emit(f"""SELECT
    'completed' AS probe_arm,
    o.delivery_id AS anchor_id
FROM {q(SPINE)} AS o
WHERE o.phase = 'completed'
  AND o.courier_id IN {_u_sub}
UNION ALL
SELECT
    'failed',
    o.delivery_id
FROM {q(SPINE)} AS o
WHERE o.phase = 'failed'
  AND o.courier_id IN {_u_sub};""")
    emit()

    view_open(f"{P}_{T2}_union_tally")
    emit(f"""SELECT
    anchor_id,
    pg_catalog.count(*) AS probe_arms
FROM {q(f'{P}_{T2}_union_probe')}
GROUP BY anchor_id;""")
    emit()

    # ---- C28g: IN (SELECT generate_series(a, b)) (rewrite 10) ----------
    # depot_id is an integer column, so BETWEEN is exact. load_units is not,
    # and the sibling probe below is the herring: a fractional value is in
    # the range but not in the series.
    view_open(f"{P}_{T2}_series_probe")
    if REF:
        emit(f"""SELECT
    o.delivery_id AS anchor_id,
    o.depot_id AS probe_depot
FROM {q(SPINE)} AS o
WHERE o.depot_id BETWEEN 10 AND 40;""")
    else:
        emit(f"""SELECT
    o.delivery_id AS anchor_id,
    o.depot_id AS probe_depot
FROM {q(SPINE)} AS o
WHERE o.depot_id IN (
    SELECT generate_series(10, 40));""")
    emit()

    view_open(f"{P}_{T2}_float_probe")
    emit(f"""SELECT
    o.delivery_id AS anchor_id,
    o.load_units AS probe_units
FROM {q(SPINE)} AS o
WHERE o.load_units IN (
    SELECT generate_series(1, 60));""")
    emit()

    emit("-- ============ v6 subquery terminal materialized view ============")
    emit()
    mv5(f"{P}_{T4}_ref_probe",
        ["o.delivery_id AS anchor_id",
         CO("bp.probe_band", "''", "probe_band"),
         CO("sp.probe_courier", "0", "probe_courier"),
         CO("lp.probe_alt_ref", "''", "probe_alt_ref"),
         CO("tp.probe_lane", "''", "probe_lane"),
         CO("cp.probe_curfew_n", "0", "probe_curfew_n"),
         CO("up.probe_arms", "0", "probe_arms"),
         CO("rp.probe_depot", "-1", "probe_depot"),
         CO("fp.probe_units", "0.0", "probe_units")],
        [(f"{P}_{T2}_band_probe", "bp", "bp.anchor_id = o.delivery_id"),
         (f"{P}_{T2}_shift_probe", "sp", "sp.anchor_id = o.delivery_id"),
         (f"{P}_{T2}_link_probe", "lp", "lp.anchor_id = o.delivery_id"),
         (f"{P}_{T2}_tag_probe", "tp", "tp.anchor_id = o.delivery_id"),
         (f"{P}_{T2}_curfew_probe", "cp", "cp.anchor_id = o.delivery_id"),
         (f"{P}_{T2}_union_tally", "up", "up.anchor_id = o.delivery_id"),
         (f"{P}_{T2}_series_probe", "rp", "rp.anchor_id = o.delivery_id"),
         (f"{P}_{T2}_float_probe", "fp", "fp.anchor_id = o.delivery_id")])
    emit("-- ============ v6 ledger tables (delta-flip family) ============")
    emit()
    v6_table("ledger_runs", [
        "run_id pg_catalog.int4",
        "delivery_id pg_catalog.int4",
        "courier_id pg_catalog.int4",
        "route_code pg_catalog.text",
        "rate_code pg_catalog.text",
        "zone_code pg_catalog.text",
        "run_units pg_catalog.float8"])
    v6_table("ledger_routes", [
        "route_code pg_catalog.text",
        "route_label pg_catalog.text",
        "route_note pg_catalog.text"])
    v6_table("ledger_rates", [
        "rate_code pg_catalog.text",
        "rate_label pg_catalog.text",
        "rate_note pg_catalog.text"])
    v6_table("ledger_zones", [
        "zone_code pg_catalog.text",
        "zone_label pg_catalog.text",
        "zone_note pg_catalog.text"])
    emit(f"""INSERT INTO {q('ledger_runs')}
SELECT
    g,
    g * 10 + 7,
    38 + ((g * 7) % {N_COUR - 38}),
    'rt' || (g % {N_LEDGER_ROUTE})::pg_catalog.text,
    'ra' || (g % {N_LEDGER_RATE})::pg_catalog.text,
    'zn' || (g % {N_LEDGER_ZONE})::pg_catalog.text,
    ((g % 900) / 7.0)::pg_catalog.float8
FROM generate_series(1, {100_000 // _SC}) AS g;
""")
    # Two rows per route_code, so the first join stage already exceeds the
    # driver: that expansion is what the differential intermediates hold.
    emit(f"""INSERT INTO {q('ledger_routes')}
SELECT
    'rt' || (g % {N_LEDGER_ROUTE})::pg_catalog.text,
    'route_label_' || repeat('r', 28) || (g % {N_LEDGER_ROUTE})::pg_catalog.text,
    'route_note_' || repeat('n', 24) || (g % 17)::pg_catalog.text
FROM generate_series(1, {N_LEDGER_ROUTE * 2}) AS g;
""")
    emit(f"""INSERT INTO {q('ledger_rates')}
SELECT
    'ra' || (g - 1)::pg_catalog.text,
    'rate_label_' || repeat('a', 30) || (g - 1)::pg_catalog.text,
    'rate_note_' || repeat('m', 26) || (g % 13)::pg_catalog.text
FROM generate_series(1, {N_LEDGER_RATE}) AS g;
""")
    emit(f"""INSERT INTO {q('ledger_zones')}
SELECT
    'zn' || (g - 1)::pg_catalog.text,
    'zone_label_' || repeat('z', 30) || (g - 1)::pg_catalog.text,
    'zone_note_' || repeat('q', 26) || (g % 11)::pg_catalog.text
FROM generate_series(1, {N_LEDGER_ZONE}) AS g;
""")

    # ---- C29: flipping a differential join to delta --------------------
    # Four inputs, the driver probed on THREE different columns, so the
    # differential cascade keeps two JoinStage intermediates at expansion
    # scale and accumulated width. The flip is all-or-nothing: indexes on
    # only some of the probe keys change nothing.
    emit("-- ============ v6 ledger view ============")
    emit()
    view_open(f"{P}_{T2}_ledger_legs")
    STATS["joins"] += 3
    STATS["filters"] += 2
    emit(f"""SELECT
    r.courier_id,
    pg_catalog.count(*) AS ledger_n,
    pg_catalog.sum(r.run_units)::pg_catalog.float8 AS ledger_units,
    pg_catalog.sum(
        pg_catalog.length(rt.route_label)
        + pg_catalog.length(ra.rate_label)
        + pg_catalog.length(z.zone_label))::pg_catalog.int8 AS ledger_tag_len,
    pg_catalog.count(*) FILTER (WHERE rt.route_note <> ra.rate_note)
        AS ledger_note_n,
    pg_catalog.count(*) FILTER (WHERE z.zone_note <> ra.rate_note)
        AS ledger_zone_n
FROM {q('ledger_runs')} AS r
JOIN {q('ledger_routes')} AS rt
    ON rt.route_code = r.route_code
JOIN {q('ledger_rates')} AS ra
    ON ra.rate_code = r.rate_code
JOIN {q('ledger_zones')} AS z
    ON z.zone_code = r.zone_code
GROUP BY r.courier_id;""")
    emit()
    if REF:
        emit("-- ============ v6 delta-enabling indexes (reference) ============")
        emit(f"CREATE INDEX idx_ledger_runs_route "
             f"ON {q('ledger_runs')} (route_code);")
        emit(f"CREATE INDEX idx_ledger_runs_rate "
             f"ON {q('ledger_runs')} (rate_code);")
        emit(f"CREATE INDEX idx_ledger_runs_zone "
             f"ON {q('ledger_runs')} (zone_code);")
        emit()
    emit("-- ============ v6 parcel tables (late materialization) ============")
    emit()
    v6_table("holders", [
        "holder_id pg_catalog.int4",
        "carrier_ref pg_catalog.text"] + [
        f"att_{c} pg_catalog.text" for c in "abcdefgh"])
    v6_table("carriers_wide", [
        "carrier_ref pg_catalog.text"] + [
        f"cat_{c} pg_catalog.text" for c in "abcd"])
    v6_table("parcel_units", [
        "unit_id pg_catalog.int4",
        "delivery_id pg_catalog.int4",
        "courier_id pg_catalog.int4",
        "holder_id pg_catalog.int4",
        "unit_units pg_catalog.float8"])
    _hatt = ",\n    ".join(
        f"'h{c}' || repeat('{c}', 40) || (g % {m})::pg_catalog.text"
        for c, m in zip("abcdefgh", (97, 89, 83, 79, 73, 71, 67, 61)))
    emit(f"""INSERT INTO {q('holders')}
SELECT
    g,
    'cw' || (g % {N_CARRIER_W})::pg_catalog.text,
    {_hatt}
FROM generate_series(1, {N_HOLDERS}) AS g;
""")
    _catt = ",\n    ".join(
        f"'c{c}' || repeat('{p}', 40) || (g % {m})::pg_catalog.text"
        for c, p, m in zip("abcd", "pqrs", (53, 47, 43, 41)))
    emit(f"""INSERT INTO {q('carriers_wide')}
SELECT
    'cw' || (g - 1)::pg_catalog.text,
    {_catt}
FROM generate_series(1, {N_CARRIER_W}) AS g;
""")
    emit(f"""INSERT INTO {q('parcel_units')}
SELECT
    g,
    g * 6 + 1,
    38 + ((g * 7) % {N_COUR - 38}),
    1 + ((g * 11) % {N_HOLDERS}),
    ((g % 700) / 9.0)::pg_catalog.float8
FROM generate_series(1, {150_000 // _SC}) AS g;
""")

    emit("-- ============ v6 relay tables (VOJ pushdown gap) ============")
    emit()
    for t, col in (("relay_a", "a_units"), ("relay_b", "b_units"),
                   ("relay_c", "c_units")):
        v6_table(t, ["delivery_id pg_catalog.int4",
                     f"{col} pg_catalog.float8"])
    for t, col, stride, m, d in (("relay_a", "a_units", 3, 400, 7.0),
                                 ("relay_b", "b_units", 5, 300, 5.0),
                                 ("relay_c", "c_units", 7, 500, 9.0)):
        emit(f"""INSERT INTO {q(t)}
SELECT
    g * 1000 + {stride},
    ((g % {m}) / {d})::pg_catalog.float8
FROM generate_series(1, {N_RELAY_KEYS}) AS g;
""")

    emit("-- ============ v6 parcel and relay views ============")
    emit()

    # ---- C30: late materialization -------------------------------------
    # The wide holder payload is consumed, so projection pushdown cannot
    # prune it, and it rides the intermediate of the SECOND join at
    # accumulated width. Routing the chain through a narrow (primary key,
    # foreign key) view and joining the wide relation once, by primary key,
    # at the end is the documented fix.
    if REF:
        view_open(f"{P}_{T2}_holder_keys")
        emit(f"""SELECT
    holder_id,
    carrier_ref
FROM {q('holders')};""")
        emit()
    view_open(f"{P}_{T2}_parcel_profile")
    _wsum = """pg_catalog.sum(
        pg_catalog.length(h.att_a) + pg_catalog.length(h.att_b)
        + pg_catalog.length(h.att_c) + pg_catalog.length(h.att_d)
        + pg_catalog.length(h.att_e) + pg_catalog.length(h.att_f)
        + pg_catalog.length(h.att_g) + pg_catalog.length(h.att_h)
        + pg_catalog.length(c.cat_a) + pg_catalog.length(c.cat_b)
        + pg_catalog.length(c.cat_c)
        + pg_catalog.length(c.cat_d))::pg_catalog.int8 AS parcel_width"""
    if REF:
        STATS["joins"] += 3
        emit(f"""SELECT
    p.courier_id,
    pg_catalog.count(*) AS parcel_n,
    pg_catalog.sum(p.unit_units)::pg_catalog.float8 AS parcel_units,
    {_wsum}
FROM {q('parcel_units')} AS p
JOIN {q(f'{P}_{T2}_holder_keys')} AS hk
    ON hk.holder_id = p.holder_id
JOIN {q('carriers_wide')} AS c
    ON c.carrier_ref = hk.carrier_ref
JOIN {q('holders')} AS h
    ON h.holder_id = hk.holder_id
GROUP BY p.courier_id;""")
    else:
        STATS["joins"] += 2
        emit(f"""SELECT
    p.courier_id,
    pg_catalog.count(*) AS parcel_n,
    pg_catalog.sum(p.unit_units)::pg_catalog.float8 AS parcel_units,
    {_wsum}
FROM {q('parcel_units')} AS p
JOIN {q('holders')} AS h
    ON h.holder_id = p.holder_id
JOIN {q('carriers_wide')} AS c
    ON c.carrier_ref = h.carrier_ref
GROUP BY p.courier_id;""")
    emit()

    # ---- C31: the VOJ pushdown gap -------------------------------------
    # A clean three-deep VOJ stack off the fact TABLE. The consumer's
    # selective predicate filters the main preserving copy but NOT the
    # distinct-keys copy that builds the null augmentation, so every
    # Threshold runs at whole-history scale and `Source deliveries` carries
    # no filter= line. The right sides hold far fewer keys than the filtered
    # driver asks about, which is the side of the crossover where pushing
    # the predicate down wins.
    view_open(f"{P}_{T2}_relay_stack")
    STATS["joins"] += 3
    STATS["left"] += 3
    _relay_from = (f"""(
    SELECT *
    FROM {q('deliveries')}
    WHERE risk_score < {C31_CUT}
) AS d""" if REF else f"{q('deliveries')} AS d")
    emit(f"""SELECT
    d.delivery_id,
    d.courier_id,
    d.risk_score,
    a.a_units,
    b.b_units,
    c.c_units
FROM {_relay_from}
LEFT JOIN {q('relay_a')} AS a
    ON a.delivery_id = d.delivery_id
LEFT JOIN {q('relay_b')} AS b
    ON b.delivery_id = d.delivery_id
LEFT JOIN {q('relay_c')} AS c
    ON c.delivery_id = d.delivery_id;""")
    emit()

    view_open(f"{P}_{T3}_relay_hot")
    emit(f"""SELECT
    courier_id,
    pg_catalog.count(*) AS relay_n,
    pg_catalog.sum(
        COALESCE(a_units, 0)
        + COALESCE(b_units, 0)
        + COALESCE(c_units, 0))::pg_catalog.float8 AS relay_units
FROM {q(f'{P}_{T2}_relay_stack')}
WHERE risk_score < {C31_CUT}
GROUP BY courier_id;""")
    emit()

    emit("-- ============ v6 ledger terminal materialized view ============")
    emit()
    mv5(f"{P}_{T4}_ledger_board",
        ["o.delivery_id AS anchor_id",
         CO("ll.ledger_n", "0", "ledger_n"),
         CO("ll.ledger_units", "0.0", "ledger_units"),
         CO("ll.ledger_tag_len", "0", "ledger_tag_len"),
         CO("ll.ledger_note_n", "0", "ledger_note_n"),
         CO("ll.ledger_zone_n", "0", "ledger_zone_n"),
         CO("pp.parcel_n", "0", "parcel_n"),
         CO("pp.parcel_units", "0.0", "parcel_units"),
         CO("pp.parcel_width", "0", "parcel_width"),
         CO("rh.relay_n", "0", "relay_n"),
         CO("rh.relay_units", "0.0", "relay_units")],
        [(f"{P}_{T2}_ledger_legs", "ll", "ll.courier_id = o.courier_id"),
         (f"{P}_{T2}_parcel_profile", "pp", "pp.courier_id = o.courier_id"),
         (f"{P}_{T3}_relay_hot", "rh", "rh.courier_id = o.courier_id")])

# ==================================================================
# Output
# ==================================================================
_GENTAG = 'v4' if args.v4 else ('v5' if args.v5 else 'v6')
MANIFEST = f"""{_GENTAG} construction manifest (schema {S}, seed {args.seed})
C1  K1=(courier_id,depot_id): {P}_{T3}_depot_history [P2], {P}_{T3}_depot_recency [P2],
    {P}_{T3}_depot_moment [P3], {P}_{T3}_owner_top3 [P8 LATERAL].
    K2=(courier_id,lane_code): {P}_{T3}_lane_history [P4], {P}_{T3}_lane_first [P4],
    {P}_{T2}_shift_mix lane_hist CTE [P8].
C2  {COURW}: fat cols bio_note/address_full/device_fingerprint; consumers join
    courier_id, use rank_grade/region_code/joined_at only.
C3  idx_couriers_home ON couriers(home_depot_id), dead and wide.
C4  {MEGA}: hist_eff / hist_cat divergent twin scans of hxm.
C5a {P}_{T2}_gw_outcome (kind 'quote', 22 extractions, raw_payload CONSUMED by
    {P}_{T4}_saga_vector).
C5b {P}_{T2}_gw_probe (kind 'verify', 13 mixed, raw_payload NOT consumed by
    {P}_{T4}_audit_trail).
C6  c6a {P}_{T2}_scan_trail pick 65536 (true ~40); c6b {P}_{T2}_claim_totals
    tally 4096 (true ~12); c6c {P}_{T2}_dispute_marks tally 65536 (true ~30);
    c6d {MEGA} sl_twin_a 65536 vs sl_twin_b 256 (true ~300; twin_b input is
    hist_cat, landmark needed); c6e {P}_{T2}_shift_mix sx_1 256 (true ~4k
    shift_logs per courier); c6f {P}_{T3}_owner_tally own_extremes UNHINTED
    (30-day slice of the history).
C7  {P}_{T2}_route_flux: 15-min delay_logs window, ratio ~1.1 (leave alone).
C8  {P}_{T3}_owner_pulse over {PAIRS} (ratio target 8-10), estimate only.
C9  deliveries.alt_ref (~4.3% NULL); consumer {P}_{T2}_alt_share; naive shared
    index ON {FACTW}(alt_ref) arms NULL^2 grind on rebuild; fix = NULL-filtered
    boundary + closure audit. 3B arm 2 also touches alt_ref.
C10 {P}_{T3}_lane_first (P4) and {P}_{T2}_delay_bands (P4): grouped over
    spine LEFT JOIN => total per anchor => MV LEFT JOINs convertible to INNER.
NB  the INDF-in-join idiom is NOT reproduced: the planner cross-joins
    IS NOT DISTINCT FROM (empty-key arranges, one-worker 5e9-pair grind,
    measured live), so first-use joins use plain equality instead.
R*  mega hx/hxm shared correctly (R1); single-consumer enrichment views;
    65536 owner-history hints CORRECT (courier 0 = 41.7k rows, dormant);
    {IDENT} already indexed (colleague-redundant target); serving indexes
    produce advisor drop/convert rows.
Data: {N_DELIV} fact rows, {N_COUR} couriers; anchors = active couriers
    (id>=38) with g%{ANCHOR_MOD}<3 (~2% of active rows, ~10k rows), 70% in last
    2h; couriers 0-37 dormant (never anchors, never in spine); alt_ref NULL when
    g%{NULL_MOD}=0; gateway retry storms on ~6 anchors x{STORM_CALLS} calls
    (2048-hint sites correct). The window/history ratio is the
    distribution-matching knob: it sets how much of the cluster's memory sits in
    re-arrangements of the history versus in per-anchor reduce state.
"""

MANIFEST_V5 = f"""C11 {P}_{T2}_doc_codes: scalar subquery whose only outer reference is
    manifest_docs.doc_body (~1.5 kB), so Distinct and both join-back
    arrangements are keyed by the document. Fix = extract the header code
    into a CTE first. R: the ref_known column beside it is a SELECT-list IN
    on two NOT NULL columns and is already a semijoin (leave alone).
C12 {SCREEN} WHERE alt_ref NOT IN (SELECT carrier_code ...): CrossJoin +
    three-valued Union/Negate/Distinct. TRAP: plain NOT EXISTS ADDS the
    NULL-alt_ref rows; exact = alt_ref IS NOT NULL AND NOT EXISTS.
C13 {SCREEN}.ref_listed: SELECT-list IN on the nullable alt_ref. Reduce
    aggregates=[any(...)] over a CrossJoin. TRAP: COALESCE(..., false)
    turns NULL into false on the same rows; exact = a CASE on IS NULL.
C14 {SCREEN}.bands_below: correlation through an inequality only. No
    equi-join exists; no rewrite fixes it. Measure and leave alone.
C15 {BEST}: row_number() = 1 over the 16-column fact wrapper, phase
    completed. Fix = narrow the window's input relation. The DISTINCT ON
    rewrite measures WORSE (the whale courier forces a deep TopK ladder).
C16 {GAP}: lag() over irregularly spaced timestamps on the same wide
    wrapper, phase failed. The self-equi-join rewrite is NOT available;
    only the input slimming applies.
C17 {HOLDR}: LEFT JOIN rate_bands on a cross-side inequality = the general
    outer-join lowering (two full-width Distincts + an all-column
    self-join + an empty-key arrange). Fix = pre-project the preserving
    side AND rewrite the ON to the band-grid equi-join.
C18 {LEGS}: SELECT DISTINCT * over the canceled slice, consumed by
    {LEGCOUR} [P10] and {LEGLANE} [P11]. The DISTINCT is redundant
    (delivery_id unique in the slice). TWIN HERRING: {LEGLANES}'s DISTINCT
    is NOT redundant and dropping it changes results.
C19 {SEALM}: seal_code IS NOT DISTINCT FROM = CrossJoin over two empty-key
    arranges, one-worker grind, negligible memory. Fix = sentinel COALESCE
    equi-join. TRAP: plain = drops the NULL-NULL matches.
C20 {DIGEST}: jsonb_agg of whole gateway payloads, two scalars read out of
    the array. The basic aggregate retains every payload. Fix = narrow the
    aggregate's argument to the consumed field.
C21 {PEAK}: DISTINCT ON pick ordered by mark_units DESC plus a sibling
    un-hinted max(mark_units) over the same relation and key. Fix = delete
    the max and read the value from the pick (hinting it is the lesser
    fix).
C22 dictionary compression: enum-like text columns dominate the biggest
    arrangements. Lever = ALTER CLUSTER {S} SET (EXPERIMENTAL ARRANGEMENT
    COMPRESSION = true), which replaces the replica and rehydrates. Not in
    any reference build.
C23 {POSTAL}: aggregates the spine x fact-history join product on
    postal_code. Fix = pre-aggregate the fact side per postal_code and
    join that; sum(count(*)) promotes to numeric, so cast back to int8.
R   {DOCK} is grouped by anchor_id, so it exports a unique key and the MV's
    LEFT JOIN to it is already collapsed by SemijoinIdempotence: the
    LEFT-to-INNER conversion buys ~0 (proposal item 20).
Data(v5): manifest_docs on anchors with id%{DOC_MOD}<{DOC_RES} (~1.5 kB bodies);
    seal_scans on anchors with id%{SEAL_MOD}={SEAL_RES} joined null-safely against
    {N_SEALREG} registry rows (~8% NULL codes on each side); {N_CARRIER} carrier
    codes (NOT NULL); {N_BANDS} rate bands on a uniform 10-unit grid.
"""


MANIFEST_V6 = f"""C24 {CHAIN}: three-deep LEFT JOIN stack written with USING (delivery_id)
    over a driver whose leftmost column is courier_id. The first join plans
    a Project, the bottom join loses the VOJ lowering, Threshold count 2
    instead of 3. Fix = ON d.delivery_id = r.delivery_id throughout. Seeds:
    ~0.1% NULL right keys and ~0.5% duplicate right keys.
C25 {WATCH}: the same stack written with ON, but the SECOND join carries
    AND k.dock_code = 'dk2' in its ON. The lowering attempt bails and NO
    Threshold survives. Fix = the predicate into a derived table on the
    right side (Threshold count 0 -> 3).
C26 {SPAN}: first_value(created_at) OVER (PARTITION BY courier_id ORDER BY
    created_at, delivery_id) over the heavy-load half of the history, fused
    with last_value(load_units) under the DEFAULT frame. first_value over
    its own ordering column IS min(); last_value under that frame is the
    CURRENT row's value. Fix = min() GROUP BY courier_id with a measured
    hint plus the bare load_units column. TRAP: max(load_units) for the
    last_value changes every courier row.
C27 {TOLLJ} + {TOLLR}: an equi LEFT JOIN to an UNKEYED right side with the
    selective WHERE above it. The matched-key Distinct blocks the predicate
    from the preserving read, so the join reads all {N_DELIV} fact rows and
    Source deliveries shows no filter= line. Fix = wrap the preserving side
    in (SELECT ... WHERE promo_code IS NOT NULL); no index on the
    preserving relation competes for adoption. filter= and pushdown= then
    appear on the Source.
NB  C7, C8, C22 and C23 are still built and still hold their memory, but
    they are OUT OF GRADING SCOPE in v6: the skill's first version drops
    pre-aggregation entirely and drops dictionary compression because the
    feature is experimental.
C28 the remaining subqueries.md rewrites, one small site each over the
    spine. a {P}_{T2}_band_probe (rewrite 3, subquery in a LEFT JOIN's ON:
    an all-column Distinct over the 16-column spine); b
    {P}_{T2}_shift_probe (rewrite 4, IN over an aggregating subquery in a
    top-level WHERE: the outer keys seed the aggregate); c
    {P}_{T2}_link_probe (rewrite 5, nested IN: MEASURED HERRING, already
    two clean semijoins on this release; TRAP = flattening either level
    into a JOIN over carrier_links, whose carrier_code repeats); d
    {P}_{T2}_tag_probe (rewrite 6, = ANY(tag_list): the Distinct and the
    join-back are keyed on the LIST; MEASURED HERRING, the unnest rewrite
    is bigger here; TRAP = that rewrite without its DISTINCT); e
    {P}_{T2}_curfew_probe (rewrite 8, correlated aggregate; TRAP = the
    LEFT JOIN without COALESCE, which turns 0 into NULL on the couriers
    curfew_windows does not cover); f {P}_{T2}_union_probe (rewrite 9, the
    same subquery text in two UNION branches, built twice); g
    {P}_{T2}_series_probe (rewrite 10, IN (SELECT generate_series) on the
    INTEGER depot_id, fixable with BETWEEN) beside {P}_{T2}_float_probe
    (the same shape on the FLOAT load_units, where BETWEEN is NOT
    equivalent: HERRING).
C29 {P}_{T2}_ledger_legs: a four-input join whose driver is probed on
    route_code, rate_code and zone_code, so the plan is type=differential
    and keeps two JoinStage intermediates at expansion scale. Fix = three
    indexes on ledger_runs, one per probe key; the flip is all-or-nothing.
    TRAP: an index on ledger_runs (delivery_id), a key no path probes.
C30 {P}_{T2}_parcel_profile: parcel_units joined to the WIDE holders and
    then to carriers_wide keyed off the holder, so the holder payload
    rides the second join's intermediate at accumulated width. Fix = the
    narrow key-pair view {P}_{T2}_holder_keys, the chain routed through
    it, holders joined once by holder_id at the end.
C31 {P}_{T2}_relay_stack + {P}_{T3}_relay_hot: a clean three-deep VOJ off
    the deliveries table with a 1%-selective predicate ABOVE it. The
    augment-key read is unfiltered, so every Threshold runs at
    whole-history scale and Source deliveries shows no filter= line. Fix =
    the predicate into the driver below the stack.
Data(v6b): carrier_links repeats each carrier_code; route_tags repeats two
    fixed lanes per anchor; curfew_windows covers only part of the courier
    population; ledger_routes carries two rows per route_code; relay_a/b/c
    hold {N_RELAY_KEYS} keys each.
Data(v6): yard_moves / yard_docks / yard_seals cover the kiosk-app slice of
    the history (g % {YARD_MOD} = {YARD_RES}), one row per delivery plus a
    duplicate-key and a NULL-key tail; toll_grades holds one row per
    {TOLL_STRIDE} deliveries across the whole id space.
"""

if args.manifest:
    if args.v4:
        print(MANIFEST)
    elif args.v5:
        print(MANIFEST + MANIFEST_V5)
    else:
        print(MANIFEST + MANIFEST_V5 + MANIFEST_V6)
    sys.exit(0)

def wrap_line(l, width=62):
    out = []
    while len(l) > width:
        head = l[:width]
        cut = -1
        for pat in (", ", " AND ", " || ", " THEN ", " ELSE "):
            i = head.rfind(pat)
            if i > cut and i > 12:
                cut = i + (1 if pat == ", " else len(pat) - 1)
        if cut < 0:
            break
        out.append(l[:cut])
        indent = len(l) - len(l.lstrip())
        l = " " * (indent + 4) + l[cut:].lstrip()
    out.append(l)
    return out

WRAPPED = []
for l in OUT:
    if l.lstrip().startswith("--") or "'" in l and len(l) <= 62:
        WRAPPED.append(l)
    else:
        WRAPPED.extend(wrap_line(l))
sql = "\n".join(WRAPPED) + "\n"
print(sql)

if args.stats:
    nlines = sql.count("\n")
    print(f"-- STATS: lines={nlines} joins~={STATS['joins']} "
          f"left~={STATS['left']} filters~={STATS['filters']} "
          f"hints~={STATS['hints']} picks~={STATS['picks']} "
          f"coalesce~={STATS['coalesce']}", file=sys.stderr)
    print(f"-- text-scan: JOIN={sql.count(' JOIN ')} LEFT_JOIN={sql.count('LEFT JOIN')} "
          f"FILTER={sql.count('FILTER (WHERE')} "
          f"DISTINCT_ON={sql.count('DISTINCT ON (')} "
          f"OPTIONS={sql.count('INPUT GROUP SIZE')} "
          f"COALESCE={sql.count('COALESCE(')} "
          f"mz_now={sql.count('mz_now()')}", file=sys.stderr)
