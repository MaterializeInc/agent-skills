import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
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


if __name__ == "__main__":
    unittest.main()
