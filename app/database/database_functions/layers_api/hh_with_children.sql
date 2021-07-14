CREATE OR REPLACE FUNCTION hh_with_children()
RETURNS TABLE (vi_nummer TEXT, share integer, score text, geom geometry) AS
$$
select m.vi,cast(m.sh_child*100 as integer) as share, 
case 
	when m.sh_child = 0 then 0::text
	when m.sh_child = 999999 then 'nodata'::text
	when m.sh_child > 0 and m.sh_child < 999999 then p.score::text
end as score,
m.geom
from muc_households m
full outer join
(select vi, sh_child as share, 
case WHEN sh_child < 0.10 THEN 1 
WHEN sh_child  BETWEEN 0.10 AND 0.19999 THEN 2
WHEN sh_child  BETWEEN 0.2 AND 0.29999 THEN 3 
WHEN sh_child  BETWEEN 0.3 AND 0.39999 THEN 4 
WHEN sh_child  > 0.39999 THEN 5 END AS score, geom 
from muc_households where sh_child > 0 and sh_child < 99999) p 
on p.vi = m.vi
order by score, share;
$$
LANGUAGE sql;

COMMENT ON FUNCTION hh_with_children() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';

