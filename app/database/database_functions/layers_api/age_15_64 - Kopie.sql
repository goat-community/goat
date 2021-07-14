CREATE OR REPLACE FUNCTION age_15_64()
RETURNS TABLE (vi_nummer TEXT, pop integer, score text, geom geometry) AS
$$ 
select m.vi_nummer,m.age_15_64 as pop, 
case 
	when m.age_15_64 = 0 then 0::text
	when m.age_15_64 = 999999 then 'missingdata'::text
	when m.age_15_64 > 0 and m.age_15_64 < 999999 then p.score::text
end as score,
m.geom
from muc_age m
full outer join
(select vi_nummer, age_15_64 as pop, 
case WHEN age_15_64 BETWEEN 1 AND 1500 THEN 1 
WHEN age_15_64  BETWEEN 1501 AND 3000 THEN 2
WHEN age_15_64  BETWEEN 3001 AND 4500 THEN 3 
WHEN age_15_64  BETWEEN 4501 AND 6000 THEN 4 
WHEN age_15_64  > 6001 THEN 5 END AS score, geom 
from muc_age where age_15_64 > 0 and age_15_64 < 999999) p 
on p.vi_nummer = m.vi_nummer
order by score, pop;
$$
LANGUAGE sql;

COMMENT ON FUNCTION age_15_64() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,pop,score,geom] **FOR-API-FUNCTION**';
