CREATE OR REPLACE FUNCTION age_14_under()
RETURNS TABLE (vi_nummer TEXT, share integer, score text, geom geometry) AS
$$
select m.vi_nummer,cast(m.sh_0_14*100 as integer) as share, 
case 
	when m.sh_0_14 = 0 then 0::text
	when m.sh_0_14 = 999999 then 'nodata'::text
	when m.sh_0_14 > 0 and m.sh_0_14 < 999999 then p.score::text
end as score,
m.geom
from muc_age m
full outer join
(select vi_nummer, sh_0_14 as share, 
case WHEN sh_0_14 < 0.1 THEN 1 
WHEN sh_0_14  BETWEEN 0.1 AND 0.14999 THEN 2
WHEN sh_0_14  BETWEEN 0.15 AND 0.19999 THEN 3 
WHEN sh_0_14  BETWEEN 0.2 AND 0.24999 THEN 4 
WHEN sh_0_14  > 0.24999 THEN 5 END AS score, geom 
from muc_age where sh_0_14 > 0 and sh_0_14 < 99999) p 
on p.vi_nummer = m.vi_nummer
order by score, share;
$$
LANGUAGE sql;

COMMENT ON FUNCTION age_14_under() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';
