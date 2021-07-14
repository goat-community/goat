CREATE OR REPLACE FUNCTION hh_without_children()
RETURNS TABLE (vi_nummer TEXT, share integer, score text, geom geometry) AS
$$
select m.vi,cast(m.sh_nochild*100 as integer) as share, 
case 
	when m.sh_nochild = 0 then 0::text
	when m.sh_nochild = 999999 then 'nodata'::text
	when m.sh_nochild > 0 and m.sh_nochild < 999999 then p.score::text
end as score,
m.geom
from muc_households m
full outer join
(select vi, sh_nochild as share, 
case WHEN sh_nochild < 0.60 THEN 1 
WHEN sh_nochild  BETWEEN 0.60 AND 0.69999 THEN 2
WHEN sh_nochild  BETWEEN 0.7 AND 0.79999 THEN 3 
WHEN sh_nochild  BETWEEN 0.8 AND 0.89999 THEN 4 
WHEN sh_nochild  > 0.89999 THEN 5 END AS score, geom 
from muc_households where sh_nochild > 0 and sh_nochild < 99999) p 
on p.vi = m.vi
order by score, share;
$$
LANGUAGE sql;

COMMENT ON FUNCTION hh_without_children() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';

