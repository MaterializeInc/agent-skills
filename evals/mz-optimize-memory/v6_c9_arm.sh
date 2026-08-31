#!/usr/bin/env bash
# Arms/restores the nullable-key landmine construction (C9); see README.md.
# arm:     create the naive shared index on the nullable key, rebuild the
#          consumer MV, time its hydration (expect a one-worker NULL^2 grind).
# restore: drop the index, rebuild the consumer MV, time normal hydration.
# Usage: v6_c9_arm.sh <schema> arm|restore
set -eu
S="${1:?schema}"
MODE="${2:?arm|restore}"
: "${EVAL_PSQL_ARGS:=-h localhost -p 6875 -U materialize -d materialize}"
PSQL="psql $EVAL_PSQL_ARGS -qAt"
MV="dsp_pack_owner_risk"
DEF="${TMPDIR:-/tmp}/v6_c9_${S}_${MV}.sql"

# arm always re-captures the definition: schema names are reused across
# environment builds, so a cached file could recreate an earlier
# generation's MV. restore replays the file the preceding arm captured.
if [ "$MODE" = arm ]; then
    $PSQL -c "SHOW CREATE MATERIALIZED VIEW materialize.$S.$MV" \
        | sed -e 's/^[^|]*|//' > "$DEF"
    grep -q "CREATE MATERIALIZED VIEW" "$DEF" || {
        echo "failed to capture $MV definition"; exit 1; }
    echo "captured definition -> $DEF"
else
    [ -s "$DEF" ] || { echo "no captured definition at $DEF: run arm first in this environment"; exit 1; }
fi

if [ "$MODE" = arm ]; then
    $PSQL -c "SET cluster = $S" -c "CREATE INDEX idx_${S}_c9_landmine
        ON materialize.$S.dsp_deliveries_full (alt_ref)" >/dev/null
    echo "landmine index created"
else
    $PSQL -c "DROP INDEX IF EXISTS materialize.$S.idx_${S}_c9_landmine" \
        >/dev/null
    echo "landmine index dropped"
fi

$PSQL -c "DROP MATERIALIZED VIEW materialize.$S.$MV" >/dev/null
T0=$(date +%s)
$PSQL -f "$DEF" >/dev/null
$PSQL -c "SET cluster = $S" -c "CREATE INDEX idx_dsp_pack_owner_risk
    ON materialize.$S.$MV (anchor_id)" >/dev/null 2>&1 || true
echo "MV recreated, waiting for hydration..."

for _ in $(seq 1 120); do
    H=$(timeout 30 $PSQL -c "
SELECT bool_and(h.hydrated)
FROM mz_internal.mz_hydration_statuses h
JOIN mz_materialized_views mv ON mv.id = h.object_id
JOIN mz_schemas s ON mv.schema_id = s.id
WHERE s.name = '$S' AND mv.name = '$MV'" 2>/dev/null || true)
    if [ "$H" = t ]; then
        echo "hydrated after $(( $(date +%s) - T0 ))s"
        break
    fi
    timeout 8 bash -c 'read -t 5 x < /dev/zero || true' 2>/dev/null || true
done
[ "${H:-}" = t ] || echo "NOT hydrated after $(( $(date +%s) - T0 ))s (grind?)"

echo "worker elapsed (cumulative, ratio matters):"
timeout 170 $PSQL -c "SET cluster = $S" -c "
SELECT worker_id, pg_catalog.round(sum(elapsed_ns)/1e9) AS s
FROM mz_introspection.mz_scheduling_elapsed_per_worker
GROUP BY 1 ORDER BY 1" 2>/dev/null || echo "(introspection unresponsive, itself a grind signature)"
