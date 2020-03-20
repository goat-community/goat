DROP FUNCTION IF EXISTS thematic_data_json;
CREATE OR REPLACE FUNCTION public.thematic_data_json(input_gid integer)
 RETURNS TABLE(gid_isochrone integer, pois_isochrones text)
 LANGUAGE plpgsql
AS $function$
Declare 
distinct_objectid integer;
begin
	
	--The distance FROM each POI/transport stop to a calculated vertex FROM the edges table
	--is calculated AND the cost is passed and saved.
	SELECT DISTINCT objectid 
	INTO distinct_objectid 
	FROM isochrones 
	WHERE gid = input_gid;

	DROP TABLE IF EXISTS vertices_edges;
	CREATE TEMP TABLE  vertices_edges AS 
	SELECT min(cost) AS cost, geom
	FROM (SELECT st_startpoint(geom) geom, cost
		  FROM edges
		  WHERE objectid= distinct_objectid
		  UNION ALL
		  SELECT st_endpoint(geom) geom, cost
		  FROM edges
		  WHERE objectid= distinct_objectid
		  UNION ALL 
		  SELECT geom,1 AS cost 
		  FROM starting_point_isochrones 
		  WHERE objectid = distinct_objectid
		) x
	GROUP BY geom;
	ALTER TABLE vertices_edges ADD COLUMN gid serial;
	ALTER TABLE vertices_edges ADD PRIMARY key(gid);
	CREATE INDEX ON vertices_edges USING gist(geom);

	DROP TABLE IF EXISTS pois_and_pt;
	CREATE temp TABLE pois_and_pt AS 
	SELECT i.gid,i.step, p.gid as poi_gid,p.amenity,p.name, p.geom  
	FROM pois p,isochrones i,variable_container v 
	WHERE v.identifier = 'poi_categories'
	AND amenity = any(variable_array)
	AND i.gid= input_gid
	AND st_intersects(p.geom,i.geom)
	UNION ALL 
	SELECT i.gid,i.step,p.gid as poi_gid,public_transport_stop AS amenity,p.name,p.geom
	FROM public_transport_stops p, isochrones i
	WHERE i.gid= input_gid
	AND st_intersects(p.geom,i.geom);
	ALTER TABLE pois_and_pt ADD PRIMARY key(poi_gid);
	CREATE INDEX ON pois_and_pt USING gist(geom);
	--!!!!The Selection of the nearest vertex has to be improved!!!!
	WITH distance_pois as (
		SELECT  DISTINCT on(x.poi_gid) x.poi_gid,name,amenity,st_distance(x.geom,v.geom) as min_dist, v.cost, x.geom 
		FROM  vertices_edges v, pois_and_pt x
		WHERE v.geom && ST_Buffer(x.geom::geography,100)::geometry
		ORDER BY x.poi_gid, st_distance(x.geom,v.geom)

	)
	UPDATE isochrones set pois = z.array_to_json::text
	FROM (
	SELECT input_gid,array_to_json(array_agg(row_to_json(x))) 
		FROM(
			SELECT amenity,name,min(cost) as cost FROM distance_pois --Every entrance OR bus_stop is only counted once (shortest distance is taken)
			WHERE amenity in('subway_entrance','bus_stop','tram_stop','sbahn_regional') 
			GROUP BY amenity,name
			UNION ALL
			SELECT amenity,name,cost FROM distance_pois
			WHERE amenity not in('subway_entrance','bus_stop','tram_stop','sbahn_regional')
			)x
		) z 
	WHERE isochrones.gid = z.input_gid;

	return query SELECT i.gid, i.pois FROM isochrones i WHERE gid= input_gid;
END ;
$function$
