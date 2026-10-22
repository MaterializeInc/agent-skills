# SQL functions & operators

Learn more about the SQL functions and operators supported in Materialize

This page details Materialize's supported SQL [functions](#functions) and [operators](#operators).

## Functions

### Unmaterializable functions

Several functions in Materialize are **unmaterializable** because their output
depends upon state besides their input parameters, like the value of a session
parameter or the timestamp of the current transaction. You cannot create an
[index](/sql/create-index) or materialized view that depends on an
unmaterializable function, but you can use them in non-materialized views and
one-off [`SELECT`](/sql/select) statements.

Unmaterializable functions are marked as such in the table below.

### Side-effecting functions

Several functions in Materialize are **side-effecting** because their evaluation
changes system state. For example, the `pg_cancel_backend` function allows
canceling a query running on another connection.

Materialize offers only limited support for these functions. They may be called
only at the top level of a `SELECT` statement, like so:

```mzsql
SELECT side_effecting_function(arg, ...);
```

You cannot manipulate or alias the function call expression, call multiple
side-effecting functions in the same `SELECT` statement, nor add any additional
clauses to the `SELECT` statement (e.g., `FROM`, `WHERE`).

Side-effecting functions are marked as such in the table below.

### Generic functionsGeneric functions can typically take arguments of any type.#### `CAST (cast_expr) -> T`

Value as type <code>T</code> [(docs)](/sql/functions/cast)#### `TRY_CAST (cast_expr) -> T?`

