CREATE OR REPLACE FUNCTION basic.get_aoi_area_sum(user_id_input integer, modus text, extent geometry, pixel_resolution integer, 
scenario_id_input integer DEFAULT 0, active_upload_ids integer[] DEFAULT '{}'::integer[])
 RETURNS SETOF VOID --TABLE(pixel int[], category text, cnt integer)
 LANGUAGE plpgsql
AS $function$
DECLARE 

BEGIN 		

	DROP TABLE temporal.test 
	
	CREATE TABLE temporal.test AS 

		WITH selected_aoi AS 
		(
			SELECT ST_AREA(
				st_makeenvelope(
					ST_X(centroid), ST_Y(centroid),
					ST_X(centroid) + 0.0007, ST_Y(centroid) + 0.0007
				)::geography 
			)::integer AS area, geom   
			FROM basic.aoi a, LATERAL ST_CENTROID(geom) AS centroid 
			WHERE ST_Intersects(a.geom, ST_SETSRID(ST_BUFFER(ST_MAKEPOINT(11.57616, 48.13168)::geography, 15000)::geometry, 4326))
			
		)
		SELECT area, basic.coordinate_to_pixel(ST_X(ST_Centroid(g.geom)), ST_Y(ST_Centroid(g.geom)), 12), g.geom
		FROM selected_aoi,
		LATERAL ST_SquareGrid(0.0007, geom) g; 
		   
	SELECT * FROM temporal.test 
	
	
END;
$function$;


SELECT * 
FROM basic.get_aoi_area_sum(15, 'default'::text, ST_SETSRID(ST_BUFFER(ST_MAKEPOINT(11.57616, 48.13168)::geography, 200000)::geometry, 4326), 12)



