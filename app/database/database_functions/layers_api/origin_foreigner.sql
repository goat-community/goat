CREATE OR REPLACE FUNCTION origin_foreigner()
RETURNS TABLE (vi_nummer TEXT, share integer, score text, geom geometry) AS
$$
select m.vi,cast(m.foreign as integer) as share, 
case 
	when m.foreign = 0 then 0::text
	when m.foreign = 999999 then 'nodata'::text
	when m.foreign > 0 and m.foreign < 999999 then p.score::text
end as score,
m.geom
from muc_origin m
full outer join
(select vi, o.foreign as share, 
case WHEN o.foreign < 500 THEN 1 
WHEN o.foreign  BETWEEN 500 AND 999 THEN 2
WHEN o.foreign  BETWEEN 1000 AND 1999 THEN 3
WHEN o.foreign  > 1999 THEN 4 END AS score, geom 
from muc_origin o where o.foreign > 0 and o.foreign < 99999) p 
on p.vi = m.vi
order by score, share;
$$
LANGUAGE sql;

COMMENT ON FUNCTION origin_foreigner() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';
