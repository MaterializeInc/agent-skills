#!/usr/bin/env bash
# Launch one clean-room eval run of the mz-optimize-memory skill
# (FOUR rounds in ONE agent session via resume, with a schema snapshot at
# every round boundary for checkpoint grading):
#   run_cleanroom_v6.sh <cond>
#   cond: sb|ss|ob|os|o8b|o8s  (model sonnet-5/opus-5/opus-4-8 x bare/Skill)
#         hb|hs = haiku-4-5, for smoke-testing the harness only (not graded)
# Rounds (see README.md):
#   1  first recommendation package, READ-ONLY wrapper, 5400s
#   2  validate + implement under the gate, RW wrapper (swapped), 9000s
#   3  look for further optimizations AND validate them, RW, 7200s
#   4  pressure + method upgrade + per-change attribution, RW, 5400s
# (round budgets are generous upper bounds: a thermally throttled host
# needed more than the 1800/3600/1800 s the v4 campaign ran with)
# The runner is written for the Claude Code CLI; the isolation flags it
# relies on are documented in README.md so other harnesses can port them.
set -euo pipefail
cond=$1
run="v6_${cond}"
case "$cond" in
  o8*) model=claude-opus-4-8;;
  s*)  model=claude-sonnet-5;;
  o*)  model=claude-opus-5;;
  h*)  model=claude-haiku-4-5-20251001;;
  *)   echo "unknown cond $cond"; exit 1;;
esac
GATE=15   # MB; from v6-ANSWER-KEY.md section 5 (measured prize spectrum)
NMV=14    # materialized views the generator builds (build verify + hydration)
here="$(cd "$(dirname "$0")" && pwd)"

# ---- configuration (override via environment) ------------------------------
: "${EVAL_BENCH_ROOT:=$HOME/eval-bench}"     # per-run working dirs live here
: "${EVAL_PSQL_ARGS:=-h localhost -p 6875 -U materialize -d materialize}"
: "${MZ_SRC:=$EVAL_BENCH_ROOT/mz-src}"       # plain Materialize checkout (read-only for agents)
: "${SKILL_DIR:=$here/../../skills/mz-optimize-memory}"  # the skill under test
: "${EVAL_SCALE:=}"                          # set (e.g. 100) to build a small environment: smoke tests only

[ -d "$MZ_SRC" ] || { echo "MZ_SRC=$MZ_SRC not found (clone MaterializeInc/materialize there, or export MZ_SRC)"; exit 1; }
case "$cond" in *s) [ -f "$SKILL_DIR/SKILL.md" ] || { echo "SKILL_DIR=$SKILL_DIR has no SKILL.md"; exit 1; };; esac

bench="$EVAL_BENCH_ROOT/$run"
d="$bench"; while [ "$d" != "/" ]; do
  if [ -e "$d/CLAUDE.md" ]; then echo "refusing to run: CLAUDE.md at $d would be loaded into the agent session (ancestor project instructions are not excluded)" >&2; exit 1; fi
  d=$(dirname "$d")
done
PSQL="psql -X -q -v ON_ERROR_STOP=1 $EVAL_PSQL_ARGS"
PSQLT="psql -X -t -A -q $EVAL_PSQL_ARGS"
# Prompts, transcripts and snapshots live outside the agent's working
# directory: the permission layer lets it read files under $bench, so a
# round must not be able to read a later round's prompt.
pdir="$EVAL_BENCH_ROOT/$run.private"
mkdir -p "$bench" "$bench/scratch" "$pdir"

