CREATE OR REPLACE FUNCTION hh_single_parent()
RETURNS TABLE (vi_nummer TEXT, singlepar numeric, score text, geom geometry) AS
$$
select m.vi_nummer, m.singlepar, 
case 
	when m.singlepar = 0 then 0::text
	when m.singlepar = 999999 then 'nodata'::text
	when m.singlepar > 0 and m.singlepar < 999999 then p.score::text
end as score,
m.geom
from muc_households m
full outer join
(select vi_nummer, singlepar, 
case WHEN singlepar < 51 THEN 1 
WHEN singlepar  BETWEEN 51 AND 100 THEN 2
WHEN singlepar  BETWEEN 101 AND 200 THEN 3 
WHEN singlepar > 201 THEN 4 
end as score, geom
from muc_households where singlepar > 0 and singlepar < 99999) p 
on p.vi_nummer = m.vi_nummer
order by score;
$$
LANGUAGE sql;

COMMENT ON FUNCTION hh_single_parent() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,singplepar,score,geom] **FOR-API-FUNCTION**';

