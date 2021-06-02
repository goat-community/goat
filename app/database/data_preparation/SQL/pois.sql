CREATE TABLE pois_osm
(
GID BIGSERIAL PRIMARY KEY,
osm_id bigint,
origin_geometry VARCHAR(255),
access VARCHAR(255),
"addr:housenumber" VARCHAR(255),
amenity VARCHAR(255),
shop VARCHAR(255),
leisure VARCHAR(255),
tourism VARCHAR(255),
name VARCHAR(255),
sport VARCHAR(255),
opening_hours VARCHAR(255),
tags HSTORE,
geom GEOMETRY (Geometry,4326),
wheelchair VARCHAR(255)
) 
;

CREATE INDEX pois_osm_index
  ON pois_osm
  USING GIST (geom);


--1.Points POI
--Only amenity (without shop and leisure)
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber",amenity, shop, leisure, 
name, tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE amenity IS NOT NULL AND amenity <> 'school' AND amenity <> 'kindergarten' AND shop is NULL AND leisure is NULL;


--Only shop (without amenity and leisure)
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id, 'point' as origin_geometry, access,"addr:housenumber", amenity, shop, leisure, name, tags -> 'opening_hours' as opening_hours, tags, way as geom, tags -> 'wheelchair' as wheelchair
FROM planet_osm_point
WHERE amenity IS NULL AND shop is NOT NULL AND leisure is NULL;

--Only leisure (without amenity and shop)
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber", amenity, shop, leisure,
name,tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE leisure is NOT NULL AND amenity is NULL AND shop is NULL;


--Only tourism (without amenity)
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, tourism, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber", amenity, shop, leisure, tourism,
name,tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE tourism IS NOT NULL and amenity is NULL;


--Only sport without shop
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, sport, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'point' as origin_geometry, access,"addr:housenumber",amenity, shop, leisure, 
name,sport,tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_point
WHERE sport IS NOT NULL AND shop IS NULL;
--1.End of Points POI


--2.Polygon POI
--Only amenity (without shop and leisure)
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber",amenity, shop, leisure, 
name, tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE amenity IS NOT NULL AND amenity <> 'school' AND amenity <> 'kindergarten' AND shop is NULL AND leisure is NULL;

--Only shop (without amenity and leisure)
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber",amenity, shop, leisure, 
name,tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE amenity IS NULL AND shop is NOT NULL AND leisure is NULL;


--Only leisure (without amenity and shop)
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber", amenity, shop, leisure,
name,tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE leisure is NOT NULL AND amenity is NULL AND shop is NULL;


--Only tourism without amenity 
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, tourism, name, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber", amenity, shop, leisure, tourism,
name,tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE tourism IS NOT NULL and amenity is NULL;


--Only sport without shop
INSERT INTO pois_osm(osm_id, origin_geometry, access, "addr:housenumber", amenity, shop, leisure, name, sport, opening_hours, tags, geom, wheelchair)
SELECT osm_id,'polygon' as origin_geometry, access,"addr:housenumber",amenity, shop, leisure, 
name,sport,tags -> 'opening_hours' as opening_hours,tags, way as geom, tags -> 'wheelchair' as wheelchair  
FROM planet_osm_polygon
WHERE sport IS NOT NULL AND shop IS NULL
--2.End of Polygon POI
