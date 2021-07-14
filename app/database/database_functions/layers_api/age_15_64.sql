CREATE OR REPLACE FUNCTION age_15_64()
RETURNS TABLE (vi_nummer TEXT, share integer, score text, geom geometry) AS
$$ 
select m.vi_nummer,cast(m.sh_15_64 as integer) as share, 
case 
	when m.sh_15_64 = 0 then 0::text
	when m.sh_15_64 = 999999 then 'nodata'::text
	when m.sh_15_64 > 0 and m.sh_15_64 < 999999 then p.score::text
end as score,
m.geom
from muc_age m
full outer join
(select vi_nummer, sh_15_64 as share, 
case WHEN sh_15_64 < 0.5 THEN 1 
WHEN sh_15_64  BETWEEN 0.5 AND 0.5999 THEN 2
WHEN sh_15_64  BETWEEN 0.6 AND 0.6999 THEN 3 
WHEN sh_15_64  BETWEEN 0.7 AND 0.7999 THEN 4 
WHEN sh_15_64  > 0.7999 THEN 5 END AS score, geom 
from muc_age where sh_15_64 > 0 and sh_15_64 < 999999) p 
on p.vi_nummer = m.vi_nummer
order by score, share;
$$
LANGUAGE sql;

COMMENT ON FUNCTION age_15_64() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';
