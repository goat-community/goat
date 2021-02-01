
CREATE OR REPLACE VIEW layer_metadata AS
WITH metadata AS (
        SELECT
                p.proname,
                regexp_replace(
                      d.description,
                      '\*\*FOR\-API\-FUNCTION\*\*|\]|\[|RETURNS col_names|geom,|,geom|geom|geometry,|,geometry|geometry|origin_geometry,|origin_geometry|\s',
                      '',
                      'g'
                ) as "columns",
                'function' AS layer_type,
                'geom' AS geom_columns,
                '4326' AS srid,
                string_to_array(regexp_replace(regexp_replace(pg_catalog.pg_get_function_identity_arguments(p.oid),' [^,]+, ', ',','g'),'| [^, [^,]+', '','g'), ',') AS args
          FROM pg_proc p
          LEFT JOIN pg_description d ON d.objoid = p.oid
          WHERE description LIKE '%**FOR-API-FUNCTION**%'
      UNION ALL
      SELECT
            t.table_name AS "proname",
            string_agg(concat('"',c2.column_name,'"'), ',') AS "columns",
            'table' AS layer_type,
            'geom' AS geom_columns,
            '4326' AS srid,
            NULL
      FROM
            information_schema.tables t
            JOIN information_schema.columns c ON c.table_name = t.table_name
            AND c.table_schema = t.table_schema
            JOIN information_schema.columns c2 ON t.table_name = c2.table_name
            AND c2.column_name NOT IN('geom', 'geometry', 'origin_geometry')
      WHERE
            c.column_name = 'geom'
            AND t.table_schema NOT IN('information_schema', 'pg_catalog')
            AND t.table_type = 'BASE TABLE'
      GROUP BY
            t.table_name,
            t.table_schema
),
json_rows AS (
      SELECT
            proname,
            jsonb_build_object(
                  'columns',
                  "columns",
                  'layer_type',
                  layer_type,
                  'geom',
                  geom_columns,
                  'srid',
                  srid,
                  'args',
                  args
            ) AS json_data
      FROM
            metadata
)
SELECT jsonb_object_agg(proname, json_data) metadata
FROM json_rows;
