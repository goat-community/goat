CREATE OR REPLACE FUNCTION bezirke()
RETURNS TABLE (nr integer, name text, geom geometry) AS
$$
select nr, name, geom
from modeshare;
$$
LANGUAGE sql;

COMMENT ON FUNCTION bezirke() 
IS '**FOR-API-FUNCTION** RETURNS col_names[nr integer, name text, geom geometry] **FOR-API-FUNCTION**';