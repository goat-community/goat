CREATE OR REPLACE FUNCTION munich_density()
RETURNS TABLE (vi_nummer TEXT, score integer, geom geometry) AS
$$ 
select vi_nummer, 
case 
when pop_dens < 1 then 0
when pop_dens > 1 and pop_dens < 5000 then 1
when pop_dens > 4999 and pop_dens < 10000 then 2
when pop_dens > 9999 and pop_dens < 15000 then 3
when pop_dens > 14999 and pop_dens < 20000 then 4
when pop_dens > 19999 then 5
end as score, geom
from muc_density;
$$
LANGUAGE sql;

COMMENT ON FUNCTION munich_density() 
IS '**FOR-API-FUNCTION** RETURNS col_names[vi_nummer,score,geom] **FOR-API-FUNCTION**';

