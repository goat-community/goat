

DROP TABLE test;

CREATE TABLE test AS 
WITH x AS (
SELECT st_startpoint(geom) geom, cost
FROM edges
UNION ALL
SELECT st_endpoint(geom) geom, cost
FROM edges
)
SELECT min(cost), geom
FROM x
GROUP BY geom

SELECT * FROM edges

DELETE FROM isochrones


CREATE OR REPLACE FUNCTION public.thematic_data_json(input_gid integer)
 RETURNS TABLE(gid_isochrone integer, pois_isochrones text)
 LANGUAGE plpgsql
AS $function$
begin
	

	
	--Pois AND public transport stops are combined AND all which are intersecting with the isochrones
	--are SELECTed.
with var_poi as (
		SELECT i.gid,i.step, p.gid as poi_gid,p.amenity,p.name, p.geom  
		FROM pois p,isochrones i,variable_container v 
		WHERE v.identifier = 'poi_categories'
		AND amenity = any(variable_array)
		AND i.gid= input_gid
		AND st_intersects(p.geom,i.geom)
		UNION ALL
		SELECT i.gid,i.step,p.gid as poi_gid,public_transport_stop,p.name,p.geom
		FROM public_transport_stops p, isochrones i
		WHERE i.gid= input_gid
		AND st_intersects(p.geom,i.geom)
		
	)	
	
	--The distance FROM each POI/transport stop to a calculated vertex FROM the edges table
	--is calculated AND the cost is passed is saved.
	--!!!!The SELECTion of the nearest vertex has to be improved!!!!
	,vertices_edges(
		SELECT min(cost), geom
		FROM (SELECT st_startpoint(geom) geom, cost
			  FROM edges
			  WHERE objectid= (SELECT distinct objectid FROM isochrones WHERE gid = input_gid)
			  UNION ALL
			  SELECT st_endpoint(geom) geom, cost
			  FROM edges
			  WHERE objectid= (SELECT distinct objectid FROM isochrones WHERE gid = input_gid)
			) x
		GROUP BY geom
	)
	,min_dist as (
		SELECT  poi_gid,name,amenity,st_distance(x.geom,v.geom) as min_dist,x.geom, v.geom 
		FROM  vertices_edges v, var_poi x
		WHERE St_dwithin(v.geom::geography,x.geom::geography,50,true)
	)
	
	,min_dist1 as (
		SELECT * FROM min_dist 
		WHERE min_dist <> 0
		AND min_dist in(
		SELECT min(min_dist) FROM min_dist GROUP BY poi_gid)
	)	
		
	--The pois are saved as jsonb AND saved at the isochrones table	
	,costs_pois as (
		SELECT amenity,name,cost FROM min_dist1 m
		WHERE 
	
	)
	UPDATE isochrones set pois = z.array_to_json::text
	FROM (
	SELECT input_gid,array_to_json(array_agg(row_to_json(x))) FROM(
	SELECT amenity,name,min(cost) as cost FROM test_pois --Every entrance OR bus_stop is only counted once (shortest distance is taken)
	WHERE amenity in('subway_entrance','bus_stop','tram_stop','sbahn_regional') 
	GROUP BY amenity,name
	UNION ALL
	SELECT amenity,name,cost FROM test_pois
	WHERE amenity not in('subway_entrance','bus_stop','tram_stop','sbahn_regional'))x) z 
	WHERE isochrones.gid = z.input_gid;

	return query SELECT i.gid, i.pois FROM isochrones i WHERE gid= input_gid;
END ;
$function$
