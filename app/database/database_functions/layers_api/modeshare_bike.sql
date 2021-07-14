CREATE OR REPLACE FUNCTION modeshare_bike()
RETURNS TABLE (vi_nummer TEXT, share integer, score integer, geom geometry) AS
$$
select name, cast(share_bike*100 as integer) as share, 
case when share_bike < 0.16 then 1
when share_bike > 0.15 and share_bike < 0.21 then 2
when share_bike > 0.20 and share_bike < 0.26 then 3
when share_bike > 0.25 then 4
end as score, geom
from modeshare;
$$
LANGUAGE sql;

COMMENT ON FUNCTION modeshare_bike() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';