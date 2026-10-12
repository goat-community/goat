---
description: "Write SQL queries against up to three connected inputs (input_1 to input_3) in a Custom SQL workflow node, with spatial functions and workflow variables."
---

# Custom SQL

The **Custom SQL** tool allows you to write custom SQL queries for data analysis directly within your workflows. This powerful feature enables advanced data processing that goes beyond GOAT's built-in tools.

:::warning Advanced Feature
This is an advanced feature intended for users with SQL knowledge. Incorrect queries may cause workflows to fail or produce unexpected results. If you need help writing SQL queries, you can use AI assistants to help generate and explain the code.
:::

## Overview

The Custom SQL tool connects to GOAT's DuckDB backend, giving you direct access to query your datasets using SQL syntax. You can:

- Execute complex analytical queries
- Join multiple datasets
- Perform aggregations and statistical calculations  
- Create derived datasets with custom logic
- Access advanced spatial functions

## Using Custom SQL

### Adding the Tool

<div class="step">
  <div class="step-number">1</div>
  <div class="content">In the <strong>Tools</strong> tab of the right panel, find <strong>Custom SQL</strong> under <strong>Data Management</strong> and drag it onto your workflow canvas.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content">Connect up to three dataset or tool nodes to provide data sources for your query. They are listed under <strong>Connected Inputs</strong>.</div>
</div>

<div class="step">
  <div class="step-number">3</div>
  <div class="content">Click on the Custom SQL node to open the <strong>Configuration Panel</strong> on the right.</div>
</div>

### Writing SQL Queries

In the **SQL Query** section of the configuration panel, click **Write SQL Query** (or **Edit SQL Query** once a query exists) to open the **Custom SQL Editor**, and write your query in the editor at the top:

```sql
SELECT
  h.*,
  p.population_density
FROM input_1 h
JOIN input_2 p ON ST_Intersects(h.geometry, p.geometry)
WHERE p.population_density > 1000
```

The editor capitalizes SQL keywords and suggests table and column names as you type; press `Tab` to accept a suggestion. On the **Build** tab below the editor, pick **Tables**, **Operators** or a function category on the left and click an entry in the middle list to insert it at the cursor; clicking a column inserts it with its table name, for example `input_1.height`. The **Help** panel on the right describes the entry under your mouse pointer.

When the query is ready, click **Apply** to save it to the node. The query is then shown in the **SQL Query** section; click it to open the editor again.

#### Input References

- **input_1, input_2, input_3**: Reference your connected datasets using these table names
- The number corresponds to the connection order on the node
- You can connect up to 3 input datasets per Custom SQL node

#### Additional Layers

Besides the connected inputs, you can query up to two more layers without connecting them on the canvas. Under **Additional Layers**, click **Add layer** and choose **From Project** or **My datasets**. Each added layer is referenced by its **Table Alias** (`extra_1` and `extra_2` by default), which you can change; aliases may contain only letters, numbers and underscores.

#### Geometry and Units

Every layer has its geometry in a column named `geometry`, in WGS 84 longitude and latitude (EPSG:4326). Spatial functions therefore measure in degrees: `ST_Distance(a.geometry, b.geometry)` returns degrees, not metres. For metres and square metres, first transform the geometry into a projected coordinate system, for example UTM zone 32N, which covers most of Germany:

```sql
ST_Transform(geometry, 'EPSG:4326', 'EPSG:25832', always_xy := true)
```

For other regions, use the UTM zone of the area. Return the original `geometry` column, or transform the result back to EPSG:4326, so the result shows in the right place on the map.

#### Available Functions

The Custom SQL tool supports standard SQL functions plus spatial operations:

**Spatial Functions:**
- `ST_Intersects()` - Check if geometries intersect
- `ST_Within()` - Test if geometry is within another
- `ST_DWithin()` - Test if geometries are within a distance of each other
- `ST_Distance()` - Calculate distances between geometries
- `ST_Buffer()` - Create buffers around geometries
- `ST_Area()` - Calculate geometry area
- `ST_Length()` - Calculate line length
- `ST_Transform()` - Transform geometries to another coordinate system

