CREATE OR REPLACE FUNCTION modeshare_put()
RETURNS TABLE (vi_nummer TEXT, share integer, score integer, geom geometry) AS
$$
select name, cast(share_put*100 as integer) as share, 
case when share_put < 0.21 then 1
when share_put > 0.20 and share_put < 0.26 then 2
when share_put > 0.25 and share_put < 0.31 then 3
when share_put > 0.30 then 4
end as score, geom
from modeshare;
$$
LANGUAGE sql;

COMMENT ON FUNCTION modeshare_put() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';