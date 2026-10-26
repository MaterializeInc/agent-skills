#!/usr/bin/env bash
# One clean-room eval run of the mz-graph-queries skill:
#   run_cleanroom.sh <cond> [seed]
#   cond: sb|ss|ob|os|hb|hs  (sonnet-5 | opus-5 | haiku-4-5  x  bare | skill)
# One read-write authoring round, then automatic grading.
# The runner is written for the Claude Code CLI; the isolation flags it
# relies on are documented in README.md so other harnesses can port them.
set -euo pipefail
cond=$1; seed=${2:-1}
case "$cond" in sb|ss|ob|os|hb|hs) ;; *) echo "unknown cond $cond (want sb|ss|ob|os|hb|hs)"; exit 1;; esac
run="gq_${cond}_s${seed}"
case "$cond" in
  s*) model=claude-sonnet-5;;
  o*) model=claude-opus-5;;
  h*) model=claude-haiku-4-5-20251001;;
  *) echo "unknown cond $cond"; exit 1;;
esac
here="$(cd "$(dirname "$0")" && pwd)"

# ---- configuration (override via environment) ------------------------------
: "${EVAL_BENCH_ROOT:=$HOME/eval-bench}"     # per-run working dirs live here
: "${EVAL_PSQL_ARGS:=-h localhost -p 6877 -U materialize -d materialize}"
: "${EVAL_CLUSTER_SIZE:=25cc}"               # replica size for the run's cluster
: "${EVAL_SCALE:=100}"                       # fixture scale; 100 is the graded size
: "${EVAL_TIMEOUT:=7200}"                    # wall-clock budget for the round
: "${SKILL_DIR:=$here/../../skills/mz-graph-queries}"  # the skill under test
# The ancestor walk below and every path handed to the agent need an absolute root.
case "$EVAL_BENCH_ROOT" in /*) ;; *) echo "EVAL_BENCH_ROOT must be absolute" >&2; exit 1;; esac
case "$cond" in *s) [ -f "$SKILL_DIR/SKILL.md" ] || { echo "no SKILL.md at $SKILL_DIR"; exit 1; };; esac
export EVAL_PSQL_ARGS                        # grade.py reads it through mzclient
bench="$EVAL_BENCH_ROOT/$run"; pdir="$EVAL_BENCH_ROOT/$run.private"
d="$bench"; while [ "$d" != "/" ]; do
  [ -e "$d/CLAUDE.md" ] && { echo "refusing: CLAUDE.md at $d would load into the agent session" >&2; exit 1; }
  d=$(dirname "$d")
done
PSQL="psql -X -q -v ON_ERROR_STOP=1 $EVAL_PSQL_ARGS"
mkdir -p "$bench/scratch" "$pdir"

# ---- 1. build --------------------------------------------------------------
$PSQL -c "DROP SCHEMA IF EXISTS $run CASCADE" -c "DROP CLUSTER IF EXISTS $run CASCADE"
$PSQL -c "CREATE CLUSTER $run (SIZE = '$EVAL_CLUSTER_SIZE')"
(cd "$here" && python3 build_fixture.py --eval --seed "$seed" --scale "$EVAL_SCALE" --schema "$run") | $PSQL -f -
n=$(psql -X -At $EVAL_PSQL_ARGS -c "SELECT count(*) FROM $run.employees")
case "$n" in ''|*[!0-9]*) echo "BUILD VERIFY FAILED for $run (employees='$n')" >&2; exit 1;; esac
[ "$n" -gt 0 ] || { echo "BUILD VERIFY FAILED for $run (employees=0)" >&2; exit 1; }
echo "$run built (employees=$n)"

# ---- 2. prompt + skill -----------------------------------------------------
tasks_text=$(cd "$here" && python3 -c '
import sys, tasks, fixture as fx
f = fx.eval_fixture(int(sys.argv[1]), int(sys.argv[2]))
print("\n\n".join(f"## Task {t.id}\n\n" + tasks.render_prompt(t, f, sys.argv[3]) for t in tasks.TASKS))
' "$seed" "$EVAL_SCALE" "$run")
python3 - "$here/prompt.txt.in" "$run" "$pdir/prompt.txt" <<'EOF' "$tasks_text"
import sys
tpl, run, out, tasks_text = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
open(out, "w").write(open(tpl).read().replace("__RUN__", run).replace("__TASKS__", tasks_text))
EOF
case "$cond" in
  *s)
    # Mount only SKILL.md and references/ (the progressive-disclosure
    # structure). Never the whole directory: DEVELOPMENT.md describes this
    # harness and its grading and must not reach the graded agent.
    rm -rf "$bench/skill"; mkdir -p "$bench/skill"
    cp "$SKILL_DIR/SKILL.md" "$bench/skill/"
    cp -r "$SKILL_DIR/references" "$bench/skill/"
    { echo; echo "Internal guidance that may help with this class of task is available under ./skill/;"
      echo "read ./skill/SKILL.md first. It links further files under ./skill/references/."; } >> "$pdir/prompt.txt"
    ;;
esac
rm -f "$bench/bench-psql"      # chmod-555 file: rm before regenerate
sed -e "s/__RUN__/$run/" -e "s|__PSQL_ARGS__|$EVAL_PSQL_ARGS|" "$here/bench-psql.template" > "$bench/bench-psql"
chmod 555 "$bench/bench-psql"

# ---- 3. the round ----------------------------------------------------------
rm -f "$bench/scratch/report.md" "$pdir/round.killed"   # a rerun must not carry the last run's report or kill marker
# One Edit rule covers every file-editing tool, Write included; a separate
# Write(...) rule is rejected by the CLI's permission layer with a warning.
allowed=( "Bash(./bench-psql:*)" "Bash($bench/bench-psql:*)" "Bash(sleep :*)" "Bash(sleep:*)"
          "Read(//$bench/scratch/**)" "Edit(//$bench/scratch/**)" "Read(//$bench/skill/**)" )
# The round is bounded by a plain-bash watchdog, not GNU timeout, which macOS
# does not ship. claude is backgrounded directly (not inside a subshell) so the
# watchdog's signal reaches the process itself; the watchdog polls every five
# seconds, exits on its own when the round finishes, and holds no descriptor of
# this script's stdout.
cd "$bench"
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --model "$model" --setting-sources project \
  --allowedTools "${allowed[@]}" --disallowedTools "Skill" "WebSearch" "WebFetch" \
  < "$pdir/prompt.txt" > "$pdir/transcript.txt" 2>&1 &
apid=$!
( n=0
  while [ "$n" -lt "$EVAL_TIMEOUT" ]; do
    sleep 5
    kill -0 "$apid" 2>/dev/null || exit 0
    n=$((n + 5))
  done
  : > "$pdir/round.killed"
  kill -TERM "$apid" 2>/dev/null
  sleep 10
  kill -KILL "$apid" 2>/dev/null ) >/dev/null 2>&1 </dev/null &
wpid=$!
arc=0; { wait "$apid" || arc=$?; } 2>/dev/null
kill -TERM "$wpid" 2>/dev/null || true
{ wait "$wpid" || true; } 2>/dev/null
cd "$here"
if [ -e "$pdir/round.killed" ]; then
  echo "round killed by the watchdog after ${EVAL_TIMEOUT}s; grading what the agent left behind"
elif [ "$arc" -ne 0 ]; then
  echo "agent exited $arc"
fi
cat "$pdir/transcript.txt"
cp "$bench/scratch/report.md" "$pdir/report.md" 2>/dev/null || echo "no report.md written"

# ---- 4. grade --------------------------------------------------------------
(cd "$here" && python3 grade.py --schema "$run" --seed "$seed" --scale "$EVAL_SCALE" --out "$pdir")
echo "RUN $run DONE: results in $pdir"
