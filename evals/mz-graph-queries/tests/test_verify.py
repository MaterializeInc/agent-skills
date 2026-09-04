import sys, os, io, unittest
from contextlib import redirect_stdout
from unittest import mock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import mzclient
import verify_skill_sql as v

MD = """# Title

```sql
SELECT 1;
```

Some prose.

<!-- verify: error -->

```sql
SELECT 1/0;
```

```postgresql
WITH RECURSIVE t AS (SELECT 1) SELECT * FROM t;
```

<!-- verify: skip -->
```sql
SELECT 'never runs';
```

```sql
SELECT 2;
```
"""


class Extract(unittest.TestCase):
    def test_blocks_and_modes(self):
        b = v.extract_blocks(MD)
        self.assertEqual([(x.index, x.mode, x.sql.strip()) for x in b], [
            (1, "run", "SELECT 1;"),
            (2, "error", "SELECT 1/0;"),
            (0, "skip", "SELECT 'never runs';"),
            (3, "run", "SELECT 2;"),
        ])

    def test_expected_name(self):
        self.assertEqual(v.expected_path("hierarchies", 3).name, "03.txt")
        self.assertEqual(v.expected_path("hierarchies", 3).parent.name, "hierarchies")


class Normalize(unittest.TestCase):
    def test_sorted_rows(self):
        self.assertEqual(v.normalize([["b", "2"], ["a", "1"]]), "a\t1\nb\t2\n")
        self.assertEqual(v.normalize([]), "")


class ParseRows(unittest.TestCase):
    def test_trailing_newline_is_not_a_row(self):
        self.assertEqual(mzclient.parse_rows("a\tb\nc\td\n"), [["a", "b"], ["c", "d"]])

    def test_no_output_is_no_rows(self):
        self.assertEqual(mzclient.parse_rows(""), [])

    # SELECT 'a' AS c UNION ALL SELECT '' renders as "\na\n": the empty-string
    # row is a real row and must survive.
    def test_empty_string_row_is_kept(self):
        self.assertEqual(mzclient.parse_rows("\na\n"), [[""], ["a"]])

    def test_empty_string_row_last_is_kept(self):
        self.assertEqual(mzclient.parse_rows("a\n\n"), [["a"], [""]])


class SelectFiles(unittest.TestCase):
    def test_only_matching_nothing_raises(self):
        with self.assertRaises(LookupError):
            v.select_files("no-such-reference-file")

    def test_main_fails_on_only_matching_nothing(self):
        argv = ["verify_skill_sql.py", "--only", "no-such-reference-file"]
        out = io.StringIO()
        with mock.patch.object(sys, "argv", argv), redirect_stdout(out):
            rc = v.main()
        self.assertNotEqual(rc, 0)
        self.assertIn("no-such-reference-file", out.getvalue())
        self.assertNotIn("OK", out.getvalue())


if __name__ == "__main__":
    unittest.main()
