CREATE OR REPLACE FUNCTION hh_two_parent()
RETURNS TABLE (vi_nummer TEXT, twoparent numeric, score text, geom geometry) AS
$$
select m.vi_nummer, m.twoparent, 
case 
	when m.twoparent = 0 then 0::text
	when m.twoparent = 999999 then 'nodata'::text
	when m.twoparent > 0 and m.twoparent < 999999 then p.score::text
end as score,
m.geom
from muc_households m
full outer join
(select vi_nummer, twoparent, 
case WHEN twoparent < 151 THEN 1 
WHEN twoparent  BETWEEN 151 AND 300 THEN 2
WHEN twoparent  BETWEEN 301 AND 450 THEN 3 
WHEN twoparent > 450 THEN 4 
end as score, geom
from muc_households where twoparent > 0 and twoparent < 99999) p 
on p.vi_nummer = m.vi_nummer
order by score;
$$
LANGUAGE sql;

COMMENT ON FUNCTION hh_two_parent() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,twoparent,score,geom] **FOR-API-FUNCTION**';

