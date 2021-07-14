CREATE OR REPLACE FUNCTION age_65_over()
RETURNS TABLE (vi_nummer TEXT, share integer, score text, geom geometry) AS
$$ 
select m.vi_nummer,cast(m.sh_65_ov as integer) as share, 
case 
	when m.sh_65_ov = 0 then 0::text
	when m.sh_65_ov = 999999 then 'nodata'::text
	when m.sh_65_ov > 0 and m.sh_65_ov < 999999 then p.score::text
end as score,
m.geom
from muc_age m
full outer join
(select vi_nummer, sh_65_ov as share, 
case WHEN sh_65_ov > 0 and sh_65_ov < 0.10 THEN 1 
WHEN sh_65_ov  BETWEEN 0.10 AND 0.1999 THEN 2
WHEN sh_65_ov  BETWEEN 0.20 AND 0.2999 THEN 3 
WHEN sh_65_ov  BETWEEN 0.30 AND 0.3999 THEN 4 
WHEN sh_65_ov  > 0.3999 THEN 5 END AS score, geom 
from muc_age where sh_65_ov > 0 and sh_65_ov < 99999) p 
on p.vi_nummer = m.vi_nummer
order by score, share;
$$
LANGUAGE sql;

COMMENT ON FUNCTION age_65_over() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,share,score,geom] **FOR-API-FUNCTION**';