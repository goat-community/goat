
--Drops the former created tables
DROP TABLE IF EXISTS building_derived_addresses;
DROP TABLE IF EXISTS directly_derived_addresses;
DROP TABLE IF EXISTS entrances_derived_addresses;
DROP TABLE IF EXISTS all_addresses;
DROP TABLE IF EXISTS house_address;


--Find all addresses tagged as points
SELECT osm_id,tags -> 'addr:street' as street,"addr:housenumber" as housenumber,way as geom 
INTO directly_derived_addresses 
FROM planet_osm_point  
WHERE (tags -> 'addr:street') IS NOT NULL 
OR "addr:housenumber" IS NOT NULL 
ORDER by street,"addr:housenumber";

CREATE INDEX index_directly_derived_addresses ON directly_derived_addresses USING GIST (geom);

--Find all buildings which have an address attached
SELECT h.* INTO house_address 
FROM  
(SELECT osm_id,tags -> 'addr:street' as street,"addr:housenumber" as housenumber, tags -> 'addr:city' as city,way as geom 
FROM planet_osm_polygon  
WHERE (tags -> 'addr:street') IS NOT NULL 
OR "addr:housenumber" IS NOT NULL) h;






CREATE INDEX index_houses_address ON house_address USING GIST (geom);

--Find all entrances which are lying on a building

SELECT x.osm_id,h.street,h.housenumber,x.geom 
INTO entrances_derived_addresses 
FROM (
	SELECT osm_id,way as geom,tags -> 'door' as door,tags -> 'entrance' as entrance,tags, tags -> 'level' as level1, 
	exist(tags, 'subway') subway, 
	exist(tags, 'entrance_marker:subway') subway1, 
	exist(tags, 'indoor') indoor, 
	exist(tags, 'entrance_marker:s-train') sbahn, 
	exist(tags, 'entrance_marker:tram') tram 
	FROM planet_osm_point WHERE "addr:housenumber" IS NULL 
	) x, house_address h 

WHERE subway = false AND subway1 =false AND indoor=false AND sbahn=false AND tram=false 
AND entrance IS NOT NULL 
AND entrance <> 'emergency' 
AND level1 IS NULL 
AND st_intersects(x.geom,h.geom);

CREATE INDEX index_entrances_derived_addresses  ON entrances_derived_addresses USING GIST (geom);


--entrances was changes to entrances derived (it has to be checked if results are good enough)
with x as (
	SELECT h.osm_id
	FROM house_address h,entrances_derived_addresses e  
	WHERE st_intersects(e.geom,h.geom)
),
xx as (
	SELECT x.osm_id,street,housenumber,city,geom
	FROM house_address x WHERE x.osm_id  
	not in (SELECT * FROM x)
)
SELECT osm_id,street,housenumber,st_centroid(geom) as geom 
INTO building_derived_addresses 
FROM xx;


CREATE INDEX index_building_derived_addresses ON building_derived_addresses USING GIST (geom);

--Add columns for the origin of the address

ALTER TABLE building_derived_addresses add column origin varchar(20);
ALTER TABLE directly_derived_addresses add column origin varchar(20);
ALTER TABLE entrances_derived_addresses add column origin varchar(20);

UPDATE building_derived_addresses set origin='building';
UPDATE directly_derived_addresses set origin='point_data';
UPDATE entrances_derived_addresses set origin ='entrances';


ALTER TABLE building_derived_addresses add column x varchar;
UPDATE building_derived_addresses set x=concat(street,housenumber);

ALTER TABLE entrances_derived_addresses add column x varchar;
UPDATE entrances_derived_addresses set x=concat(street,housenumber);

ALTER TABLE directly_derived_addresses add column x varchar;
UPDATE directly_derived_addresses set x=concat(street,housenumber);


-- Merge all the addresses together
DROP TABLE IF EXISTS all_addresses;
SELECT *,(SELECT max(gid) FROM public_transport_stops) + row_number() over() as gid
INTO all_addresses FROM  
(SELECT * FROM entrances_derived_addresses 
UNION ALL 
SELECT * FROM directly_derived_addresses 
UNION ALL 
SELECT * FROM building_derived_addresses WHERE x not in(SELECT x FROM directly_derived_addresses)) as x;



CREATE INDEX index_all_addresses ON all_addresses USING GIST (geom);
ALTER TABLE all_addresses ADD PRIMARY KEY (id);
--Drop all not used tables AND index
DROP TABLE IF EXISTS house_address; 
DROP TABLE IF EXISTS x;
DROP TABLE IF EXISTS xx;