Value as type <code>T</code>, or <em>NULL</em> if the conversion fails. [(docs)](/sql/functions/cast#try_cast)#### `coalesce(x: T...) -> T?`

First non-<em>NULL</em> arg, or <em>NULL</em> if all are <em>NULL</em>.#### `greatest(x: T...) -> T?`

The maximum argument, or <em>NULL</em> if all are <em>NULL</em>.#### `least(x: T...) -> T?`

The minimum argument, or <em>NULL</em> if all are <em>NULL</em>.#### `nullif(x: T, y: T) -> T?`

<em>NULL</em> if <code>x == y</code>, else <code>x</code>.### Aggregate functionsAggregate functions take one or more of the same element type as arguments.#### `array_agg(x: T) -> T[]`

Aggregate values (including nulls) as an array [(docs)](/sql/functions/array_agg)#### `avg(x: T) -> U`

<p>Average of <code>T</code>&rsquo;s values.</p>
<p>Returns <code>numeric</code> if <code>x</code> is <code>int</code>, <code>double</code> if <code>x</code> is <code>real</code>, else returns
same type as <code>x</code>.</p>
<p>For <code>real</code> and <code>double precision</code> inputs, see <a href="../types/float/#aggregate-precision" >aggregate
precision</a>.</p>
#### `bool_and(x: T) -> T`

<em>NULL</em> if all values of <code>x</code> are <em>NULL</em>, otherwise true if all values of <code>x</code> are true, otherwise false.#### `bool_or(x: T) -> T`

<em>NULL</em> if all values of <code>x</code> are <em>NULL</em>, otherwise true if any values of <code>x</code> are true, otherwise false.#### `count(x: T) -> bigint`

Number of non-<em>NULL</em> inputs.#### `jsonb_agg(expression) -> jsonb`

Aggregate values (including nulls) as a jsonb array [(docs)](/sql/functions/jsonb_agg)#### `jsonb_object_agg(keys, values) -> jsonb`

Aggregate keys and values (including nulls) as a jsonb object [(docs)](/sql/functions/jsonb_object_agg)#### `max(x: T) -> T`

Maximum value among <code>T</code>.#### `min(x: T) -> T`

Minimum value among <code>T</code>.#### `stddev(x: T) -> U`

<p>Historical alias for <code>stddev_samp</code>. <em>(imprecise)</em></p>
<p>Returns <code>numeric</code> if <code>x</code> is <code>int</code>, <code>double</code> if <code>x</code> is <code>real</code>, else returns
same type as <code>x</code>.</p>
#### `stddev_pop(x: T) -> U`

<p>Population standard deviation of <code>T</code>&rsquo;s values. <em>(imprecise)</em></p>
<p>Returns <code>numeric</code> if <code>x</code> is <code>int</code>, <code>double</code> if <code>x</code> is <code>real</code>, else returns
same type as <code>x</code>.</p>
#### `stddev_samp(x: T) -> U`

<p>Sample standard deviation of <code>T</code>&rsquo;s values. <em>(imprecise)</em></p>
<p>Returns <code>numeric</code> if <code>x</code> is <code>int</code>, <code>double</code> if <code>x</code> is <code>real</code>, else returns
same type as <code>x</code>.</p>
#### `string_agg(value: text, delimiter: text) -> text`

Concatenates the non-null input values into text. Each value after the first is preceded by the corresponding delimiter [(docs)](/sql/functions/string_agg)#### `sum(x: T) -> U`

<p>Sum of <code>T</code>&rsquo;s values</p>
<p>Returns <code>bigint</code> if <code>x</code> is <code>int</code> or <code>smallint</code>, <code>numeric</code> if <code>x</code> is <code>bigint</code> or <code>uint8</code>,
<code>uint8</code> if <code>x</code> is <code>uint4</code> or <code>uint2</code>, else returns same type as <code>x</code>.</p>
<p>For <code>real</code> and <code>double precision</code> inputs, see <a href="../types/float/#aggregate-precision" >aggregate
precision</a>.</p>
#### `variance(x: T) -> U`

<p>Historical alias for <code>var_samp</code>. <em>(imprecise)</em></p>
<p>Returns <code>numeric</code> if <code>x</code> is <code>int</code>, <code>double</code> if <code>x</code> is <code>real</code>, else returns
same type as <code>x</code>.</p>
#### `var_pop(x: T) -> U`

<p>Population variance of <code>T</code>&rsquo;s values. <em>(imprecise)</em></p>
<p>Returns <code>numeric</code> if <code>x</code> is <code>int</code>, <code>double</code> if <code>x</code> is <code>real</code>, else returns
same type as <code>x</code>.</p>
#### `var_samp(x: T) -> U`

<p>Sample variance of <code>T</code>&rsquo;s values. <em>(imprecise)</em></p>
<p>Returns <code>numeric</code> if <code>x</code> is <code>int</code>, <code>double</code> if <code>x</code> is <code>real</code>, else returns
same type as <code>x</code>.</p>
### List functionsList functions take <a href="../types/list" ><code>list</code></a> arguments, and are <a href="../types/list/#polymorphism" >polymorphic</a>.#### `list_agg(x: any) -> L`

Aggregate values (including nulls) as a list [(docs)](/sql/functions/list_agg)#### `list_append(l: listany, e: listelementany) -> L`

Appends <code>e</code> to <code>l</code>.#### `list_cat(l1: listany, l2: listany) -> L`

Concatenates <code>l1</code> and <code>l2</code>.#### `list_length(l: listany) -> int`

Return the number of elements in <code>l</code>.#### `list_prepend(e: listelementany, l: listany) -> listany`

Prepends <code>e</code> to <code>l</code>.### Map functionsMap functions take <a href="../types/map" ><code>map</code></a> arguments, and are <a href="../types/#polymorphism" >polymorphic</a>.#### `map_length(m: mapany) -> int`

Return the number of elements in <code>m</code>.#### `map_build(kvs: list record(text, T)) -> map[text=>T]`

Builds a map from a list of records whose fields are two elements, the
first of which is <code>text</code>. In the face of duplicate keys, <code>map_build</code> retains
value from the record in the latest positition. This function is
purpose-built to process <a href="/sql/create-source/kafka/#headers" >Kafka headers</a>.#### `map_agg(keys: text, values: T) -> map[text=>T]`

Aggregate keys and values (including nulls) as a map [(docs)](/sql/functions/map_agg)### Numbers functionsNumber functions take number-like arguments, e.g. <a href="../types/int" ><code>int</code></a>, <a href="../types/float" ><code>float</code></a>, <a href="../types/numeric" ><code>numeric</code></a>, unless otherwise specified.#### `abs(x: N) -> N`

The absolute value of <code>x</code>.#### `cbrt(x: double precision) -> double precision`

The cube root of <code>x</code>.#### `ceil(x: N) -> double precision`

The smallest integer &gt;= <code>x</code>.#### `ceiling(x: N) -> double precision`

Alias of <code>ceil</code>.#### `exp(x: N) -> double precision`

Exponential of <code>x</code> (e raised to the given power)#### `floor(x: N) -> double precision`

The largest integer &lt;= <code>x</code>.#### `ln(x: double precision) -> double precision`

Natural logarithm of <code>x</code>.#### `ln(x: numeric) -> numeric`

Natural logarithm of <code>x</code>.#### `log(x: double precision) -> double precision`

Base 10 logarithm of <code>x</code>.#### `log(x: numeric) -> numeric`

Base 10 logarithm of <code>x</code>.#### `log10(x: double precision) -> double precision`

Base 10 logarithm of <code>x</code>, same as <code>log</code>.#### `log10(x: numeric) -> numeric`

Base 10 logarithm of <code>x</code>, same as <code>log</code>.#### `log(b: numeric, x: numeric) -> numeric`

Base <code>b</code> logarithm of <code>x</code>.#### `mod(x: N, y: N) -> N`

<code>x % y</code>#### `pow(x: double precision, y: double precision) -> double precision`

Alias of <code>power</code>.#### `pow(x: numeric, y: numeric) -> numeric`

Alias of <code>power</code>.#### `power(x: double precision, y: double precision) -> double precision`

<code>x</code> raised to the power of <code>y</code>.#### `power(x: numeric, y: numeric) -> numeric`

<code>x</code> raised to the power of <code>y</code>.#### `round(x: N) -> double precision`

<code>x</code> rounded to the nearest whole number.
If <code>N</code> is <code>real</code> or <code>double precision</code>, rounds ties to the nearest even number.
If <code>N</code> is <code>numeric</code>, rounds ties away from zero.#### `round(x: numeric, y: int) -> numeric`

<code>x</code> rounded to <code>y</code> decimal places, while retaining the same <a href="../types/numeric" ><code>numeric</code></a> scale; rounds ties away from zero.#### `sqrt(x: numeric) -> numeric`

The square root of <code>x</code>.#### `sqrt(x: double precision) -> double precision`

The square root of <code>x</code>.#### `trunc(x: N) -> double precision`

<code>x</code> truncated toward zero to a whole number.### Trigonometric functionsTrigonometric functions take and return <code>double precision</code> values.#### `cos(x: double precision) -> double precision`

The cosine of <code>x</code>, with <code>x</code> in radians.#### `acos(x: double precision) -> double precision`

The inverse cosine of <code>x</code>, result in radians.#### `cosh(x: double precision) -> double precision`

The hyperbolic cosine of <code>x</code>, with <code>x</code> as a hyperbolic angle.#### `acosh(x: double precision) -> double precision`

The inverse hyperbolic cosine of <code>x</code>.#### `cot(x: double precision) -> double precision`

The cotangent of <code>x</code>, with <code>x</code> in radians.#### `sin(x: double precision) -> double precision`

The sine of <code>x</code>, with <code>x</code> in radians.#### `asin(x: double precision) -> double precision`

The inverse sine of <code>x</code>, result in radians.#### `sinh(x: double precision) -> double precision`

The hyperbolic sine of <code>x</code>, with <code>x</code> as a hyperbolic angle.#### `asinh(x: double precision) -> double precision`

The inverse hyperbolic sine of <code>x</code>.#### `tan(x: double precision) -> double precision`

The tangent of <code>x</code>, with <code>x</code> in radians.#### `atan(x: double precision) -> double precision`

The inverse tangent of <code>x</code>, result in radians.#### `tanh(x: double precision) -> double precision`

The hyperbolic tangent of <code>x</code>, with <code>x</code> as a hyperbolic angle.#### `atanh(x: double precision) -> double precision`

The inverse hyperbolic tangent of <code>x</code>.#### `radians(x: double precision) -> double precision`

Converts degrees to radians.#### `degrees(x: double precision) -> double precision`

Converts radians to degrees.### String functions#### `ascii(s: str) -> int`

The ASCII value of <code>s</code>&rsquo;s left-most character.#### `btrim(s: str) -> str`

Trim all spaces from both sides of <code>s</code>.#### `btrim(s: str, c: str) -> str`

Trim any character in <code>c</code> from both sides of <code>s</code>.#### `bit_count(b: bytea) -> bigint`

Returns the number of bits set in the bit string (aka <em>popcount</em>).#### `bit_length(s: str) -> int`

Number of bits in <code>s</code>.#### `bit_length(b: bytea) -> int`

Number of bits in <code>b</code>.#### `char_length(s: str) -> int`

Number of code points in <code>s</code>.#### `chr(i: int) -> str`

Character with the given Unicode codepoint.
Only supports codepoints that can be encoded in UTF-8.
The NULL (0) character is not allowed.#### `concat(f: any, r: any...) -> text`

Concatenates the text representation of non-NULL arguments. The maximum length of the result string is 100 MiB.#### `concat_ws(sep: str, f: any, r: any...) -> text`

Concatenates the text representation of non-NULL arguments from <code>f</code> and <code>r</code> separated by <code>sep</code>. The maximum length of the result string is 100 MiB.#### `convert_from(b: bytea, src_encoding: text) -> text`

Convert data <code>b</code> from original encoding specified by <code>src_encoding</code> into <code>text</code>.#### `decode(s: text, format: text) -> bytea`

Decode <code>s</code> using the specified textual representation. The maximum size of the result is 100 MiB. [(docs)](/sql/functions/encode)#### `encode(b: bytea, format: text) -> text`

Encode <code>b</code> using the specified textual representation [(docs)](/sql/functions/encode)#### `get_bit(b: bytea, n: int) -> int`

Return the <code>n</code>th bit from <code>b</code>, where the left-most bit in <code>b</code> is at the 0th position.#### `get_byte(b: bytea, n: int) -> int`

Return the <code>n</code>th byte from <code>b</code>, where the left-most byte in <code>b</code> is at the 0th position.#### `constant_time_eq(a: bytea, b: bytea) -> bool`

Returns <code>true</code> if the arrays are identical, otherwise returns <code>false</code>. The implementation mitigates timing attacks by making a best-effort attempt to execute in constant time if the arrays have the same length, regardless of their contents.#### `constant_time_eq(a: text, b: text) -> bool`

Returns <code>true</code> if the strings are identical, otherwise returns <code>false</code>. The implementation mitigates timing attacks by making a best-effort attempt to execute in constant time if the strings have the same length, regardless of their contents.#### `initcap(a: text) -> text`

Returns <code>a</code> with the first character of every word in upper case and all
other characters in lower case. Words are separated by non-alphanumeric
characters.#### `left(s: str, n: int) -> str`

The first <code>n</code> characters of <code>s</code>. If <code>n</code> is negative, all but the last <code>|n|</code> characters of <code>s</code>.#### `length(s: str) -> int`

Number of code points in <code>s</code>. [(docs)](/sql/functions/length)#### `length(b: bytea) -> int`

Number of bytes in <code>s</code>. [(docs)](/sql/functions/length)#### `length(s: bytea, encoding_name: str) -> int`

Number of code points in <code>s</code> after encoding [(docs)](/sql/functions/length)#### `lower(s: str) -> str`

Convert <code>s</code> to lowercase.#### `lpad(s: str, len: int) -> str`

Prepend <code>s</code> with spaces up to length <code>len</code>, or right truncate if <code>len</code> is less than the length of <code>s</code>. The maximum length of the result string is 100 MiB.#### `lpad(s: str, len: int, p: str) -> str`

Prepend <code>s</code> with characters pulled from <code>p</code> up to length <code>len</code>, or right truncate if <code>len</code> is less than the length of <code>s</code>. The maximum length of the result string is 100 MiB.#### `ltrim(s: str) -> str`

Trim all spaces from the left side of <code>s</code>.#### `ltrim(s: str, c: str) -> str`

Trim any character in <code>c</code> from the left side of <code>s</code>.#### `normalize(s: str) -> str`

Normalize <code>s</code> to Unicode Normalization Form NFC (default). [(docs)](/sql/functions/normalize)#### `normalize(s: str, form: keyword) -> str`

Normalize <code>s</code> to the specified Unicode normalization form (NFC, NFD, NFKC, or NFKD). [(docs)](/sql/functions/normalize)#### `octet_length(s: str) -> int`

Number of bytes in <code>s</code>.#### `octet_length(b: bytea) -> int`

Number of bytes in <code>b</code>.#### `parse_ident(ident: str[, strict_mode: bool]) -> str[]`

Given a qualified identifier like <code>a.&quot;b&quot;.c</code>, splits into an array of the
constituent identifiers with quoting removed and escape sequences decoded.
Extra characters after the last identifier are ignored unless the
<code>strict_mode</code> parameter is <code>true</code> (defaults to <code>false</code>).#### `position(sub: str IN s: str) -> int`

The starting index of <code>sub</code> within <code>s</code> or <code>0</code> if <code>sub</code> is not a substring of <code>s</code>.#### `regexp_match(haystack: str, needle: str [, flags: str]]) -> str[]`

Matches the regular expression <code>needle</code> against haystack, returning a
string array that contains the value of each capture group specified in
<code>needle</code>, in order. If <code>flags</code> is set to the string <code>i</code> matches
case-insensitively.#### `regexp_replace(source: str, pattern: str, replacement: str [, flags: str]]) -> str`

> **Warning:** This function has the potential to produce very large strings and
> may cause queries to run out of memory or crash. Use with caution.

<p>Replaces the first occurrence of <code>pattern</code> with <code>replacement</code> in <code>source</code>.
No match will return <code>source</code> unchanged.</p>
<p>If <code>flags</code> is set to <code>g</code>, all occurrences are replaced.
If <code>flags</code> is set to <code>i</code>, matches case-insensitively.</p>
<p><code>$N</code> or <code>$name</code> in <code>replacement</code> can be used to match capture groups.
<code>${N}</code> must be used to disambiguate capture group indexes from names if other characters follow <code>N</code>.
A <code>$$</code> in <code>replacement</code> will write a literal <code>$</code>.</p>
<p>See the <a href="https://docs.rs/regex/latest/regex/struct.Regex.html#method.replace" >rust regex docs</a> for more details about replacement.</p>
#### `regexp_matches(haystack: str, needle: str [, flags: str]]) -> str[]`

Matches the regular expression <code>needle</code> against haystack, returning a
string array that contains the value of each capture group specified in
<code>needle</code>, in order. If <code>flags</code> is set to the string <code>i</code> matches
case-insensitively. If <code>flags</code> is set to the string <code>g</code> all matches are
returned, otherwise only the first match is returned. Without the <code>g</code>
flag, the behavior is the same as <code>regexp_match</code>.#### `regexp_split_to_array(text: str, pattern: str [, flags: str]]) -> str[]`

Splits <code>text</code> by the regular expression <code>pattern</code> into an array.
If <code>flags</code> is set to <code>i</code>, matches case-insensitively.#### `repeat(s: str, n: int) -> str`

Replicate the string <code>n</code> times. The maximum length of the result string is 100 MiB.#### `replace(s: str, f: str, r: str) -> str`

<code>s</code> with all instances of <code>f</code> replaced with <code>r</code>. The maximum length of the result string is 100 MiB.#### `right(s: str, n: int) -> str`

The last <code>n</code> characters of <code>s</code>. If <code>n</code> is negative, all but the first <code>|n|</code> characters of <code>s</code>.#### `rtrim(s: str) -> str`

Trim all spaces from the right side of <code>s</code>.#### `rtrim(s: str, c: str) -> str`

Trim any character in <code>c</code> from the right side of <code>s</code>.#### `split_part(s: str, d: s, i: int) -> str`

Split <code>s</code> on delimiter <code>d</code>. Return the <code>str</code> at index <code>i</code>, counting from 1.#### `starts_with(s: str, prefix: str) -> bool`

Report whether <code>s</code> starts with <code>prefix</code>.#### `substring(s: str, start_pos: int) -> str`

Substring of <code>s</code> starting at <code>start_pos</code> [(docs)](/sql/functions/substring)#### `substring(s: str, start_pos: int, l: int) -> str`

Substring starting at <code>start_pos</code> of length <code>l</code> [(docs)](/sql/functions/substring)#### `substring('s' [FROM 'start_pos']? [FOR 'l']?) -> str`

Substring starting at <code>start_pos</code> of length <code>l</code> [(docs)](/sql/functions/substring)#### `translate(s: str, from: str, to: str) -> str`

Any character in <code>s</code> that matches a character in <code>from</code> is replaced by the corresponding character in <code>to</code>.
If <code>from</code> is longer than <code>to</code>, occurrences of the extra characters in <code>from</code> are removed.#### `trim([BOTH | LEADING | TRAILING]? ['c'? FROM]? 's') -> str`

<p>Trims any character in <code>c</code> from <code>s</code> on the specified side.</p>
<p>Defaults:</p>
<p>• Side: <code>BOTH</code></p>
<p>• <code>'c'</code>: <code>' '</code> (space)</p>
#### `try_parse_monotonic_iso8601_timestamp(s: str) -> timestamp`

Parses a specific subset of ISO8601 timestamps, returning <code>NULL</code> instead of
error on failure: <code>YYYY-MM-DDThh:mm:ss.sssZ</code> [(docs)](/sql/functions/pushdown)#### `upper(s: str) -> str`

Convert <code>s</code> to uppercase.#### `reverse(s: str) -> str`

Reverse the characters in <code>s</code>.#### `string_to_array(s: str, delimiter: str [, null_string: str]) -> str[]`

<p>Splits the string at occurrences of delimiter and returns a text array of
the split segments.</p>
<p>If <code>delimiter</code> is NULL, each character in the string will become a
separate element in the array.</p>
<p>If <code>delimiter</code> is an empty string, then the string is treated as a single
field.</p>
<p>If <code>null_string</code> is supplied and is not NULL, fields matching that string
are replaced by NULL.</p>
<p>If <code>s</code> is NULL, the result is NULL. If <code>s</code> is the empty string, the
result is an empty array (regardless of <code>delimiter</code> or <code>null_string</code>).</p>
<p>For example: <code>string_to_array('xx~~yy~~zz', '~~', 'yy')</code> → <code>{xx,NULL,zz}</code></p>
### Scalar functionsScalar functions take a list of scalar expressions#### `expression bool_op ALL(s: Scalars) -> bool`

<code>true</code> if applying <a href="#boolean-operators" >bool_op</a> to <code>expression</code> and every value of <code>s</code> evaluates to <code>true</code>.#### `expression bool_op ANY(s: Scalars) -> bool`

<code>true</code> if applying <a href="#boolean-operators" >bool_op</a> to <code>expression</code> and any
value of <code>s</code> evaluates to <code>true</code>. Avoid using in equi-join conditions as
its use in the equi-join condition can lead to a significant increase in
memory usage. See <a href="/transform-data/idiomatic-materialize-sql/any" >idiomatic Materialize
SQL</a> for the alternative.#### `expression IN(s: Scalars) -> bool`

<code>true</code> for each value in <code>expression</code> if it matches at least one element of <code>s</code>.#### `expression NOT IN(s: Scalars) -> bool`

<code>true</code> for each value in <code>expression</code> if it does not match any elements of <code>s</code>.#### `expression bool_op SOME(s: Scalars) -> bool`

<code>true</code> if applying <a href="#boolean-operators" >bool_op</a> to <code>expression</code> and any value of <code>s</code> evaluates to <code>true</code>.### Subquery functionsSubquery functions take a query, e.g. <a href="/sql/select" ><code>SELECT</code></a>#### `expression bool_op ALL(s: Query) -> bool`

<code>s</code> must return exactly one column; <code>true</code> if applying <a href="#boolean-operators" >bool_op</a> to <code>expression</code> and every value of <code>s</code> evaluates to <code>true</code>.#### `expression bool_op ANY(s: Query) -> bool`

<code>s</code> must return exactly one column; <code>true</code> if applying <a href="#boolean-operators" >bool_op</a> to <code>expression</code> and any value of <code>s</code> evaluates to <code>true</code>.#### `csv_extract(num_csv_col: int, col_name: string) -> col1: string, ... coln: string`

Extracts separated values from a column containing a CSV file formatted as a string [(docs)](/sql/functions/csv_extract)#### `EXISTS(s: Query) -> bool`

<code>true</code> if <code>s</code> returns at least one row.#### `expression IN(s: Query) -> bool`

<code>s</code> must return exactly one column; <code>true</code> for each value in <code>expression</code> if it matches at least one element of <code>s</code>.#### `NOT EXISTS(s: Query) -> bool`

<code>true</code> if <code>s</code> returns zero rows.#### `expression NOT IN(s: Query) -> bool`

<p><code>s</code> must return exactly one column; <code>true</code> for each value in <code>expression</code>
if it does not match any elements of <code>s</code>.</p>
> **Note:** When evaluating a `WHERE fieldX NOT IN (<subquery>)` predicate involving
> possible `NULL` values for `fieldX` or `<subquery>`, Materialize performs a
> cross join between the outer relation and the subquery to preserve SQL
> `NULL` semantics, which can significantly increase memory usage. If
> possible, rewrite using [idiomatic Materialize
> SQL](/transform-data/idiomatic-materialize-sql/not-in/).#### `expression bool_op SOME(s: Query) -> bool`

<code>s</code> must return exactly one column; <code>true</code> if applying <a href="#boolean-operators" >bool_op</a> to <code>expression</code> and any value of <code>s</code> evaluates to <code>true</code>.### Date and time functionsTime functions take or produce a time-like type, e.g. <a href="../types/date" ><code>date</code></a>, <a href="../types/timestamp" ><code>timestamp</code></a>, <a href="../types/timestamptz" ><code>timestamp with time zone</code></a>.#### `age(timestamp, timestamp) -> interval`

Subtracts one timestamp from another, producing a &ldquo;symbolic&rdquo; result that uses years and months, rather than just days.#### `current_timestamp() -> timestamptz`

The <code>timestamp with time zone</code> representing when the query was executed.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `date_bin(stride: interval, source: timestamp, origin: timestamp) -> timestamp`

Align <code>source</code> with <code>origin</code> along <code>stride</code> [(docs)](/sql/functions/date-bin)#### `date_trunc(time_component: str, val: timestamp) -> timestamp`

Largest <code>time_component</code> &lt;= <code>val</code> [(docs)](/sql/functions/date-trunc)#### `date_trunc(time_component: str, val: interval) -> interval`

Largest <code>time_component</code> &lt;= <code>val</code> [(docs)](/sql/functions/date-trunc)#### `EXTRACT(extract_expr) -> numeric`

Specified time component from value [(docs)](/sql/functions/extract)#### `date_part(time_component: str, val: timestamp) -> float`

Specified time component from value [(docs)](/sql/functions/date-part)#### `mz_now() -> mz_timestamp`

The logical time at which a query executes. Used for temporal filters and query timestamp introspection [(docs)](/sql/functions/now_and_mz_now)

**Note:** This function is [unmaterializable](#unmaterializable-functions), but can be used in limited contexts in materialized views as a [temporal filter](/transform-data/patterns/temporal-filters/).#### `now() -> timestamptz`

The <code>timestamp with time zone</code> representing when the query was executed [(docs)](/sql/functions/now_and_mz_now)

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `timestamp AT TIME ZONE zone -> timestamptz`

Converts <code>timestamp</code> to the specified time zone, expressed as an offset from UTC [(docs)](/sql/functions/timezone-and-at-time-zone)

**Known limitation:** You must explicitly cast the type for the time zone.#### `timestamptz AT TIME ZONE zone -> timestamp`

Converts <code>timestamp with time zone</code> from UTC to the specified time zone, expressed as the local time [(docs)](/sql/functions/timezone-and-at-time-zone)

**Known limitation:** You must explicitly cast the type for the time zone.#### `timezone(zone, timestamp) -> timestamptz`

Converts <code>timestamp</code> to specified time zone, expressed as an offset from UTC [(docs)](/sql/functions/timezone-and-at-time-zone)

**Known limitation:** You must explicitly cast the type for the time zone.#### `timezone(zone, timestamptz) -> timestamp`

Converts <code>timestamp with time zone</code> from UTC to specified time zone, expressed as the local time [(docs)](/sql/functions/timezone-and-at-time-zone)

**Known limitation:** You must explicitly cast the type for the time zone.#### `timezone_offset(zone: str, when: timestamptz) ->
(abbrev: str, base_utc_offset: interval, dst_offset: interval)`

<p>Describes a time zone&rsquo;s offset from UTC at a specified moment.</p>
<p><code>zone</code> must be a valid IANA Time Zone Database identifier.</p>
<p><code>when</code> is a <code>timestamp with time zone</code> that specifies the moment at which to determine <code>zone</code>&rsquo;s offset from UTC.</p>
<p><code>abbrev</code> is the abbreviation for <code>zone</code> that is in use at the specified moment (e.g., <code>EST</code> or <code>EDT</code>).</p>
<p><code>base_utc_offset</code> is the base offset from UTC at the specified moment (e.g., <code>-5 hours</code>). Positive offsets mean east of Greenwich; negative offsets mean west of Greenwich.</p>
<p><code>dst_offset</code> is the additional offset at the specified moment due to Daylight Saving Time rules (e.g., <code>1 hours</code>). If non-zero, Daylight Saving Time is in effect.</p>
#### `to_timestamp(val: double precision) -> timestamptz`

Converts Unix epoch (seconds since 00:00:00 UTC on January 1, 1970) to timestamp.#### `to_char(val: timestamp, format: str)`

Converts a timestamp into a string using the specified format [(docs)](/sql/functions/to_char)#### `justify_days(val: interval) -> interval`

Adjust interval so 30-day time periods are represented as months [(docs)](/sql/functions/justify-days)#### `justify_hours(val: interval) -> interval`

Adjust interval so 24-hour time periods are represented as days [(docs)](/sql/functions/justify-hours)#### `justify_interval(val: interval) -> interval`

Adjust interval using justify_days and justify_hours, with additional sign adjustments [(docs)](/sql/functions/justify-interval)### UUID functions#### `uuid_generate_v5(namespace: uuid, name: text) -> uuid`

Generates a <a href="https://www.rfc-editor.org/rfc/rfc4122#page-7" >version 5 UUID</a> (SHA-1) in the given namespace using the specified input name.### JSON functions#### `jsonb_agg(expression) -> jsonb`

Aggregate values (including nulls) as a jsonb array [(docs)](/sql/functions/jsonb_agg)#### `jsonb_array_elements(j: jsonb) -> Col<jsonb>`

<code>j</code>&rsquo;s elements if <code>j</code> is an array [(docs)](/sql/types/jsonb#jsonb_array_elements)#### `jsonb_array_elements_text(j: jsonb) -> Col<string>`

<code>j</code>&rsquo;s elements if <code>j</code> is an array [(docs)](/sql/types/jsonb#jsonb_array_elements_text)#### `jsonb_array_length(j: jsonb) -> int`

Number of elements in <code>j</code>&rsquo;s outermost array [(docs)](/sql/types/jsonb#jsonb_array_length)#### `jsonb_build_array(x: ...) -> jsonb`

Output each element of <code>x</code> as a <code>jsonb</code> array. Elements can be of heterogenous types [(docs)](/sql/types/jsonb#jsonb_build_array)#### `jsonb_build_object(x: ...) -> jsonb`

The elements of x as a <code>jsonb</code> object. The argument list alternates between keys and values [(docs)](/sql/types/jsonb#jsonb_build_object)#### `jsonb_each(j: jsonb) -> Col<(key: string, value: jsonb)>`

<code>j</code>&rsquo;s outermost elements if <code>j</code> is an object [(docs)](/sql/types/jsonb#jsonb_each)#### `jsonb_each_text(j: jsonb) -> Col<(key: string, value: string)>`

<code>j</code>&rsquo;s outermost elements if <code>j</code> is an object [(docs)](/sql/types/jsonb#jsonb_each_text)#### `jsonb_object_agg(keys, values) -> jsonb`

Aggregate keys and values (including nulls) as a <code>jsonb</code> object [(docs)](/sql/functions/jsonb_object_agg)#### `jsonb_object_keys(j: jsonb) -> Col<string>`

<code>j</code>&rsquo;s outermost keys if <code>j</code> is an object [(docs)](/sql/types/jsonb#jsonb_object_keys)#### `jsonb_pretty(j: jsonb) -> string`

Pretty printed (i.e. indented) <code>j</code> [(docs)](/sql/types/jsonb#jsonb_pretty)#### `jsonb_typeof(j: jsonb) -> string`

Type of <code>j</code>&rsquo;s outermost value. One of <code>object</code>, <code>array</code>, <code>string</code>, <code>number</code>, <code>boolean</code>, and <code>null</code> [(docs)](/sql/types/jsonb#jsonb_typeof)#### `jsonb_strip_nulls(j: jsonb) -> jsonb`

<code>j</code> with all object fields with a value of <code>null</code> removed. Other <code>null</code> values remain [(docs)](/sql/types/jsonb#jsonb_strip_nulls)#### `to_jsonb(v: T) -> jsonb`

<code>v</code> as <code>jsonb</code> [(docs)](/sql/types/jsonb#to_jsonb)### Table functionsTable functions evaluate to a collection of rows rather than a single row. You can use the <code>WITH ORDINALITY</code> and
<code>ROWS FROM</code> clauses together with table functions. For more details, see <a href="/sql/functions/table-functions" >Table functions</a>.#### `generate_series(start: int, stop: int) -> Col<int>`

Generate all integer values between <code>start</code> and <code>stop</code>, inclusive.#### `generate_series(start: int, stop: int, step: int) -> Col<int>`

Generate all integer values between <code>start</code> and <code>stop</code>, inclusive, incrementing by <code>step</code> each time.#### `generate_series(start: timestamp, stop: timestamp, step: interval) -> Col<timestamp>`

Generate all timestamp values between <code>start</code> and <code>stop</code>, inclusive, incrementing by <code>step</code> each time.#### `generate_subscripts(a: anyarray, dim: int) -> Col<int>`

Generates a series comprising the valid subscripts of the <code>dim</code>&lsquo;th dimension of the given array <code>a</code>.#### `regexp_extract(regex: str, haystack: str) -> Col<string>`

Values of the capture groups of <code>regex</code> as matched in <code>haystack</code>. Outputs each capture group in a separate column. At least one capture group is needed. (The capture groups are the parts of the regular expression between parentheses.)#### `regexp_split_to_table(text: str, pattern: str [, flags: str]]) -> Col<string>`

Splits <code>text</code> by the regular expression <code>pattern</code>.
If <code>flags</code> is set to <code>i</code>, matches case-insensitively.#### `unnest(a: anyarray)`

Expands the array <code>a</code> into a set of rows.#### `unnest(l: anylist)`

Expands the list <code>l</code> into a set of rows.#### `unnest(m: anymap)`

Expands the map <code>m</code> in a set of rows with the columns <code>key</code> and <code>value</code>.### Array functions#### `array_cat(a1: arrayany, a2: arrayany) -> arrayany`

Concatenates <code>a1</code> and <code>a2</code>.#### `array_fill(anyelement, int[], [, int[]]) -> anyarray`

Returns an array initialized with supplied value and dimensions, optionally with lower bounds other than 1.#### `array_length(a: arrayany, dim: bigint) -> int`

Returns the length of the specified dimension of the array.#### `array_position(haystack: anycompatiblearray, needle: anycompatible) -> int`

Returns the subscript of <code>needle</code> in <code>haystack</code>. Returns <code>null</code> if not found.#### `array_position(haystack: anycompatiblearray, needle: anycompatible, skip: int) -> int`

Returns the subscript of <code>needle</code> in <code>haystack</code>, skipping the first <code>skip</code> elements. Returns <code>null</code> if not found.#### `array_to_string(a: anyarray, sep: text [, ifnull: text]) -> text`

> **Warning:** This function has the potential to produce very large strings and
> may cause queries to run out of memory or crash. Use with caution.

<p>Concatenates the elements of <code>array</code> together separated by <code>sep</code>.
Null elements are omitted unless <code>ifnull</code> is non-null, in which case
null elements are replaced with the value of <code>ifnull</code>.</p>#### `array_remove(a: anyarray, e: anyelement) -> anyarray`

Returns the array <code>a</code> without any elements equal to the given value <code>e</code>.
The array must be one-dimensional. Comparisons are done using `IS NOT
DISTINCT FROM semantics, so it is possible to remove NULLs.### Hash functions#### `crc32(data: bytea) -> uint32`

Computes the 32-bit cyclic redundancy check of the given bytea <code>data</code> using the IEEE 802.3 polynomial.#### `crc32(data: text) -> uint32`

Computes the 32-bit cyclic redundancy check of the given text <code>data</code> using the IEEE 802.3 polynomial.#### `digest(data: text, type: text) -> bytea`

Computes a binary hash of the given text <code>data</code> using the specified <code>type</code> algorithm.
Supported hash algorithms are: <code>md5</code>, <code>sha1</code>, <code>sha224</code>, <code>sha256</code>, <code>sha384</code>, and <code>sha512</code>.#### `digest(data: bytea, type: text) -> bytea`

Computes a binary hash of the given bytea <code>data</code> using the specified <code>type</code> algorithm.
The supported hash algorithms are the same as for the text variant of this function.#### `hmac(data: text, key: text, type: text) -> bytea`

Computes a hashed MAC of the given text <code>data</code> using the specified <code>key</code> and
<code>type</code> algorithm. Supported hash algorithms are the same as for <code>digest</code>.#### `hmac(data: bytea, key: bytea, type: text) -> bytea`

Computes a hashed MAC of the given bytea <code>data</code> using the specified <code>key</code> and
<code>type</code> algorithm. The supported hash algorithms are the same as for <code>digest</code>.#### `kafka_murmur2(data: bytea) -> integer`

Computes the Murmur2 hash of the given bytea <code>data</code> using the seed used by Kafka&rsquo;s default partitioner and with the high bit cleared.#### `kafka_murmur2(data: text) -> integer`

Computes the Murmur2 hash of the given text <code>data</code> using the seed used by Kafka&rsquo;s default partitioner and with the high bit cleared.#### `md5(data: bytea) -> text`

Computes the MD5 hash of the given bytea <code>data</code>.
For PostgreSQL compatibility, returns a hex-encoded value of type <code>text</code> rather than <code>bytea</code>.#### `seahash(data: bytea) -> u64`

Computes the <a href="https://docs.rs/seahash" >SeaHash</a> hash of the given bytea <code>data</code>.#### `seahash(data: text) -> u64`

Computes the <a href="https://docs.rs/seahash" >SeaHash</a> hash of the given text <code>data</code>.#### `sha224(data: bytea) -> bytea`

Computes the SHA-224 hash of the given bytea <code>data</code>.#### `sha256(data: bytea) -> bytea`

Computes the SHA-256 hash of the given bytea <code>data</code>.#### `sha384(data: bytea) -> bytea`

Computes the SHA-384 hash of the given bytea <code>data</code>.#### `sha512(data: bytea) -> bytea`

Computes the SHA-512 hash of the given bytea <code>data</code>.### Window functions> **Tip:** For some window function query patterns, rewriting your query to not use
> window functions can yield better performance.  See [Idiomatic Materialize SQL](/transform-data/idiomatic-materialize-sql/) for details.

<p>Window functions compute values across sets of rows related to the current row.
For example, you can use a window aggregation to smooth measurement data by computing the average of the last 5
measurements before every row as follows:</p>
<pre tabindex="0"><code>SELECT
  avg(measurement) OVER (ORDER BY time ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
FROM measurements;
</code></pre><p>Window functions always need an <code>OVER</code> clause. For the <code>OVER</code> clause, Materialize supports the same
<a href="https://www.postgresql.org/docs/current/tutorial-window.html" >syntax as
PostgreSQL</a>,
but supports only the following frame modes:</p>
<ul>
<li>
<p>the <code>ROWS</code> frame mode.</p>
</li>
<li>
<p>the default frame, which is <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>.</p>
</li>
</ul>
> **Note:** For indexed views and materialized views that contain [window
> functions](/sql/functions/#window-functions) (including aggregate functions used
> with an `OVER` clause), when an input record in a partition is
> added/removed/changed, Materialize **recomputes the results from scratch** for
> that partition (instead of using incremental computation).
> The `PARTITION BY` clause of your window function determines your partitions. If
> `PARTITION BY` is omitted, all records belong to a single partition (i.e., any
> record change results in a recomputation from scratch over the whole input).
> To avoid performance issues that may arise as the number of records grows,
> consider rewriting your indexed views and materialized views to use idiomatic
> Materialize SQL instead of window functions. If your view definitions cannot be
> rewritten without the window functions and the performance of window functions
> is insufficient for your use case, please [contact our team](https://materialize.com/support/).
> See [Idiomatic Materialize SQL](/transform-data/idiomatic-materialize-sql/)
> for examples of rewriting window functions.

<p>In addition to the below window functions, you can use the <code>OVER</code> clause with any <a href="#aggregate-functions" >aggregation function</a>
(e.g., <code>sum</code>, <code>avg</code>) as well. Using an aggregation with an <code>OVER</code> clause is called a <em>window aggregation</em>. A
window aggregation computes the aggregate not on the groups specified by the <code>GROUP BY</code> clause, but on the frames
specified inside the <code>OVER</code> clause. (Note that a window aggregation produces exactly one output value <em>for each input
row</em>. This is different from a standard aggregation, which produces one output value for each <em>group</em> specified by
the <code>GROUP BY</code> clause.)</p>
#### `dense_rank() -> int`

Returns the rank of the current row within its partition without gaps, counting from 1.
Rows that compare equal will have the same rank.#### `first_value(value anycompatible) -> anyelement`

<p>Returns <code>value</code> evaluated at the first row of the window frame. The default window frame is
<code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>.</p>
<p>See also <a href="/transform-data/idiomatic-materialize-sql/first-value/" >Idiomatic Materialize SQL: First value</a>.</p>
#### `lag(value anycompatible [, offset integer [, default anycompatible ]]) -> int`

<p>Returns <code>value</code> evaluated at the row that is <code>offset</code> rows before the current row within the partition;
if there is no such row, instead returns <code>default</code> (which must be of a type compatible with <code>value</code>).
If <code>offset</code> is <code>NULL</code>, <code>NULL</code> is returned instead.
Both <code>offset</code> and <code>default</code> are evaluated with respect to the current row.
If omitted, <code>offset</code> defaults to 1 and <code>default</code> to <code>NULL</code>.</p>
<p>See also <a href="/transform-data/idiomatic-materialize-sql/lag/" >Idiomatic Materialize SQL: Lag over</a>.</p>
#### `last_value(value anycompatible) -> anyelement`

<p>Returns <code>value</code> evaluated at the last row of the window frame. The default window frame is
<code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>.</p>
<p>See also <a href="/transform-data/idiomatic-materialize-sql/last-value/" >Idiomatic Materialize SQL: Last
value</a>.</p>
#### `lead(value anycompatible [, offset integer [, default anycompatible ]]) -> int`

<p>Returns <code>value</code> evaluated at the row that is <code>offset</code> rows after the current row within the partition;
if there is no such row, instead returns <code>default</code> (which must be of a type compatible with <code>value</code>).
If <code>offset</code> is <code>NULL</code>, <code>NULL</code> is returned instead.
Both <code>offset</code> and <code>default</code> are evaluated with respect to the current row.
If omitted, <code>offset</code> defaults to 1 and <code>default</code> to <code>NULL</code>.</p>
<p>See also <a href="/transform-data/idiomatic-materialize-sql/lead/" >Idiomatic Materialize SQL: Lead
over</a>.</p>
#### `rank() -> int`

Returns the rank of the current row within its partition with gaps (counting from 1):
rows that compare equal will have the same rank, and then the rank is incremented by the number of rows that
compared equal.#### `row_number() -> int`

<p>Returns the number of the current row within its partition, counting from 1.
Rows that compare equal will be ordered in an unspecified way.</p>
<p>See also <a href="/transform-data/idiomatic-materialize-sql/top-k/" >Idiomatic Materialize SQL: Top-K</a>.</p>
### System information functionsFunctions that return information about the system.#### `mz_environment_id() -> text`

Returns a string containing a <code>uuid</code> uniquely identifying the Materialize environment.#### `mz_uptime() -> interval`

Returns the length of time that the materialized process has been running.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `mz_version() -> text`

Returns the server&rsquo;s version information as a human-readable string.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `mz_version_num() -> int`

Returns the server&rsquo;s version as an integer having the format <code>XXYYYZZ</code>, where <code>XX</code> is the major version, <code>YYY</code> is the minor version and <code>ZZ</code> is the patch version.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `mz_session_role_memberships() -> text[]`

Returns the names of the roles the current role is a member of, directly
or through other roles, including the current role itself.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `current_database() -> text`

Returns the name of the current database.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `current_catalog() -> text`

Alias for <code>current_database</code>.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `current_user() -> text`

Returns the name of the user who executed the containing query.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `current_role() -> text`

Alias for <code>current_user</code>.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `user() -> text`

Alias for <code>current_user</code>.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `session_user() -> text`

Returns the name of the user who initiated the database connection.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `mz_row_size(expr: Record) -> int`

Returns the number of bytes used to store a row.### PostgreSQL compatibility functionsFunctions whose primary purpose is to facilitate compatibility with PostgreSQL tools.
These functions may have suboptimal performance characteristics.#### `format_type(oid: int, typemod: int) -> text`

Returns the canonical SQL name for the type specified by <code>oid</code> with <code>typemod</code> applied.#### `current_schema() -> text`

Returns the name of the first non-implicit schema on the search path, or
<code>NULL</code> if the search path is empty.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `current_schemas(include_implicit: bool) -> text[]`

Returns the names of the schemas on the search path.
The <code>include_implicit</code> parameter controls whether implicit schemas like
<code>mz_catalog</code> and <code>pg_catalog</code> are included in the output.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `current_setting(setting_name: text[, missing_ok: bool]) -> text`

Returns the value of the named setting or error if it does not exist.
If <code>missing_ok</code> is true, return NULL if it does not exist.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `obj_description(oid: oid, catalog: text) -> text`

Returns the comment for a database object specified by its <code>oid</code> and the name of the containing system catalog.#### `col_description(oid: oid, column: int) -> text`

Returns the comment for a table column, which is specified by the <code>oid</code> of its table and its column number.#### `pg_backend_pid() -> int`

Returns the internal connection ID.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `pg_cancel_backend(connection_id: int) -> bool`

Cancels an in-progress query on the specified connection ID.
Returns whether the connection ID existed (not if it cancelled a query).

**Note:** This function is [side-effecting](#side-effecting-functions).#### `pg_column_size(expr: any) -> int`

Returns the number of bytes used to store any individual data value.#### `pg_size_pretty(expr: numeric) -> text`

Converts a size in bytes into a human-readable format.#### `pg_get_constraintdef(oid: oid[, pretty: bool]) -> text`

Returns the constraint definition for the given <code>oid</code>. Currently always
returns NULL since constraints aren&rsquo;t supported.#### `pg_get_indexdef(index: oid[, column: integer, pretty: bool]) -> text`

Reconstructs the creating command for an index. (This is a decompiled
reconstruction, not the original text of the command.) If column is
supplied and is not zero, only the definition of that column is reconstructed.#### `pg_get_ruledef(rule_oid: oid[, pretty bool]) -> text`

Reconstructs the creating command for a rule. This function
always returns NULL because Materialize does not support rules.#### `pg_get_userbyid(role: oid) -> text`

Returns the role (user) name for the given <code>oid</code>. If no role matches the
specified OID, the string <code>unknown (OID=oid)</code> is returned.#### `pg_get_viewdef(view_name: text[, pretty: bool]) -> text`

Returns the underlying SELECT command for the given view.#### `pg_get_viewdef(view_oid: oid[, pretty: bool]) -> text`

Returns the underlying SELECT command for the given view.#### `pg_get_viewdef(view_oid: oid[, wrap_column: integer]) -> text`

Returns the underlying SELECT command for the given view.#### `pg_has_role([user: name or oid,] role: text or oid, privilege: text) -> bool`

Alias for <code>has_role</code> for PostgreSQL compatibility.#### `pg_is_in_recovery() -> bool`

Returns if the a recovery is still in progress.#### `pg_table_is_visible(relation: oid) -> boolean`

Reports whether the relation with the specified OID is visible in the search path.#### `pg_tablespace_location(tablespace: oid) -> text`

Returns the path in the file system that the provided tablespace is on.#### `pg_type_is_visible(relation: oid) -> boolean`

Reports whether the type with the specified OID is visible in the search path.#### `pg_function_is_visible(relation: oid) -> boolean`

Reports whether the function with the specified OID is visible in the search path.#### `pg_typeof(expr: any) -> text`

Returns the type of its input argument as a string.#### `pg_encoding_to_char(encoding_id: integer) -> text`

PostgreSQL compatibility shim. Not intended for direct use.#### `pg_postmaster_start_time() -> timestamptz`

Returns the time when the server started.

**Note:** This function is [unmaterializable](#unmaterializable-functions).#### `pg_relation_size(relation: regclass[, fork: text]) -> bigint`

Disk space used by the specified fork (&lsquo;main&rsquo;, &lsquo;fsm&rsquo;, &lsquo;vm&rsquo;, or &lsquo;init&rsquo;)
of the specified table or index. If no fork is specified, it defaults
to &lsquo;main&rsquo;. This function always returns -1 because Materialize does
not store tables and indexes on local disk.#### `pg_stat_get_numscans(oid: oid) -> bigint`

Number of sequential scans done when argument is a table,
or number of index scans done when argument is an index.
This function always returns -1 because Materialize does
not collect statistics.#### `version() -> text`

Returns a PostgreSQL-compatible version string.

**Note:** This function is [unmaterializable](#unmaterializable-functions).### Access privilege inquiry functionsFunctions that allow querying object access privileges. None of the following functions consider
whether the provided role is a <em>superuser</em> or not.#### `has_cluster_privilege([role: text or oid,] cluster: text, privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the privilege on
the cluster with the specified cluster name. If the role is omitted then
the <code>current_role</code> is assumed.#### `has_connection_privilege([role: text or oid,] connection: text or oid, privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the privilege on
the connection with the specified connection name or OID. If the role is omitted then
the <code>current_role</code> is assumed.#### `has_database_privilege([role: text or oid,] database: text or oid, privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the privilege on
the database with the specified database name or OID. If the role is omitted then
the <code>current_role</code> is assumed.#### `has_schema_privilege([role: text or oid,] schema: text or oid, privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the privilege on
the schema with the specified schema name or OID. If the role is omitted then
the <code>current_role</code> is assumed.#### `has_role([user: name or oid,] role: text or oid, privilege: text) -> bool`

Reports whether the <code>user</code> has the privilege for <code>role</code>. <code>privilege</code> can either be <code>MEMBER</code>
or <code>USAGE</code>, however currently this value is ignored. The <code>PUBLIC</code> pseudo-role cannot be used
for the <code>user</code> nor the <code>role</code>. If the <code>user</code> is omitted then the <code>current_role</code> is assumed.#### `has_secret_privilege([role: text or oid,] secret: text or oid, privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the privilege on
the secret with the specified secret name or OID. If the role is omitted then
the <code>current_role</code> is assumed.#### `has_system_privilege([role: text or oid,] privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the system privilege.
If the role is omitted then the <code>current_role</code> is assumed.#### `has_table_privilege([role: text or oid,] relation: text or oid, privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the privilege on
the relation with the specified relation name or OID. If the role is omitted then
the <code>current_role</code> is assumed.#### `has_type_privilege([role: text or oid,] type: text or oid, privilege: text) -> bool`

Reports whether the role with the specified role name or OID has the privilege on
the type with the specified type name or OID. If the role is omitted then
the <code>current_role</code> is assumed.#### `mz_is_superuser() -> bool`

Reports whether the <code>current_role</code> is a superuser.

**Note:** This function is [unmaterializable](#unmaterializable-functions).

## Operators

### Generic operators

Operator | Computes
---------|---------
`val::type` | Cast of `val` as `type` ([docs](cast))

### Boolean operators

Operator | Computes
---------|---------
`AND` | Boolean "and"
`OR` | Boolean "or"
`=` | Equality. Do not use with `NULL` as `= NULL` always evaluates to `NULL`; instead, use `IS NULL` for null checks.
`<>` | Inequality. Do not use with `NULL` as `<> NULL` always evaluates to `NULL`; instead, use `IS NOT NULL` for null checks.
`!=` | Inequality. Do not use with `NULL` as `!= NULL` always evaluates to `NULL`; instead, use `IS NOT NULL` for null checks.
`<` | Less than
`>` | Greater than
`<=` | Less than or equal to
`>=` | Greater than or equal to
`a BETWEEN x AND y` | `a >= x AND a <= y`
`a NOT BETWEEN x AND y` | `a < x OR a > y`
`a IS NULL` | Evaluates to true if the value of a is `NULL`.
`a ISNULL` | Evaluates to true if the value of a is `NULL`.
`a IS NOT NULL` | Evaluates to true if the value of a is **NOT** `NULL`.
`a IS TRUE` | `a` is true, requiring `a` to be a boolean
`a IS NOT TRUE` | `a` is not true, requiring `a` to be a boolean
`a IS FALSE` | `a` is false, requiring `a` to be a boolean
`a IS NOT FALSE` | `a` is not false, requiring `a` to be a boolean
`a IS UNKNOWN` | `a = NULL`, requiring `a` to be a boolean
`a IS NOT UNKNOWN` | `a != NULL`, requiring `a` to be a boolean
`a LIKE match_expr [ ESCAPE escape_char ]` | `a` matches `match_expr`, using [SQL LIKE matching](https://www.postgresql.org/docs/13/functions-matching.html#FUNCTIONS-LIKE)
`a ILIKE match_expr [ ESCAPE escape_char ]` | `a` matches `match_expr`, using case-insensitive [SQL LIKE matching](https://www.postgresql.org/docs/13/functions-matching.html#FUNCTIONS-LIKE)

### Numbers operators

Operator | Computes
---------|---------
`+` | Addition
`-` | Subtraction
`*` | Multiplication
`/` | Division
`%` | Modulo
`&` | Bitwise AND
<code>&vert;</code> | Bitwise OR
`#` | Bitwise XOR
`~` | Bitwise NOT
`<<`| Bitwise left shift
`>>`| Bitwise right shift

### String operators

Operator | Computes
---------|---------
<code>&vert;&vert;</code> | Concatenation
`~~` | Matches LIKE pattern case sensitively, see [SQL LIKE matching](https://www.postgresql.org/docs/13/functions-matching.html#FUNCTIONS-LIKE)
`~~*` | Matches LIKE pattern case insensitively (ILIKE), see [SQL LIKE matching](https://www.postgresql.org/docs/13/functions-matching.html#FUNCTIONS-LIKE)
`!~~` | Matches NOT LIKE pattern (case sensitive), see [SQL LIKE matching](https://www.postgresql.org/docs/13/functions-matching.html#FUNCTIONS-LIKE)
`!~~*` | Matches NOT ILIKE pattern (case insensitive), see [SQL LIKE matching](https://www.postgresql.org/docs/13/functions-matching.html#FUNCTIONS-LIKE)
`~` | Matches regular expression, case sensitive
`~*` | Matches regular expression, case insensitive
`!~` | Matches regular expression case sensitively, and inverts the match
`!~*` | Match regular expression case insensitively, and inverts the match

The regular expression syntax supported by Materialize is documented by the
[Rust `regex` crate](https://docs.rs/regex/*/#syntax).
The maximum length of a regular expression is 1 MiB in its raw form, and 10 MiB
after compiling it. A regular expression may also contain at most 2000 character
classes, counting each Unicode, Perl, or POSIX class such as `\p{L}`, `\d`, or
`[[:alpha:]]`, and each range such as `a-z`.

> **Warning:** Materialize regular expressions are similar to, but not identical to, PostgreSQL
> regular expressions.

### Time-like operators

Operation | Computes
----------|------------
[`date`](../types/date) `+` [`interval`](../types/interval) | [`timestamp`](../types/timestamp)
[`date`](../types/date) `-` [`interval`](../types/interval) | [`timestamp`](../types/timestamp)
[`date`](../types/date) `+` [`time`](../types/time) | [`timestamp`](../types/timestamp)
[`date`](../types/date) `-` [`date`](../types/date) | [`integer`](../types/integer)
[`timestamp`](../types/timestamp) `+` [`interval`](../types/interval) | [`timestamp`](../types/timestamp)
[`timestamp`](../types/timestamp) `-` [`interval`](../types/interval) | [`timestamp`](../types/timestamp)
[`timestamp`](../types/timestamp) `-` [`timestamp`](../types/timestamp) | [`interval`](../types/interval)
[`time`](../types/time) `+` [`interval`](../types/interval) | `time`
[`time`](../types/time) `-` [`interval`](../types/interval) | `time`
[`time`](../types/time) `-` [`time`](../types/time) | [`interval`](../types/interval)

### JSON operators

Operator | RHS Type | Description
---------|----------|-------------
`->` | `text`, `int`| Access field by name or index position, and return `jsonb` ([docs](/sql/types/jsonb/#field-access-as-jsonb--))
`->>` | `text`, `int`| Access field by name or index position, and return `text` ([docs](/sql/types/jsonb/#field-access-as-text--))
`#>` | `text[]` | Access field by path, and return `jsonb` ([docs](/sql/types/jsonb/#path-access-as-jsonb-))
`#>>` | `text[]` | Access field by path, and return `text` ([docs](/sql/types/jsonb/#path-access-as-text-))
<code>&vert;&vert;</code> | `jsonb` | Concatenate LHS and RHS ([docs](/sql/types/jsonb/#jsonb-concat-))
`-` | `text` | Delete all values with key of RHS ([docs](/sql/types/jsonb/#remove-key--))
`@>` | `jsonb` | Does element contain RHS? ([docs](/sql/types/jsonb/#lhs-contains-rhs-))
<code>&lt;@</code> | `jsonb` | Does RHS contain element? ([docs](/sql/types/jsonb/#rhs-contains-lhs-))
`?` | `text` | Is RHS a top-level key? ([docs](/sql/types/jsonb/#search-top-level-keys-))

### Map operators

Operator | RHS Type | Description
---------|----------|-------------
`->` | `string` | Access field by name, and return target field ([docs](/sql/types/map/#retrieve-value-with-key--))
`@>` | `map` | Does element contain RHS? ([docs](/sql/types/map/#lhs-contains-rhs-))
<code>&lt;@</code> | `map` | Does RHS contain element? ([docs](/sql/types/map/#rhs-contains-lhs-))
`?` | `string` | Is RHS a top-level key? ([docs](/sql/types/map/#search-top-level-keys-))
`?&` | `string[]` | Does LHS contain all RHS top-level keys? ([docs](/sql/types/map/#search-for-all-top-level-keys-))
<code>?&#124;</code> | `string[]` | Does LHS contain any RHS top-level keys? ([docs](/sql/types/map/#search-for-any-top-level-keys-))

### List operators

List operators are [polymorphic](../types/list/#polymorphism).

Operator | Description
---------|-------------
<code>listany &vert;&vert; listany</code> | Concatenate the two lists.
<code>listany &vert;&vert; listelementany</code> | Append the element to the list.
<code>listelementany &vert;&vert; listany</code> | Prepend the element to the list.
<code>listany @&gt; listany</code> | Check if the first list contains all elements of the second list.
<code>listany &lt;@ listany</code> | Check if all elements of the first list are contained in the second list.
<code>listany &lt; listany</code>, and likewise <code>&lt;=</code>, <code>&gt;</code>, <code>&gt;=</code>, <code>=</code>, <code>&lt;&gt;</code> | Compare the two lists element by element. The first pair of elements that differ decides. A _NULL_ element is greater than any non-_NULL_ element, whatever `NULLS FIRST` or `NULLS LAST` says, since those only place values that are _NULL_ as a whole. A list is greater than any shorter list that it starts with. `ORDER BY`, `min`, and `max` order lists the same way.

## Pages in this section

- [Aggregate function filters](/sql/functions/filters/index.md): Use FILTER to specify which rows are sent to an aggregate function
- [array_agg function](/sql/functions/array_agg/index.md): Aggregate values (including nulls) as an array.
- [CAST and TRY_CAST](/sql/functions/cast/index.md): Returns the value converted to the specified type
- [COALESCE function](/sql/functions/coalesce/index.md): Returns the first non-NULL element provided.
- [csv_extract function](/sql/functions/csv_extract/index.md): Returns separated values from a column containing a CSV file formatted as a string.
- [date_bin function](/sql/functions/date-bin/index.md): Bins a timestamp into a specified interval
- [date_part function](/sql/functions/date-part/index.md): Returns a specified time component from a time-based value
- [date_trunc function](/sql/functions/date-trunc/index.md): Truncates a timestamp at the specified time component
- [datediff function](/sql/functions/datediff/index.md): Returns the difference between two date, time or timestamp expressions based on the specified date or time part.
- [encode and decode functions](/sql/functions/encode/index.md): Converts binary data to and from textual representations
- [EXTRACT function](/sql/functions/extract/index.md): Returns a specified time component from a time-based value
- [jsonb_agg function](/sql/functions/jsonb_agg/index.md): Aggregates values (including nulls) as a jsonb array.
- [jsonb_object_agg function](/sql/functions/jsonb_object_agg/index.md): Aggregate keys and values (including nulls) into a jsonb object
- [justify_days function](/sql/functions/justify-days/index.md): Adjust interval so 30-day time periods are represented as months
- [justify_hours function](/sql/functions/justify-hours/index.md): Adjust interval so 24-hour time periods are represented as days
- [justify_interval function](/sql/functions/justify-interval/index.md): Adjust interval using justify_days and justify_hours, with additional sign adjustments
- [LENGTH function](/sql/functions/length/index.md): Returns the number of characters in a string.
- [list_agg function](/sql/functions/list_agg/index.md): Concatenates input values (including nulls) into a string.
- [map_agg function](/sql/functions/map_agg/index.md): Aggregate keys and values (excluding null keys) into a map
- [normalize function](/sql/functions/normalize/index.md): Returns a string normalized to the specified Unicode normalization form.
- [now and mz_now functions](/sql/functions/now_and_mz_now/index.md): Details the differences between the `now()` and `mz_now()` functions.
- [Pushdown functions](/sql/functions/pushdown/index.md): Functions for use with the filter pushdown feature
- [string_agg function](/sql/functions/string_agg/index.md): Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null).
- [SUBSTRING function](/sql/functions/substring/index.md): Returns substring at specified positions
- [Table functions](/sql/functions/table-functions/index.md): Functions that return multiple rows
- [TIMEZONE and AT TIME ZONE functions](/sql/functions/timezone-and-at-time-zone/index.md): Converts timestamp to a different time zone.
- [to_char function](/sql/functions/to_char/index.md): Converts a timestamp into a string using the specified format.
