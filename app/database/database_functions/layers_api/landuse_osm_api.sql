/*This here need refactoring!*/
CREATE OR REPLACE FUNCTION landuse_osm_api()
RETURNS TABLE (landuse text, landuse_detailed TEXT, amenity TEXT, leisure TEXT, name TEXT, geom geometry) AS
$$
	WITH l AS 
	(
		select 
		case 
		when l.landuse in ('basin','reservoir','salt_pond','waters') then 'water' 
		when l.landuse in ('allotments','aquaculture','fallow','farmland','farmyard','greenhouse_horticulture','orchard','pasture','plant_nursery','plantation','vineyard') then 'agriculture' 
		when l.landuse in ('forest','grass','meadow','green_area') then 'nature' 
		when l.landuse in ('garden','national_park','nature_reserve','park','village_green','recreation_ground','leisure') then 'leisure' 
		when l.landuse in ('cemetery','grave_yard') then 'cemetery' 
		when l.landuse in ('residential','garages') then 'residential' 
		when l.landuse in ('commercial','retail') then 'commercial' 
		when l.landuse in ('school','university','hospital','college','churchyard','religious','community') then 'community' 
		when l.landuse in ('industrial','landfill','quarry') then 'industrial' 
		when l.landuse in ('highway','parking','railway') then 'transportation' 
		when l.landuse in ('military') then 'military' 
		else null end as landuse, 
		l.landuse as landuse_detailed, null as amenity, null as leisure, l.name, ST_Intersection(l.geom,s.geom) as geom  from landuse_osm l, study_area s
		where ST_Intersects(s.geom,l.geom)
		union
		SELECT 'community' as landuse, null as landuse_detailed, p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) as geom FROM planet_osm_polygon p, study_area s
		where (amenity = 'hospital' or amenity = 'school') and ST_Intersects(s.geom,p.way)
		union
		SELECT 'waters' as landuse ,null as landuse_detailed,  p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) as geom FROM planet_osm_polygon p , study_area s
		where leisure = 'swimming_pool' and ST_Intersects(s.geom,p.way)
		union
		SELECT 'leisure' as landuse ,null as landuse_detailed,  p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) as geom FROM planet_osm_polygon p , study_area s
		where leisure is not null and leisure not in ('swimming_pool') and ST_Intersects(s.geom,p.way)
		union
		SELECT 'water' as landuse ,null as landuse_detailed,  p.amenity, p.leisure, p.name, ST_Intersection(p.way,s.geom) as geom FROM planet_osm_polygon p , study_area s
		where "natural"='water' and ST_Intersects(s.geom,p.way)
		union
		SELECT  'nature' as landuse ,null as landuse_detailed, p.amenity, p.leisure, p.name,ST_Intersection(p.way,s.geom) as geom FROM planet_osm_polygon p , study_area s
		where "natural" in ('scrub','wood','wetland','grassland','heath') and ST_Intersects(s.geom,p.way)
	)
	SELECT * 
	FROM l 
	WHERE landuse IS NOT NULL
$$
LANGUAGE sql;

COMMENT ON FUNCTION landuse_osm_api() 
IS '**FOR-API-FUNCTION** RETURNS col_names[landuse,landuse_detailed,amenity,leisure,name] **FOR-API-FUNCTION**';