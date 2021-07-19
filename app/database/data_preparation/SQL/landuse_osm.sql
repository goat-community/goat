DROP TABLE IF EXISTS landuse_osm;
CREATE TABLE landuse_osm AS 
SELECT CASE 
	WHEN p.landuse in ('basin','reservoir','salt_pond','waters') then 'water' 
	WHEN p.landuse in ('allotments','aquaculture','fallow','farmland','farmyard','greenhouse_horticulture','orchard','pasture','plant_nursery','plantation','vineyard') then 'agriculture' 
	WHEN p.landuse in ('forest','grass','meadow','green_area') then 'nature' 
	WHEN p.landuse in ('garden','national_park','nature_reserve','park','village_green','recreation_ground','leisure') then 'leisure' 
	WHEN p.landuse in ('cemetery','grave_yard') then 'cemetery' 
	WHEN p.landuse in ('residential','garages') then 'residential' 
	WHEN p.landuse in ('commercial','retail') then 'commercial' 
	WHEN p.landuse in ('school','university','hospital','college','churchyard','religious','community') then 'community' 
	WHEN p.landuse in ('industrial','landfill','quarry') then 'industrial' 
	WHEN p.landuse in ('highway','parking','railway') then 'transportation' 
	WHEN p.landuse in ('military') then 'military' 
ELSE NULL END AS landuse_simplified, landuse, p.tourism, p.amenity, p.name, ST_Intersection(p.way,s.geom) AS geom 
FROM planet_osm_polygon p, study_area s
WHERE landuse IS NOT NULL
AND ST_Intersects(p.way,s.geom);

INSERT INTO landuse_osm 
SELECT 'transportation' AS landuse_simplified, p.amenity AS landuse, p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) AS geom 
FROM planet_osm_polygon p, study_area s
WHERE amenity = 'parking' 
AND ST_Intersects(s.geom,p.way);

INSERT INTO landuse_osm 
SELECT 'community' AS landuse_simplified, p.amenity AS landuse, p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) AS geom 
FROM planet_osm_polygon p, study_area s
WHERE (amenity = 'hospital' OR amenity = 'school') 
AND ST_Intersects(s.geom,p.way);

INSERT INTO landuse_osm 
SELECT 'water' AS landuse_simplified, p.leisure AS landuse, p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) AS geom 
FROM planet_osm_polygon p , study_area s
WHERE leisure = 'swimming_pool' AND ST_Intersects(s.geom,p.way);

INSERT INTO landuse_osm 
SELECT 'leisure' AS landuse_simplified, p.leisure AS landuse, p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) as geom 
FROM planet_osm_polygon p , study_area s
WHERE leisure IS NOT NULL
AND leisure <> 'swimming_pool'
AND ST_Intersects(s.geom,p.way);

INSERT INTO landuse_osm 
SELECT 'water' AS landuse_simplified, p."natural" AS landuse,  p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) as geom 
FROM planet_osm_polygon p , study_area s
WHERE "natural"='water' and ST_Intersects(s.geom,p.way);

INSERT INTO landuse_osm 
SELECT  'nature' AS landuse_simplified, p."natural" AS landuse, p.amenity, p.leisure, p.name,ST_Intersection(p.way,s.geom) as geom 
FROM planet_osm_polygon p , study_area s
WHERE "natural" IN ('scrub','wood','wetland','grassland','heath') 
AND ST_Intersects(s.geom,p.way);

ALTER TABLE landuse_osm ADD gid serial;
ALTER TABLE landuse_osm ADD PRIMARY KEY(gid);
CREATE INDEX ON landuse_osm USING gist(geom);

DROP TABLE IF EXISTS buildings_osm;
CREATE TABLE buildings_osm as 
SELECT ROW_NUMBER() OVER() AS gid, p.osm_id,p.building, p.amenity,
CASE 
WHEN p.building = 'yes' AND amenity IS NULL AND leisure IS NULL THEN 'potential_residents' 
WHEN p.building IN (SELECT UNNEST(select_from_variable_container('building_types_residential'))) THEN 'with_residents'
ELSE 'no_residents' END AS residential_status,
tags -> 'addr:street' AS street, "addr:housenumber" AS housenumber,
ST_Area(p.way::geography)::integer as area, 
CASE WHEN (p.tags -> 'building:levels')~E'^\\d+$' THEN (p.tags -> 'building:levels')::smallint ELSE null end as building_levels,
CASE WHEN (p.tags -> 'roof:levels')~E'^\\d+$' THEN (p.tags -> 'roof:levels')::smallint ELSE null end as roof_levels,
p.way as geom
FROM planet_osm_polygon p, study_area s
WHERE p.building IS NOT NULL
AND ST_Intersects(s.geom,p.way);

CREATE INDEX ON buildings_osm USING GIST(geom);
ALTER TABLE buildings_osm ADD PRIMARY key(gid);