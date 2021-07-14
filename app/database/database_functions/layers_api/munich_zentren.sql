CREATE OR REPLACE FUNCTION munich_zentren()
RETURNS TABLE (name text, score integer, geom geometry) AS
$$
select name,
case when z."type" = 'Innenstadt' and status = 'existent' then 0
when z."type" = 'Stadtteilzentrum' and status = 'existent' then 1
when z."type" = 'Quartierszentrum' and status = 'existent' then 2
when z."type" = 'Stadtteilzentrum' and status = 'planned' then 3
when z."type" = 'Quartierszentrum' and status = 'planned' then 4
end as score, geom
from muc_centres z;
$$
LANGUAGE sql;

COMMENT ON FUNCTION munich_zentren() 
IS '**FOR-API-FUNCTION** RETURNS col_names[name,score,geom] **FOR-API-FUNCTION**';
