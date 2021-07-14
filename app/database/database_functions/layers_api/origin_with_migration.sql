CREATE OR REPLACE FUNCTION origin_with_migration()
RETURNS TABLE (vi_nummer TEXT, share integer, score text, geom geometry) AS
$$
select m.vi,cast(m.migr as integer) as share, 
case 
	when m.migr = 0 then 0::text
	when m.migr = 999999 then 'nodata'::text
	when m.migr > 0 and m.migr < 999999 then p.score::text
end as score,
m.geom
from muc_origin m
full outer join
(select vi, migr as share, 
case WHEN migr < 500 THEN 1 
WHEN migr  BETWEEN 500 AND 999 THEN 2
WHEN migr  BETWEEN 1000 AND 1999 THEN 3 
WHEN migr  > 1999 THEN 4 END AS score, geom 
from muc_origin where migr > 0 and migr < 99999) p 
on p.vi = m.vi
order by score, share;
$$
LANGUAGE sql;

COMMENT ON FUNCTION origin_with_migration() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';
