"""Talk to Materialize through the psql binary. Standard library only."""
from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass, field

PSQL_ARGS: list[str] = os.environ.get(
    "EVAL_PSQL_ARGS", "-h localhost -p 6877 -U materialize -d materialize").split()


@dataclass
class Result:
    rc: int
    rows: list[list[str]] = field(default_factory=list)
    stderr: str = ""
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.rc == 0 and not self.timed_out

    @property
    def error_line(self) -> str:
        for line in self.stderr.splitlines():
            if "ERROR:" in line:
                return line[line.index("ERROR:"):].strip()
        return self.stderr.strip().splitlines()[-1] if self.stderr.strip() else ""


def parse_rows(stdout: str) -> list[list[str]]:
    """Split psql -At output into rows of tab-separated fields.

    psql terminates every row with a newline, so the split leaves one trailing
    empty element; that one is dropped. Every other empty line is a real row
    holding a single empty-string column and is kept.
    """
    lines = stdout.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [line.split("\t") for line in lines]


def run(sql: str, *, schema: str | None = None, cluster: str | None = None,
        timeout_s: int = 120, on_error_stop: bool = True) -> Result:
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as fh:
        fh.write(sql)
        path = fh.name
    try:
        return run_file(path, schema=schema, cluster=cluster, timeout_s=timeout_s, on_error_stop=on_error_stop)
    finally:
        os.unlink(path)


def run_file(path: str, *, schema: str | None = None, cluster: str | None = None,
             timeout_s: int = 120, on_error_stop: bool = True) -> Result:
    cmd = ["psql", "-X", "-q", "-At", "-F", "\t", "-P", "null=\\N",
           "-v", f"ON_ERROR_STOP={'1' if on_error_stop else '0'}", *PSQL_ARGS,
           "-c", f"SET statement_timeout = '{timeout_s}s'"]
    if cluster:
        cmd += ["-c", f"SET cluster = {cluster}"]
    if schema:
        cmd += ["-c", f"SET schema = {schema}"]
    cmd += ["-f", path]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 30)
    except subprocess.TimeoutExpired as e:
        return Result(rc=124, stderr=(e.stderr or "") if isinstance(e.stderr, str) else "", timed_out=True)
    rows = parse_rows(p.stdout)
    timed_out = "canceling statement due to statement timeout" in p.stderr
    return Result(rc=p.returncode, rows=rows, stderr=p.stderr, timed_out=timed_out)