Distances, areas, lengths and buffer sizes are in the units of the coordinate system; see [Geometry and Units](#geometry-and-units).

**Analytical Functions:**
- `AVG()`, `SUM()`, `COUNT()` - Statistical aggregations
- `PERCENTILE_CONT()` - Calculate percentiles
- `ROW_NUMBER()`, `RANK()` - Window functions
- `CASE WHEN` - Conditional logic

### Query Validation

<div class="step">
  <div class="step-number">1</div>
  <div class="content"><strong>Automatic Check</strong>: Shortly after you stop typing, the query is checked against the columns of its input tables. A green check mark in the top-right corner of the editor means the query is valid. If it is invalid, a red cross appears, the editor border turns red and the first error message is shown below the editor. <strong>Apply</strong> stays disabled until the error is fixed.</div>
</div>

<div class="step">
  <div class="step-number">2</div>
  <div class="content"><strong>Preview Results</strong>: Switch to the <strong>Preview</strong> tab to run the query and see the first 10 rows of the result, with the name and type of each column. If no input data is available yet, for example because an upstream tool has not been run, the preview lists only the columns the query will return.</div>
</div>

## Examples

### Basic Filtering and Selection
```sql
-- Residential buildings taller than 10 m
SELECT building_type, height, geometry
FROM input_1
WHERE building_type = 'residential'
  AND height > 10
```

### Spatial Join Analysis
```sql
-- Amenities within 500 m of a transit stop, with the distance in metres
WITH a AS (
  SELECT name, amenity_type, geometry,
    ST_Transform(geometry, 'EPSG:4326', 'EPSG:25832', always_xy := true) AS geom_m
  FROM input_1
), t AS (
  SELECT stop_name,
    ST_Transform(geometry, 'EPSG:4326', 'EPSG:25832', always_xy := true) AS geom_m
  FROM input_2
)
SELECT
  a.name AS amenity_name,
  a.amenity_type,
  t.stop_name,
  ST_Distance(a.geom_m, t.geom_m) AS distance_m,
  a.geometry
FROM a
JOIN t ON ST_DWithin(a.geom_m, t.geom_m, 500)
ORDER BY distance_m
```

### Aggregation by Area
```sql
-- Number of points in each district, including districts without points
SELECT
  admin.district_name,
  COUNT(points.geometry) AS point_count,
  ANY_VALUE(admin.geometry) AS geometry
FROM input_2 admin
LEFT JOIN input_1 points ON ST_Within(points.geometry, admin.geometry)
GROUP BY admin.district_name
```

## Best Practices

:::tip Performance
- Join tables on spatial predicates such as `ST_Intersects()` or `ST_Within()` rather than comparing every pair of rows yourself
- Limit results during development with `LIMIT 100`
- Test with small datasets first, then scale up
:::

:::warning Data Types
- Ensure geometry columns are properly formatted for spatial operations
- Cast data types explicitly when joining different datasets
- Check for NULL values in critical columns
:::

### Query Optimization

**Use Spatial Predicates**: Join on spatial predicates such as `ST_Intersects()`, `ST_Within()` or `ST_DWithin()`, so the database can match nearby geometries efficiently.

**Column Selection**: Select only the columns you need rather than using `SELECT *`.

**Proper Joins**: Use appropriate join types (INNER, LEFT, RIGHT) based on your analysis needs.

### Error Handling

Common issues and solutions:

- **Unknown table**: Ensure input datasets are properly connected and that the query uses their table names (`input_1` to `input_3`, or the **Table Alias** of an additional layer)
- **Unknown column**: Check column names in your input datasets; the **Tables** list on the **Build** tab shows the columns of each table
- **Geometry error**: Verify geometry columns are valid and properly formatted
- **Only SELECT statements are allowed**: Write a single `SELECT` query (optionally starting with `WITH`); statements that change data, such as `CREATE`, `INSERT`, `UPDATE` or `DELETE`, are rejected
- **Long-running query**: Break complex queries into smaller steps

## Output and Integration

The Custom SQL tool creates a new temporary layer containing your query results, named after the **Result Layer Name** field in the **Output** section (default: `Custom SQL`). After a successful run, the configuration panel shows the **Dataset details** of the result and these **Actions**:

- **Table**: Show the result in the data view below the canvas
- **Map**: Show the result on a map (only for results with a geometry column)
- **Save dataset**: Save the result as a permanent dataset

You can also:

- Connect the output to other workflow tools for further analysis
- Add a **Save as dataset** node to save the results as a permanent dataset each time the workflow runs

:::info Variables Support
Custom SQL queries support [workflow variables](variables.md) using the `{{@variable_name}}` syntax for parameterized queries. Type `{{@` in the editor to get a list of the workflow's variables.
:::

## Limitations

- Maximum of 3 connected inputs and 2 additional layers per Custom SQL node
- Only a single `SELECT` statement is allowed
- Results without a geometry column are created as a table and cannot be shown on the map
- Some advanced DuckDB functions may not be available

For more complex analysis requirements, consider using multiple Custom SQL nodes or combining with other workflow tools.
