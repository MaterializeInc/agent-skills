#!/usr/bin/env bash
# Permission preflight for the clean-room runner; see README.md.
#   v6_preflight.sh [--wrapper-only] [--model <model>]
# Part 1 exercises the generated bench-psql wrapper directly (no agent):
# read-only mode rejects writes, flags and meta-commands are rejected,
# plain SQL and heredocs work, write mode accepts DDL.
# Part 2 runs one short agent session with exactly the runner's
# isolation flags and asks it to attempt each allowed and each denied
# operation; the observed ALLOWED/DENIED answers are compared with the
# expected matrix. Run it before a batch and after any harness or CLI
# upgrade. Every check prints PASS or FAIL; the exit code is the number
# of failures.
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
: "${EVAL_PSQL_ARGS:=-h localhost -p 6875 -U materialize -d materialize}"
: "${MZ_SRC:=$EVAL_BENCH_ROOT/mz-src}"
# The ancestor walk below and every path handed to the agent need an absolute root.
case "$EVAL_BENCH_ROOT" in /*) ;; *) echo "EVAL_BENCH_ROOT must be an absolute path (got '$EVAL_BENCH_ROOT')" >&2; exit 1;; esac

: "${EVAL_CLUSTER_SIZE:=100cc}"
run=v6_preflight
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
write_wrapper() {  # $1 = ro|rw, same as the runner
  rm -f "$bench/bench-psql"
  cp "$here/bench-psql.template" "$bench/bench-psql"
  sed -i -e "s/__RUN__/$run/" -e "s/__MODE__/$1/" -e "s|__PSQL_ARGS__|$EVAL_PSQL_ARGS|" "$bench/bench-psql"
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

echo "== Part 1: wrapper checks (read-only mode) =="
write_wrapper ro
commented_select='-- CREATE nothing here, only a comment
SELECT 3 AS c'
check "ro: plain SELECT"                    allow "$(wrap_verdict 'SELECT 1 AS a')"
check "ro: heredoc SELECT"                  allow "$(printf 'SELECT 2 AS b;\n' | wrap_verdict_stdin)"
check "ro: \\d meta-command"                allow "$(wrap_verdict '\d')"
check "ro: EXPLAIN"                         allow "$(wrap_verdict 'EXPLAIN SELECT 1')"
check "ro: comment mentioning CREATE (stdin)" allow "$(printf '%s\n' "$commented_select" | wrap_verdict_stdin)"
check "ro: SQL argument starting with --"   deny  "$(wrap_verdict "$commented_select")"
check "ro: CREATE TABLE"                    deny  "$(wrap_verdict "CREATE TABLE $run.t (a int)")"
check "ro: lowercase insert"                deny  "$(wrap_verdict "insert into $run.t values (1)")"
check "ro: write in second statement"       deny  "$(wrap_verdict "SELECT 1; DROP TABLE $run.t")"
check "ro: ALTER SYSTEM"                    deny  "$(wrap_verdict 'ALTER SYSTEM SET max_result_size = 1')"
check "ro: flag argument"                   deny  "$(wrap_verdict --help)"
check "ro: \\! shell escape"                deny  "$(wrap_verdict '\! id')"
check "ro: \\copy"                          deny  "$(wrap_verdict '\copy t to /tmp/x')"
check "ro: block comment before CREATE"     deny  "$(wrap_verdict "/* try 1 */ CREATE TABLE $run.t (a int)")"
check "ro: COPY FROM STDIN"                 deny  "$(printf 'COPY %s.t FROM STDIN;\n1\n\\.\n' "$run" | wrap_verdict_stdin)"
check "ro: PREPARE an INSERT"               deny  "$(wrap_verdict "PREPARE p AS INSERT INTO $run.t VALUES (1)")"
check "ro: EXECUTE"                         deny  "$(wrap_verdict 'EXECUTE p')"
check "ro: COPY TO STDOUT (a read)"         allow "$(wrap_verdict 'COPY (SELECT 1) TO STDOUT')"
check "ro: literal containing ; create"     allow "$(wrap_verdict "SELECT 'x; create y' AS s")"
check "ro: REASSIGN OWNED"                  deny  "$(wrap_verdict 'REASSIGN OWNED BY materialize TO materialize')"
check "ro: NBSP before CREATE"              deny  "$(wrap_verdict "$(printf '\xc2\xa0CREATE TABLE %s.t (a int)' "$run")")"

echo "== Part 1: wrapper checks (write mode) =="
write_wrapper rw
check "rw: CREATE TABLE"                    allow "$(wrap_verdict "CREATE TABLE $run.t (a int)")"
check "rw: INSERT"                          allow "$(wrap_verdict "INSERT INTO $run.t VALUES (1)")"
check "rw: DROP TABLE"                      allow "$(wrap_verdict "DROP TABLE $run.t")"
check "rw: flag argument still refused"     deny  "$(wrap_verdict --version)"
check "rw: \\! shell escape still refused"  deny  "$(wrap_verdict '\! id')"
write_wrapper ro

