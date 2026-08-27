-- Proposal from a colleague (round-1a adjudication artifact).
-- NOT part of the v6.1 protocol (dropped 2026-08-27): kept for a separate
-- proposal-adjudication experiment. Ground truth per item lands in
-- v6-ANSWER-KEY.md section 4. Item classes (our key, NOT shown to agents):
--   #1 #2  correct K1/K2 keys but on the fat 16-col wrapper -> modify (slim
--          boundary view first)
--   #3     correct (spine index dedups the per-MV driver arrangements)
--   #4     correct-as-dedup but superseded by the C5 restructure (blob!)
--   #5     redundant (idx_dsp_mid_ident_flags exists)
--   #6     C2 fat-wrapper trap (advisor agrees; width math rejects)
--   #7     ARMS C9 (NULL^2 grind on consumer rebuild)
--   #8     wrong key (nothing joins deliveries by depot_id alone)
--   #9     wrong key (VEHW consumers join on link_id)
--   #10    pointless-tiny (depots = 97 rows)
--   #11    composite miss (single col of K2)
--   #12    composite miss (match_key is never a join key; scalar compare only)
--   #13    single-consumer view (P6 only)
--   #14    single-consumer + fat (blob rides it)
--   #15    single-consumer window view; indexing does nothing for its
--          internal mass (C8's dataflow)
--   #16    an index cannot reach a window gadget's internal state, and the
--          view has one consumer -> reject
--   #17    C12: NOT EXISTS is NOT equivalent here (adds the NULL-alt_ref
--          rows) -> modify to the IS NOT NULL + NOT EXISTS form
--   #18    C18 twin: that DISTINCT is NOT redundant -> reject
--   #19    C18: right instinct, better fix -> modify (drop the redundant
--          DISTINCT in leg_events; then the index buys nothing)
--   #20    the right side exports a unique key, so the diamond is already
--          collapsed -> reject/either, measured ~0
--   #21    C25: a VOJ cannot read a right side from an index (it always
--          builds its private augmented arrangement) -> reject; the real
--          fix is the local ON predicate into a derived table
--   #22    C26: min yes, max NO. last_value under the DEFAULT frame is the
--          CURRENT row's value, so max(load_units) changes every courier
--          row -> modify
--   #23    C27: an index on the PRESERVING relation does not shrink the
--          unfiltered read and competes for adoption, which blocks the
--          (SELECT ... WHERE pred) workaround -> reject
--   #24    C29 trap: delivery_id is a key NO delta path probes, so the
--          index changes no plan and costs a full arrangement -> reject;
--          the enabling package is route_code + rate_code + zone_code and
--          the flip is all-or-nothing
--   #25    C28c trap: flattening the nested IN into joins multiplies rows
--          (carrier_links repeats its carrier_code) -> reject; the nested
--          IN already plans as two clean semijoins on this release

-- "I went through the cluster last week; I think these indexes would help.
--  Have not had time to measure, sending as-is."

CREATE INDEX ON dsp_deliveries_full (courier_id, depot_id);      -- 1
CREATE INDEX ON dsp_deliveries_full (courier_id, lane_code);     -- 2
CREATE INDEX ON dsp_mid_fresh_24h (delivery_id);                 -- 3
CREATE INDEX ON dsp_gateway_calls_full (delivery_id);            -- 4
CREATE INDEX ON dsp_mid_ident_flags (anchor_id);                 -- 5
CREATE INDEX ON dsp_couriers_full (courier_id);                  -- 6
CREATE INDEX ON dsp_deliveries_full (alt_ref);                   -- 7
CREATE INDEX ON dsp_deliveries_full (depot_id);                  -- 8
CREATE INDEX ON dsp_vehicles_full (vehicle_id);                  -- 9
CREATE INDEX ON dsp_depots_full (depot_id);                      -- 10
CREATE INDEX ON dsp_deliveries_full (lane_code);                 -- 11
CREATE INDEX ON dsp_mid_asset_keys (match_key);                  -- 12
CREATE INDEX ON dsp_mid_claim_totals (anchor_id);                -- 13
CREATE INDEX ON dsp_mid_gw_outcome (anchor_id);                  -- 14
CREATE INDEX ON dsp_roll_owner_pulse (anchor_id);                -- 15
CREATE INDEX ON dsp_roll_courier_best (courier_id);              -- 16
CREATE INDEX ON dsp_mid_leg_events (courier_id);                 -- 19

-- "And a few things I did not get around to writing as SQL:"
--  17. dsp_mid_ref_screen filters with NOT IN. Swap it for NOT EXISTS,
--      that always plans better.
--  18. dsp_mid_leg_lanes has a DISTINCT that looks redundant to me, drop
--      it.
--  20. The LEFT JOIN from dsp_pack_lane_rank to dsp_mid_dock_tally always
--      finds a row, so make it an INNER JOIN and save the outer-join
--      machinery.
--  21. dsp_roll_yard_watch is the slowest thing I rebuilt. Index
--      yard_docks (delivery_id) so its LEFT JOINs stop rescanning it.
--  22. dsp_roll_first_span uses window functions. Replace them with
--      min(created_at) and max(load_units) grouped by courier_id, that is
--      the same thing and it is incremental.
--  23. dsp_mid_toll_join reads the whole delivery history. Index
--      dsp_deliveries_full (delivery_id) so the join stops doing that.
--  24. dsp_pack_ledger_board joins ledger_runs to three lookup tables and is slow to
--      rebuild. Index ledger_runs (delivery_id) so the join reuses it.
--  25. dsp_mid_link_probe has an IN inside an IN. Flatten both into
--      plain joins, nested subqueries never plan well.
