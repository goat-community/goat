CREATE OR REPLACE FUNCTION st_polygrid(geometry, numeric) RETURNS geometry AS
$$
SELECT
ST_SetSRID(ST_Collect(ST_POINT(x,y)), ST_SRID($1))
FROM
generate_series(ST_XMin($1)::numeric, ST_xmax($1)::numeric, $2) as x,
generate_series(ST_ymin($1)::numeric, ST_ymax($1)::numeric,$2) as y
WHERE
ST_Intersects($1,ST_SetSRID(ST_POINT(x,y), ST_SRID($1)))
$$
LANGUAGE sql VOLATILE;

--the st_polygrid function creates a pointgrid (MULTIPOINT) with customizable resolution in a certain geometry or area
--Example: st_polygrid(area.geometry, 0.1)

DROP TABLE IF EXISTS landuse_res;
DROP TABLE IF EXISTS population;
DROP TABLE IF EXISTS gridandpoints;
DROP TABLE IF EXISTS points_res;

--selects residential areas from the Urban Atlas landuse

CREATE TABLE landuse_res as
SELECT l.gid, l.landuse, l.geom
FROM landuse l, study_area_union a
WHERE l.landuse NOT IN (SELECT UNNEST(variable_array) FROM variable_container WHERE
identifier = 'custom_landuse_no_residents') AND st_intersects(l.geom,a.geom)=true;

ALTER TABLE landuse_res ADD COLUMN density numeric;

--different densities for pointgrid depending on landuse (less is more dense)

UPDATE landuse_res
SET density=0.0003
WHERE landuse='Continuous urban fabric (S.L. : > 80%)';

UPDATE landuse_res
SET density=0.00035
WHERE landuse='Discontinuous dense urban fabric (S.L. : 50% -  80%)';

UPDATE landuse_res
SET density=0.0004
WHERE landuse='Discontinuous medium density urban fabric (S.L. : 30% - 50%)';

UPDATE landuse_res
SET density=0.00045
WHERE landuse='Discontinuous low density urban fabric (S.L. : 10% - 30%)';

UPDATE landuse_res
SET density=0.0005
WHERE landuse='Discontinuous very low density urban fabric (S.L. : < 10%)';

--creation of pointgrids in each residential area

CREATE TABLE points_res as
WITH x AS
(SELECT st_polygrid(l.geom,l.density) AS geom
FROM landuse_res l
)
SELECT (st_dump(geom) ).geom as geom
FROM x;

ALTER TABLE points_res ADD COLUMN gid integer;

UPDATE points_res
SET gid = census.gid::integer
FROM census
WHERE st_intersects(points_res.geom, census.geom);

--combining points with census grid

CREATE TABLE gridandpoints AS
SELECT p.gid, sum(ST_NPoints(p.geom))::numeric as npoints
FROM points_res p, census c
WHERE p.gid=c.gid
GROUP BY p.gid;

ALTER TABLE gridandpoints ADD COLUMN pop integer;
ALTER TABLE gridandpoints ADD COLUMN pop_per_point numeric;

--calculation of residents per points

UPDATE gridandpoints
SET pop = census.pop::integer
FROM census
WHERE gridandpoints.gid = census.gid;

UPDATE gridandpoints SET pop_per_point = CEIL(pop/npoints);

--preparation of population layer

CREATE TABLE population as
SELECT points_res.*, gridandpoints.pop_per_point as population
FROM points_res, gridandpoints
WHERE points_res.gid = gridandpoints.gid;

CREATE INDEX index_population ON population USING GIST (geom);
ALTER TABLE population ADD COLUMN id serial;
ALTER TABLE population ADD PRIMARY KEY(id);

DROP TABLE IF EXISTS landuse_res;
DROP TABLE IF EXISTS gridandpoints;
DROP TABLE IF EXISTS points_res;