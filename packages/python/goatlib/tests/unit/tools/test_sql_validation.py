"""User SQL may read its declared inputs and nothing else.

The validator reads DuckDB's own parse tree, so whatever DuckDB would read is
what gets checked: quoting and comments cannot hide a table.

`preview-sql` runs user SQL on a connection with DuckLake attached, and the
workflow if node places a user expression inside a query on one. So the
validators accept only the input tables a request declares (plus the query's
own CTEs) and refuse qualified tables, files, table functions and the file,
database and catalog functions.
"""

import pytest
from goatlib.utils.sql_validation import validate_sql_expression, validate_sql_query

INPUTS = {"input_1", "input_2"}


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM input_1",
        "SELECT a.name, b.value FROM input_1 a JOIN input_2 b USING (id)",
        "WITH big AS (SELECT * FROM input_1 WHERE area > 10) SELECT count(*) FROM big",
        "SELECT ST_Area(geometry) AS area FROM input_1 WHERE name ILIKE '%park%'",
        "SELECT * FROM input_1 WHERE id IN (SELECT id FROM input_2)",
        "SELECT * FROM range(10)",
        "SELECT i FROM input_1, generate_series(1, 3) AS g(i)",
        "SELECT * FROM unnest([1, 2, 3])",
        "SELECT i.name, j.key, j.value FROM input_1 i, json_each(i.props) AS j",
        "SELECT * FROM json_tree('{\"a\": [1, 2]}')",
        # Comment markers and keywords inside strings and quoted names.
        "SELECT COALESCE(name, '--') FROM input_1",
        "SELECT * FROM input_1 WHERE note LIKE '%--%' OR note LIKE '%/*%'",
        'SELECT 1 AS "--", \'a;b\' AS "Update" FROM input_1',
        "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < 3) "
        "SELECT * FROM r",
        "SELECT * FROM input_1 UNION ALL SELECT * FROM input_2",
        "FROM input_1 SELECT name",
        "SELECT * EXCLUDE (geometry) FROM input_1 QUALIFY row_number() OVER () < 5",
        "SELECT * FROM (VALUES (1), (2)) AS v(a)",
        "WITH a AS (SELECT * FROM input_1), b AS (SELECT * FROM a) SELECT * FROM b",
        "SELECT * FROM (WITH c AS (SELECT * FROM input_1) SELECT * FROM c) AS s",
    ],
)
def test_queries_over_the_declared_inputs_pass(sql: str) -> None:
    validate_sql_query(sql, INPUTS)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM lake.main.t_0123456789abcdef0123456789abcdef",
        "SELECT * FROM main.t_0123456789abcdef0123456789abcdef",
        "SELECT * FROM t_0123456789abcdef0123456789abcdef",
        "SELECT * FROM input_1 JOIN lake.user_x.t_y USING (id)",
        "SELECT (SELECT count(*) FROM lake.user_x.t_y) FROM input_1",
        "SELECT * FROM read_parquet('/app/data/ducklake/x.parquet')",
        "SELECT * FROM read_csv_auto('/etc/passwd')",
        "SELECT * FROM '/app/data/temporary/user_x/t_y.parquet'",
        "SELECT * FROM glob('/app/data/*')",
        "SELECT * FROM duckdb_tables()",
        "SELECT * FROM query('SELECT 1')",
        "SELECT getenv('HOME') FROM input_1",
        "SELECT current_setting('s3_secret_access_key') FROM input_1",
        "SELECT * FROM range((SELECT count(*) FROM lake.user_x.t_y))",
        "SELECT * FROM generate_series(1, (SELECT max(id) FROM t_y))",
        # A table hidden from a comment-stripping check by markers in strings.
        "SELECT '/*' AS a, * FROM lake.main.t_v WHERE '*/' = '*/'",
        'SELECT "/*", * FROM lake.main.t_x, input_1 AS "*/"',
        "SELECT $$'$$, * FROM lake.main.t_x",
        # A CTE name is visible inside its own query only, and only after
        # its definition: DuckDB resolves these two against the catalog.
        "SELECT * FROM t_abc, (WITH t_abc AS (SELECT 1) SELECT * FROM t_abc) AS s",
        "WITH a AS (SELECT * FROM t_abc), t_abc AS (SELECT 1) SELECT * FROM a",
        "WITH t_abc AS (SELECT * FROM t_abc) SELECT * FROM t_abc",
        "SELECT * FROM (SHOW TABLES)",
        "SELECT * FROM (DESCRIBE input_1)",
        "SELECT lake.main.f(1) FROM input_1",
        "SELECT getvariable('x') FROM input_1",
        "SELECT * FROM input_1; SELECT * FROM input_2",
        "ATTACH 'other.db' AS other",
    ],
)
def test_anything_beyond_the_declared_inputs_is_refused(sql: str) -> None:
    with pytest.raises(ValueError):
        validate_sql_query(sql, INPUTS)


