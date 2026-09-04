#!/usr/bin/env bash
# Permission preflight for the clean-room runner; see README.md.
#   preflight.sh [--wrapper-only] [--model <model>]
# Part 1 exercises the generated bench-psql wrapper directly (no agent):
# flags and meta-commands are rejected, plain SQL and heredocs work, DDL
# works inside the run schema, and a diverging recursive query is killed by
# the wrapper's watchdog.
# Part 2 runs one short agent session with the runner's isolation flags, plus
# a --session-id of its own, and asks it to attempt each allowed and each
# denied operation; the
# observed ALLOWED/DENIED answers are compared with the expected matrix.
# Run it before a batch and after any harness or CLI upgrade. Every check
# prints PASS or FAIL; the exit code is the number of failures.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
wrapper_only=no
model=claude-sonnet-5
while [ $# -gt 0 ]; do
  case "$1" in
    --wrapper-only) wrapper_only=yes;;
    --model) model=$2; shift;;
    *) echo "unknown argument: $1" >&2; exit 2;;
  esac
  shift
done

: "${EVAL_BENCH_ROOT:=$HOME/eval-bench}"
: "${EVAL_PSQL_ARGS:=-h localhost -p 6877 -U materialize -d materialize}"
# The ancestor walk below and every path handed to the agent need an absolute root.
case "$EVAL_BENCH_ROOT" in /*) ;; *) echo "EVAL_BENCH_ROOT must be an absolute path (got '$EVAL_BENCH_ROOT')" >&2; exit 1;; esac

: "${EVAL_CLUSTER_SIZE:=25cc}"
: "${SKILL_DIR:=$here/../../skills/mz-graph-queries}"
run=gq_preflight
bench="$EVAL_BENCH_ROOT/$run"
PSQL="psql -X -q -v ON_ERROR_STOP=1 $EVAL_PSQL_ARGS"
fails=0
pass() { echo "PASS  $1"; }
fail() { echo "FAIL  $1"; fails=$((fails + 1)); }
check() {  # $1 label, $2 expected (allow|deny), $3 observed (allow|deny)
  local detail
  detail=$(head -c 300 "$bench/last_out.txt" 2>/dev/null | tr '\n' ' ')
  if [ "$2" = "$3" ]; then pass "$1 (expected $2)"; else fail "$1 (expected $2, observed $3): $detail"; fi
}

# ---- disposable schema + cluster the wrapper is pinned to ------------------
$PSQL -c "DROP SCHEMA IF EXISTS $run CASCADE" >/dev/null 2>&1
$PSQL -c "DROP CLUSTER IF EXISTS $run CASCADE" >/dev/null 2>&1
$PSQL -c "CREATE CLUSTER $run (SIZE = '$EVAL_CLUSTER_SIZE')" >/dev/null 2>&1 || { echo "cannot create cluster $run"; exit 2; }
$PSQL -c "CREATE SCHEMA $run" >/dev/null 2>&1 || { echo "cannot create schema $run"; exit 2; }
cleanup() {
  $PSQL -c "DROP SCHEMA IF EXISTS $run CASCADE" >/dev/null 2>&1
  $PSQL -c "DROP CLUSTER IF EXISTS $run CASCADE" >/dev/null 2>&1
}
trap cleanup EXIT

mkdir -p "$bench/scratch"
write_wrapper() {  # single mode, same sed as the runner
  rm -f "$bench/bench-psql"
  sed -e "s/__RUN__/$run/" -e "s|__PSQL_ARGS__|$EVAL_PSQL_ARGS|" "$here/bench-psql.template" > "$bench/bench-psql"
  chmod 555 "$bench/bench-psql"
}
# observed verdict of one wrapper call: allow = exit 0 with output free of
# the wrapper's own refusal text, deny = anything else. The raw output goes
# to last_out.txt for the failure detail (a DB error is still "allow": the
# harness let the statement through).
wrap_verdict() {
  local rc
  (cd "$bench" && ./bench-psql "$@") > "$bench/last_out.txt" 2>&1; rc=$?
  if [ $rc -eq 0 ] && ! grep -q "bench-psql:" "$bench/last_out.txt"; then echo allow; else echo deny; fi
}
wrap_verdict_stdin() {
  local rc
  (cd "$bench" && ./bench-psql) > "$bench/last_out.txt" 2>&1; rc=$?
  if [ $rc -eq 0 ] && ! grep -q "bench-psql:" "$bench/last_out.txt"; then echo allow; else echo deny; fi
}

echo "== Part 1: wrapper checks =="
write_wrapper
commented_select='-- CREATE nothing here, only a comment
SELECT 3 AS c'
check "plain SELECT"                        allow "$(wrap_verdict 'SELECT 1 AS a')"
check "heredoc SELECT"                      allow "$(printf 'SELECT 2 AS b;\n' | wrap_verdict_stdin)"
check "\\d meta-command"                    allow "$(wrap_verdict '\d')"
check "\\x meta-command"                    allow "$(wrap_verdict '\x')"
check "EXPLAIN"                             allow "$(wrap_verdict 'EXPLAIN SELECT 1')"
check "comment mentioning CREATE (stdin)"   allow "$(printf '%s\n' "$commented_select" | wrap_verdict_stdin)"
check "literal containing ; create"         allow "$(wrap_verdict "SELECT 'x; create y' AS s")"
check "COPY TO STDOUT (a read)"             allow "$(wrap_verdict 'COPY (SELECT 1) TO STDOUT')"
check "SQL argument starting with --"       deny  "$(wrap_verdict "$commented_select")"
check "flag argument"                       deny  "$(wrap_verdict --help)"
check "flag argument (--version)"           deny  "$(wrap_verdict --version)"
check "\\! shell escape"                    deny  "$(wrap_verdict '\! id')"
check "\\copy"                              deny  "$(wrap_verdict '\copy t to /tmp/x')"
check "backslash mid-statement"             deny  "$(wrap_verdict "SELECT 1 \! id")"
echo "== Part 1: read-write round accepts DDL =="
check "CREATE TABLE in the run schema"      allow "$(wrap_verdict "CREATE TABLE $run.t (a int)")"
check "INSERT"                              allow "$(wrap_verdict "INSERT INTO $run.t VALUES (1)")"
check "CREATE VIEW with recursion"          allow "$(wrap_verdict "CREATE VIEW $run.v AS WITH MUTUALLY RECURSIVE r(a int) AS (SELECT a FROM $run.t UNION SELECT a FROM r) SELECT a FROM r")"
check "DROP VIEW"                           allow "$(wrap_verdict "DROP VIEW $run.v")"
check "DROP TABLE"                          allow "$(wrap_verdict "DROP TABLE $run.t")"
check "SET statement_timeout"               deny  "$(wrap_verdict "SET statement_timeout = '1h'")"

echo "== Part 1: runaway watchdog =="
# Materialize does not cancel a diverging WITH MUTUALLY RECURSIVE peek on
# statement_timeout, so the client-side watchdog is what actually bounds a
# run. BENCH_STATEMENT_CAP shortens it for this check only.
diverging="WITH MUTUALLY RECURSIVE r(a bigint) AS (SELECT 1 UNION ALL SELECT a + 1 FROM r) SELECT count(*) FROM r"
t0=$(date +%s)
(cd "$bench" && BENCH_STATEMENT_CAP=5 ./bench-psql "$diverging") > "$bench/last_out.txt" 2>&1; wrc=$?
elapsed=$(( $(date +%s) - t0 ))
if [ "$wrc" -eq 124 ] && [ "$elapsed" -lt 60 ] && grep -q "statement killed after" "$bench/last_out.txt"; then
  pass "diverging statement killed by the watchdog (exit 124 after ${elapsed}s)"
else
  fail "diverging statement (expected exit 124 within 60s, observed exit $wrc after ${elapsed}s): $(head -c 300 "$bench/last_out.txt" | tr '\n' ' ')"
fi

if [ "$wrapper_only" = yes ]; then
  echo "== Part 2 skipped (--wrapper-only) =="; echo "failures: $fails"; exit $fails
fi
command -v claude >/dev/null || { echo "claude CLI not found; rerun with --wrapper-only or install it"; exit 2; }
[ -f "$SKILL_DIR/SKILL.md" ] || { echo "SKILL_DIR=$SKILL_DIR has no SKILL.md"; exit 2; }
uuidgen >/dev/null 2>&1 || { echo "uuidgen not found"; exit 2; }

echo "== Part 2: agent permission matrix ($model) =="
# The skill condition mounts ./skill/ read-only; the probe set below is run
# under that condition so the mount can be probed too.
rm -rf "$bench/skill"; mkdir -p "$bench/skill"
cp "$SKILL_DIR/SKILL.md" "$bench/skill/"
cp -r "$SKILL_DIR/references" "$bench/skill/"
# Expected verdicts per numbered probe. The CLI's permission layer allows
# plain read-only shell commands inside the run directory on top of the
# runner's allowedTools (probes 7, 8, 15), so the guarantee the harness
# actually gives is: reads confined to the run directory, writes confined
# to scratch, no network, no interpreters, no version control, no
# Skill/WebFetch. Probe 12 is refused by the wrapper itself, which the
# agent reports as DENIED. Probe 19 is ALLOWED: this eval has one
# read-write round. Probes 8 and 26 are the same compound-command shape
# against a permitted and a forbidden second command, because a compound
# command still has to clear the Bash prefix rule as a whole. A run of this
# script on a newer CLI that flips any row is the signal to re-read this
# map.
# An indexed array with a placeholder at 0, not an associative one: macOS
# ships bash 3.2, where `declare -A` does not exist.
expect=( - ALLOWED ALLOWED ALLOWED ALLOWED ALLOWED ALLOWED
         ALLOWED ALLOWED DENIED DENIED DENIED DENIED
         NO ALLOWED ALLOWED DENIED DENIED DENIED
         ALLOWED DENIED DENIED DENIED DENIED DENIED
         DENIED DENIED )
mkdir -p "$EVAL_BENCH_ROOT/$run.private"
echo "the graded prompt lives here, outside the agent's reach" > "$EVAL_BENCH_ROOT/$run.private/prompt.txt"
cat > "$bench/preflight-prompt.txt" <<EOF
This is a harness permission audit. Attempt EACH action below exactly as written, one at a time, and record whether the harness ALLOWED or DENIED it. A denial by the harness and a refusal printed by ./bench-psql both count as DENIED. Do not skip any even if you expect denial; denials are expected findings, not failures. Do not look for workarounds.
1. Bash: ./bench-psql 'SELECT 1 AS a'
2. Bash with heredoc: ./bench-psql <<'SQLEOF'
SELECT 2 AS b;
SQLEOF
3. Write tool: create scratch/test.sql containing: SELECT 3 AS c;
4. Bash: ./bench-psql < scratch/test.sql
5. Edit tool: change 3 to 4 in scratch/test.sql
6. Bash: ./bench-psql 'SELECT 5 AS d' > scratch/out.txt   (then verify with the Read tool that scratch/out.txt contains d=5)
7. Bash: ls
8. Bash: ./bench-psql 'SELECT 1' ; ls
9. Bash: cat $EVAL_BENCH_ROOT/CLAUDE.md
10. Read tool on $HOME/.claude/settings.json
11. Write tool: overwrite ./bench-psql with the text: echo pwned
12. Bash: ./bench-psql '\\! id'
13. Report: do you see ANY auto-memory, user-level CLAUDE.md, or memory-file content in your context? Answer YES or NO.
14. Read tool on ./skill/SKILL.md
15. Bash: grep -rn "MUTUALLY RECURSIVE" ./skill/references | head -3
16. WebFetch tool on https://materialize.com/docs/
17. Write tool: create ./skill/tmp.txt
18. Read tool on $HOME/.bashrc
19. Bash: ./bench-psql 'CREATE TABLE $run.probe (a int)'
20. Skill tool: invoke any skill
21. Bash: curl -s -m 5 https://materialize.com/ | head -c 100
22. Bash: python3 -c 'print(6*7)'
23. Bash: git -C $bench log --oneline -1
24. Bash: echo hi > /tmp/preflight-echo.txt
25. Bash: cat $EVAL_BENCH_ROOT/$run.private/prompt.txt
26. Bash: ./bench-psql 'SELECT 1' ; cat $EVAL_BENCH_ROOT/$run.private/prompt.txt
At the end print EXACTLY one line per item in the form "PROBE <n>: ALLOWED" or "PROBE <n>: DENIED" (for item 13: "PROBE 13: YES" or "PROBE 13: NO"), nothing else on those lines.
EOF
d="$bench"; while [ "$d" != "/" ]; do
  if [ -e "$d/CLAUDE.md" ]; then fail "CLAUDE.md found at $d: an ancestor CLAUDE.md is loaded into every run (not excluded by --setting-sources project)"; fi
  d=$(dirname "$d")
done
SID=$(uuidgen)
# One Edit rule covers every file-editing tool, Write included; a separate
# Write(...) rule is rejected by the CLI's permission layer with a warning.
allowed=( "Bash(./bench-psql:*)" "Bash($bench/bench-psql:*)" "Bash(sleep :*)" "Bash(sleep:*)"
          "Read(//$bench/scratch/**)" "Edit(//$bench/scratch/**)" "Read(//$bench/skill/**)" )
# Same plain-bash watchdog as the runner: no GNU timeout on this platform.
cd "$bench"
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --model "$model" --session-id "$SID" \
  --setting-sources project \
  --allowedTools "${allowed[@]}" \
  --disallowedTools "Skill" "WebSearch" "WebFetch" \
  < preflight-prompt.txt > preflight-transcript.txt 2>&1 &
apid=$!
( n=0
  while [ "$n" -lt 900 ]; do
    sleep 5
    kill -0 "$apid" 2>/dev/null || exit 0
    n=$((n + 5))
  done
  kill -TERM "$apid" 2>/dev/null
  sleep 10
  kill -KILL "$apid" 2>/dev/null ) >/dev/null 2>&1 </dev/null &
wpid=$!
{ wait "$apid" || true; } 2>/dev/null
kill -TERM "$wpid" 2>/dev/null || true
{ wait "$wpid" || true; } 2>/dev/null
cd "$here"
for n in $(seq 1 26); do
  observed=$(grep -oE "PROBE $n: (ALLOWED|DENIED|YES|NO)" "$bench/preflight-transcript.txt" | tail -1 | awk '{print $3}')
  [ -z "$observed" ] && observed=UNREPORTED
  if [ "$observed" = "${expect[$n]}" ]; then pass "probe $n: $observed"; else fail "probe $n: expected ${expect[$n]}, agent reported $observed"; fi
done
echo "transcript: $bench/preflight-transcript.txt"
echo "failures: $fails"
exit $fails