# ---- helpers ---------------------------------------------------------------
q() {  # one query, banner-free: psql prints its connection NOTICE on every call
  $PSQLT -c "$1" 2>&1 | grep -v -E '^(NOTICE:|  [A-Z]|Issue a SQL|[[:space:]]*$)' || true
}
hydrated_count() {  # hydrated objects / all objects with a hydration status, in this schema
  $PSQLT -c "SELECT count(*) FILTER (WHERE h.hydrated) || '/' || count(*) FROM mz_internal.mz_hydration_statuses h JOIN mz_catalog.mz_objects o ON o.id = h.object_id JOIN mz_catalog.mz_schemas s ON s.id = o.schema_id WHERE s.name = '$run'"
}
wait_hydrated() {  # $1 = max polls of 10 s; returns 0 when every object is hydrated
  local i c
  for ((i = 0; i < $1; i++)); do
    c=$(hydrated_count)
    [ "${c%/*}" = "${c#*/}" ] && return 0
    sleep 10
  done
  return 1
}
snap() {  # $1 = label (r0..r4): the schema's state at a round boundary, for checkpoint grading
  local out="$pdir/snapshot-$1.txt"
  wait_hydrated 60 || echo "WARNING: snapshot $1 taken with unhydrated objects ($(hydrated_count))"
  {
    echo "== snapshot $1  $(date -u '+%Y-%m-%dT%H:%M:%SZ')  schema $run  hydrated $(hydrated_count)"
    echo "-- objects (type|name)"
    q "SELECT o.type, o.name FROM mz_catalog.mz_objects o JOIN mz_catalog.mz_schemas s ON s.id = o.schema_id WHERE s.name = '$run' ORDER BY 1, 2"
    echo "-- indexes (index|on|id)"
    q "SELECT i.name, o.name, i.id FROM mz_catalog.mz_indexes i JOIN mz_catalog.mz_objects o ON o.id = i.on_id JOIN mz_catalog.mz_schemas s ON s.id = o.schema_id WHERE s.name = '$run' ORDER BY 1"
    echo "-- dataflow census (dataflow|records|size_bytes)"
    q "SET cluster = $run; SELECT name, records, size FROM mz_introspection.mz_dataflow_arrangement_sizes WHERE name LIKE '%$run%' ORDER BY size DESC"
    echo "-- total bytes"
    q "SET cluster = $run; SELECT sum(size) FROM mz_introspection.mz_dataflow_arrangement_sizes WHERE name LIKE '%$run%'"
    echo "-- operator census, top 300 by size (dataflow|operator|records|size_bytes)"
    q "SET cluster = $run; SELECT d.dataflow_name, d.name, a.records, a.size FROM mz_introspection.mz_arrangement_sizes a JOIN mz_introspection.mz_dataflow_operator_dataflows d ON a.operator_id = d.id WHERE d.dataflow_name LIKE '%$run%' AND a.size IS NOT NULL ORDER BY a.size DESC LIMIT 300"
  } > "$out"
  echo "snapshot $1 written ($(wc -l < "$out") lines)"
}
write_wrapper() {  # $1 = ro|rw
  rm -f "$bench/bench-psql"      # chmod-555 file: rm before regenerate
  cp "$here/bench-psql.template" "$bench/bench-psql"
  sed -i -e "s/__RUN__/$run/" -e "s/__MODE__/$1/" -e "s|__PSQL_ARGS__|$EVAL_PSQL_ARGS|" "$bench/bench-psql"
  chmod 555 "$bench/bench-psql"
}
round() {  # $1 = round number, $2 = timeout seconds, $3 = session flag (--session-id|--resume)
  echo "== ROUND $1 =="
  (cd "$bench" && CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 timeout "$2" \
    claude -p --model "$model" "$3" "$SID" \
    --setting-sources project \
    --add-dir "$MZ_SRC" \
    --allowedTools "${allowed[@]}" \
    --disallowedTools "Skill" "WebSearch" "WebFetch" \
    < "$pdir/prompt-r$1.txt" | tee "$pdir/transcript-r$1.txt")
}

# ---- 1. build + verify + wait for hydration --------------------------------
# The fact table is one million-row INSERT; on a slow host it outruns the
# 1-minute default statement_timeout. Raised for the build only, so the
# agent's wrapper keeps the server default.
python3 "$here/build_v6.py" "$run" ${EVAL_SCALE:+--scale "$EVAL_SCALE"} | PGOPTIONS="-c statement_timeout=1h" $PSQL -f -
n=$($PSQLT -c "SELECT count(*) FROM mz_catalog.mz_objects o JOIN mz_catalog.mz_schemas s ON s.id = o.schema_id WHERE s.name = '$run' AND o.type = 'materialized-view'")
[ "$n" -eq "$NMV" ] || { echo "BUILD VERIFY FAILED for $run (mvs=$n, want $NMV)"; exit 1; }
# 120 x 10 s: the v6 environment hydrates in about 4 minutes on a 100cc
# emulator replica (13-15 minutes on a throttled laptop).
wait_hydrated 120 || { echo "HYDRATION FAILED for $run ($(hydrated_count))"; exit 1; }
echo "$run built + hydrated"
snap r0

# ---- 2. prompts + skill ----------------------------------------------------
sed -e "s/__RUN__/$run/g" -e "s|__MZ_SRC__|$MZ_SRC|g" "$here/v6-prompt-1.txt.in" > "$pdir/prompt-r1.txt"
case "$cond" in
  *s)
    # Mount the skill under test as a directory, preserving its
    # progressive-disclosure structure (SKILL.md + references/).
    rm -rf "$bench/skill"
    cp -r "$SKILL_DIR" "$bench/skill"
    { echo
      echo "Internal guidance that may help with this class of task is"
      echo "available under ./skill/, read ./skill/SKILL.md first; it"
      echo "links further files under ./skill/references/."
    } >> "$pdir/prompt-r1.txt"
    ;;
esac
sed -e "s/__RUN__/$run/g" -e "s/__GATE__/$GATE/g" "$here/v6-prompt-2.txt.in" > "$pdir/prompt-r2.txt"
sed -e "s/__RUN__/$run/g" -e "s/__GATE__/$GATE/g" "$here/v6-prompt-3.txt.in" > "$pdir/prompt-r3.txt"
sed -e "s/__RUN__/$run/g" "$here/v6-prompt-4.txt.in" > "$pdir/prompt-r4.txt"

# ---- 3. rounds, with a snapshot after each -----------------------------------
SID=$(uuidgen)
allowed=( "Bash(./bench-psql:*)" "Bash($bench/bench-psql:*)" "Bash(sleep :*)" "Bash(sleep:*)" "Read(//$bench/scratch/**)" "Edit(//$bench/scratch/**)" "Read(//$bench/skill/**)" "Read(//$MZ_SRC/**)" )

write_wrapper ro
round 1 5400 --session-id
snap r1
write_wrapper rw
round 2 9000 --resume
snap r2
round 3 7200 --resume
snap r3
round 4 5400 --resume
snap r4

echo "RUN $run DONE (session $SID)"
