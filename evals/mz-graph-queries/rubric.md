# mz-graph-queries grading rubric, /5 total

One graded run is one authoring round against one eval fixture: fourteen views,
scored on five axes. Axes 1 to 3 are automatic and read
`$EVAL_BENCH_ROOT/<run>.private/results.json`, written by `grade.py`. Axes 4
and 5 are manual and read `report.md` (the agent's own write-up, copied out of
its scratch directory) and `transcript.txt`, alongside the view definitions in
the run schema.

The summary keys `grade.py` writes are `tasks`, `exists`, `initial_ok`,
`post_mutation_ok`, `mutations`, `timed_out`, and `guardrail`.

## Re-check rule

Before deducting for any automatic failure, re-run the failing view by hand
against the run schema and compare it with the answer key in `reference.py`. A
fixture bug, a reference bug, or a grader bug is possible, and a run that is
right where the harness is wrong must not lose points for it. Fix the problem
in the harness, re-grade, and record the correction; never score around it.
The same applies to a task the worksheet marks `count-only`: the grader fell
back to a row count because the full result did not ship inside the statement
timeout, so the row set was never compared. Treat a `count-only` pass as
provisional and spot-check it before awarding Axis 1 credit for that task.

## Axis 1: initial correctness (1.5)

`initial_ok / 14 * 1.5`.

A view scores here only if it exists, answers inside the grader's timeout, and
its row set equals the reference exactly. A missing view, an error, and a wrong
row set all score zero for that task.

## Axis 2: correctness after mutation (1.0)

`post_mutation_ok / mutations * 1.0`.

Six tasks carry a mutation (t01, t03, t09, t10, t11, t13); `mutations` in the
summary is the count actually attempted. A view that was already wrong before
the mutation scores zero here: the axis measures whether a correct answer stays
correct as the input changes, not whether a wrong answer stays wrong. The
worksheet records a skipped mutation as `skipped: view missing` or
`skipped: initial read timed out`; both count as zero.

## Axis 3: convergence and guardrails (0.75)

| component | weight | rule |
|---|---|---|
| convergence | 0.5 | 0.5 if `timed_out` is 0, otherwise 0 |
| guardrail | 0.25 | `0.25 * guardrail / exists` |

`guardrail` counts views whose definition contains `RECURSION LIMIT`. Every one
of the fourteen answers is recursive, so the denominator is the number of views
that exist; with all fourteen present it is 14. A run that ships no limit
anywhere scores 0 on this component even if every answer is correct.

## Axis 4: maintainability (0.75, manual)

Read the view definitions in the run schema and the corresponding paragraphs of
`report.md`.

| check | tasks it applies to |
|---|---|
| the aggregate is computed inside the recursive binding, not over an exploded path set | t03, t04, t05, t08, t10, t11, t12 |
| the recursive binding carries narrow columns: keys and the accumulator, no payload dragged around the loop | all |
| join keys are indexed on the views the prompt marked as maintained | t03, t09, t11 |
| no `UNION ALL` that re-reads the binding and grows a multiset | all |

Award the full 0.75 when all four hold across the run, about half when one
class of problem recurs, and zero when the run consistently explodes paths or
carries payload through the loop.

## Axis 5: explanation (0.5, manual)

Read `report.md` and, where it is thin, `transcript.txt`.

| check |
|---|
| a termination argument is stated per task, not once for the run |
| the t14 diagnosis names multiset growth: `UNION ALL` re-adding the binding and the base case on every iteration, so the binding never reaches a fixpoint. A diagnosis of "cycles in the transfers graph" is wrong and scores zero for this line |
| interpretations of the loosely phrased requests are stated: t06 "all paths" delivered as the set of reachable accounts within the hop bound, t01 dirty manager data (the planted cycle) handled explicitly, t10 links stored once per pair and traversed in both directions |

## Total

Sum the five axes. Record the run in the table at the bottom of `README.md`,
and record any harness correction the re-check rule produced.
