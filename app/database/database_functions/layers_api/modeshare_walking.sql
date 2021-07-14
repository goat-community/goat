CREATE OR REPLACE FUNCTION modeshare_walking()
RETURNS TABLE (vi_nummer TEXT, share integer, score integer, geom geometry) AS
$$
select name, cast(share_foot*100 as integer) as share, 
case when share_foot < 0.21 then 1
when share_foot > 0.20 and share_foot < 0.26 then 2
when share_foot > 0.25 and share_foot < 0.31 then 3
when share_foot > 0.30 then 4
end as score, geom
from modeshare;
$$
LANGUAGE sql;

COMMENT ON FUNCTION modeshare_walking() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';