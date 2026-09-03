# gq_<cond>_s<seed> grade (grader: ; date/time: )

| field | value |
|---|---|
| run id | |
| condition | (sb/ss/ob/os/hb/hs) |
| seed | |
| scale | |
| model | |

Inputs: `$EVAL_BENCH_ROOT/<run>.private/` (`prompt.txt`, `transcript.txt`,
`report.md`, `results.json`, `worksheet.md`) plus the view definitions in the
run schema. Grade against `rubric.md`.

`summary` line from `results.json` (paste verbatim):

```
```

## Per task

Copy the automatic columns from `worksheet.md`, then fill the two manual
columns. Mark a `count-only` initial pass as provisional until spot-checked.

| task | initial | after mutation | timed out | guardrail | maintainability note | explanation note |
|---|---|---|---|---|---|---|
| t01 descendants (dirty data) | | | | | | |
| t02 depth | | | | | | |
| t03 team salary (maintained) | | | | | | |
| t04 kit quantity (shared part) | | | | | | |
| t05 kit cost | | | | | | |
| t06 within hops ("all paths") | | | | | | |
| t07 ring accounts | | | | | | |
| t08 scc | | | | | | |
| t09 effective access (maintained) | | | | | | |
| t10 customer clusters | | | | | | |
| t11 route km (maintained) | | | | | | |
| t12 route hops | | | | | | |
| t13 downstream | | | | | | |
| t14 reachable (broken view) | | | | | | |

## Axes

| axis | max | formula or evidence | score |
|---|---|---|---|
| 1 initial correctness | 2.0 | `initial_ok / 14 * 2.0` | |
| 2 correctness after mutation | 1.0 | `post_mutation_ok / mutations * 1.0` | |
| 3 convergence and guardrails | 0.75 | 0.5 if `timed_out` = 0; `0.25 * guardrail / exists`, 0 when `exists` is 0 | |
| 4 maintainability | 0.75 | aggregate in the binding, narrow columns, indexes on maintained views, no re-reading `UNION ALL` | |
| 5 explanation | 0.5 | per-task termination argument, t14 multiset diagnosis, stated interpretations | |

## TOTAL: /5

Harness corrections made under the re-check rule (fixture, reference, or grader
bugs found while grading; none is scored against the run):

What the skill helped with:

What the skill did not help with:

Skill text to change:
