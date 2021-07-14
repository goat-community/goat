CREATE OR REPLACE FUNCTION age_14_under()
RETURNS TABLE (vi_nummer TEXT, pop integer, score text, geom geometry) AS
$$
select m.vi_nummer,m.age_0_14 as pop, 
case 
	when m.age_0_14 = 0 then 0::text
	when m.age_0_14 = 999999 then 'nodata'::text
	when m.age_0_14 > 0 and m.age_0_14 < 999999 then p.score::text
end as score,
m.geom
from muc_age m
full outer join
(select vi_nummer, age_0_14 as pop, 
case WHEN age_0_14 BETWEEN 1 AND 500 THEN 1 
WHEN age_0_14  BETWEEN 501 AND 1000 THEN 2
WHEN age_0_14  BETWEEN 1001 AND 1500 THEN 3 
WHEN age_0_14  BETWEEN 1501 AND 2000 THEN 4 
WHEN age_0_14  > 2001 THEN 5 END AS score, geom 
from muc_age where age_0_14 > 0 and age_0_14 < 99999) p 
on p.vi_nummer = m.vi_nummer
order by score, pop;
$$
LANGUAGE sql;

COMMENT ON FUNCTION age_14_under() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,pop,score,geom] **FOR-API-FUNCTION**';