def test_without_declared_inputs_tables_must_still_be_plain_names() -> None:
    validate_sql_query("SELECT * FROM anything")
    with pytest.raises(ValueError):
        validate_sql_query("SELECT * FROM lake.main.t_x")
    with pytest.raises(ValueError):
        validate_sql_query("SELECT * FROM read_parquet('x.parquet')")


@pytest.mark.parametrize(
    "expression",
    ["count(*) > 10", "avg(population) > 5 AND max(area) < 3", "sum(x) = 0"],
)
def test_a_condition_over_columns_passes(expression: str) -> None:
    validate_sql_expression(expression)


@pytest.mark.parametrize(
    "expression",
    [
        "(SELECT count(*) > 0 FROM lake.user_x.t_y)",
        "EXISTS (SELECT 1 FROM input_1)",
        "read_csv('/etc/passwd') IS NOT NULL",
        "getenv('HOME') = 'x'",
        "count(*) > 0) AS r FROM lake.user_x.t_y --",
        # Closing the wrapping parenthesis to add clauses or columns.
        "1=1) LIMIT (100000000",
        "TRUE) GROUP BY (1",
        "x > 1) ORDER BY (1",
        "TRUE) AS r, 1 AS (x",
        "name = 'a",
    ],
)
def test_a_condition_with_a_query_table_or_file_is_refused(expression: str) -> None:
    with pytest.raises(ValueError):
        validate_sql_expression(expression)


@pytest.mark.parametrize(
    "sql",
    [
        # Pivot columns taken from the data: DuckDB plans these as two
        # statements, so they are checked with a stand-in value list.
        "SELECT * FROM (PIVOT (SELECT name, kind, val FROM input_1) ON kind USING sum(val)) AS r",
        "PIVOT input_1 ON kind USING sum(val) GROUP BY name",
        "PIVOT input_1 ON kind",
        "SELECT * FROM (\n  PIVOT (\n    SELECT a.name, a.kind || '_' || b.code AS col_key, a.val\n"
        "    FROM input_1 a JOIN input_2 b ON a.id = b.id\n  ) ON col_key USING sum(val)\n) AS result",
        # Listed values and the SQL-standard form, as before.
        "PIVOT input_1 ON kind IN ('a', 'b') USING sum(val)",
        "SELECT * FROM input_1 PIVOT (sum(val) FOR kind IN ('a', 'b'))",
        # The keyword inside a string or a quoted name is left alone.
        "SELECT 'PIVOT x ON y' AS note, \"pivot\" FROM input_1",
    ],
)
def test_pivots_over_the_declared_inputs_pass(sql: str) -> None:
    validate_sql_query(sql, INPUTS)


@pytest.mark.parametrize(
    "sql",
    [
        "PIVOT (SELECT * FROM secret_table) ON kind USING sum(val)",
        "PIVOT input_1 ON kind USING sum((SELECT max(x) FROM lake.main.t_other))",
        "SELECT * FROM (PIVOT read_parquet('/data/x.parquet') ON kind USING sum(val))",
        "PIVOT input_1 ON (SELECT kind FROM other_table LIMIT 1) USING sum(val)",
        "PIVOT input_1 ON getenv('HOME') USING sum(val)",
        "SELECT * FROM json_each((SELECT props FROM secret_table))",
    ],
)
def test_a_pivot_reaching_beyond_the_declared_inputs_is_refused(sql: str) -> None:
    with pytest.raises(ValueError):
        validate_sql_query(sql, INPUTS)


USING_KEY = (
    "WITH RECURSIVE g(id, v) USING KEY (id) AS ("
    " SELECT id, v FROM input_1 UNION SELECT q.id, q.v + 1 FROM recurring.g q WHERE q.v < 3"
    ") SELECT * FROM g"
)


def test_a_using_key_cte_reads_its_own_recurring_table() -> None:
    # `recurring.g` is the CTE's previous iteration, not a schema.
    validate_sql_query(USING_KEY, INPUTS)


@pytest.mark.parametrize(
    "sql",
    [
        # Outside the recursive CTE it names, `recurring.` is a schema.
        "SELECT * FROM recurring.input_1",
        "WITH g AS (SELECT * FROM input_1) SELECT * FROM recurring.g",
        USING_KEY.replace("SELECT * FROM g", "SELECT * FROM recurring.g"),
        # Only the CTE's own name: not another table in that schema.
        USING_KEY.replace("FROM recurring.g q", "FROM recurring.other q"),
    ],
)
def test_recurring_is_refused_outside_its_own_recursive_cte(sql: str) -> None:
    with pytest.raises(ValueError):
        validate_sql_query(sql, INPUTS)