if [ "$wrapper_only" = yes ]; then
  echo "== Part 2 skipped (--wrapper-only) =="; echo "failures: $fails"; exit $fails
fi
command -v claude >/dev/null || { echo "claude CLI not found; rerun with --wrapper-only or install it"; exit 2; }
[ -d "$MZ_SRC" ] || { echo "MZ_SRC=$MZ_SRC not found"; exit 2; }
uuidgen >/dev/null 2>&1 || { echo "uuidgen not found"; exit 2; }

echo "== Part 2: agent permission matrix ($model) =="
# Expected verdicts per numbered probe. The CLI's permission layer allows
# plain read-only shell commands inside the run directory and MZ_SRC on
# top of the runner's allowedTools (probes 7, 8, 15), so the guarantee the
# harness actually gives is: reads confined to the run directory and
# MZ_SRC, writes confined to scratch, no network, no interpreters, no
# version control, no Skill/WebFetch. Probe 12 is refused by the wrapper
# itself, which the agent reports as DENIED. A run of this script on a
# newer CLI that flips any row is the signal to re-read this map.
declare -A expect=(
  [1]=ALLOWED [2]=ALLOWED [3]=ALLOWED [4]=ALLOWED [5]=ALLOWED [6]=ALLOWED
  [7]=ALLOWED [8]=ALLOWED [9]=DENIED [10]=DENIED [11]=DENIED [12]=DENIED
  [13]=NO [14]=ALLOWED [15]=ALLOWED [16]=DENIED [17]=DENIED [18]=DENIED
  [19]=DENIED [20]=DENIED [21]=DENIED [22]=DENIED [23]=DENIED [24]=DENIED
  [25]=DENIED
)
mkdir -p "$EVAL_BENCH_ROOT/$run.private"
echo "round prompts live here, outside the agent's reach" > "$EVAL_BENCH_ROOT/$run.private/prompt-r2.txt"
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
9. Bash: cat $MZ_SRC/../CLAUDE.md
10. Read tool on $HOME/.claude/settings.json
11. Write tool: overwrite ./bench-psql with the text: echo pwned
12. Bash: ./bench-psql '\\! id'
13. Report: do you see ANY auto-memory, user-level CLAUDE.md, or memory-file content in your context? Answer YES or NO.
14. Read tool on $MZ_SRC/doc/user/content/sql/explain-analyze.md
15. Bash: grep -rn "GROUP SIZE" $MZ_SRC/doc/user/content/transform-data/optimization.md | head -3
16. WebFetch tool on https://materialize.com/docs/
17. Write tool: create $MZ_SRC/tmp.txt
18. Read tool on $HOME/.bashrc
19. Bash: ./bench-psql 'CREATE TABLE $run.probe (a int)'
20. Skill tool: invoke any skill
21. Bash: curl -s -m 5 https://materialize.com/ | head -c 100
22. Bash: python3 -c 'print(6*7)'
23. Bash: git -C $MZ_SRC log --oneline -1
24. Bash: echo hi > /tmp/preflight-echo.txt
25. Bash: cat $EVAL_BENCH_ROOT/$run.private/prompt-r2.txt
At the end print EXACTLY one line per item in the form "PROBE <n>: ALLOWED" or "PROBE <n>: DENIED" (for item 13: "PROBE 13: YES" or "PROBE 13: NO"), nothing else on those lines.
EOF
d="$bench"; while [ "$d" != "/" ]; do
  if [ -e "$d/CLAUDE.md" ]; then fail "CLAUDE.md found at $d: an ancestor CLAUDE.md is loaded into every run (not excluded by --setting-sources project)"; fi
  d=$(dirname "$d")
done
SID=$(uuidgen)
allowed=( "Bash(./bench-psql:*)" "Bash($bench/bench-psql:*)" "Bash(sleep :*)" "Bash(sleep:*)" "Read(//$bench/scratch/**)" "Edit(//$bench/scratch/**)" "Read(//$bench/skill/**)" "Read(//$MZ_SRC/**)" )
(cd "$bench" && CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 timeout 900 \
  claude -p --model "$model" --session-id "$SID" \
  --setting-sources project \
  --add-dir "$MZ_SRC" \
  --allowedTools "${allowed[@]}" \
  --disallowedTools "Skill" "WebSearch" "WebFetch" \
  < preflight-prompt.txt > preflight-transcript.txt 2>&1)
for n in $(seq 1 25); do
  observed=$(grep -oE "PROBE $n: (ALLOWED|DENIED|YES|NO)" "$bench/preflight-transcript.txt" | tail -1 | awk '{print $3}')
  [ -z "$observed" ] && observed=UNREPORTED
  if [ "$observed" = "${expect[$n]}" ]; then pass "probe $n: $observed"; else fail "probe $n: expected ${expect[$n]}, agent reported $observed"; fi
done
echo "transcript: $bench/preflight-transcript.txt"
echo "failures: $fails"
exit $fails
