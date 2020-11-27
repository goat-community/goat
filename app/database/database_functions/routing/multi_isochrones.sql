DROP FUNCTION IF EXISTS multi_isochrones;
CREATE OR REPLACE FUNCTION public.multi_isochrones(userid_input integer, scenario_id_input integer, objectid_input integer, minutes integer, number_isochrones integer, routing_profile_input text, speed_input numeric, 
    alphashape_parameter_input NUMERIC, modus_input integer, parent_id_input integer, points_array NUMERIC[][])
    RETURNS void
    AS $function$
DECLARE
    vid integer; 
   	cutoff integer;
    counter integer := 1;
   	cutoffs float[];
   	step_isochrone numeric = (minutes*60)/number_isochrones;
BEGIN

	speed_input = speed_input/3.6;	

	SELECT array_agg(x.border) 
	INTO cutoffs
	FROM (SELECT generate_series(step_isochrone,(minutes*60),step_isochrone)::float border) x; 

  
	PERFORM pgrouting_edges_multi(cutoffs,points_array,speed_input,modus_input,routing_profile_input,userid_input,scenario_id_input);
   
	DROP TABLE IF EXISTS isos;
	CREATE TEMP TABLE isos(from_v integer, step integer, geom geometry);
	DROP TABLE IF EXISTS iso_vertices;
	CREATE TEMP TABLE iso_vertices(geom geometry);

	PERFORM plv8_require();
	FOR vid IN SELECT s.vid FROM start_vertices s	
	LOOP
		FOR cutoff IN SELECT unnest(cutoffs)
		LOOP
		counter = counter + 1;
		IF (SELECT count(*) FROM multi_edges WHERE from_v = vid AND cost BETWEEN 0 AND cutoff LIMIT 4) > 3 THEN 
			TRUNCATE iso_vertices;
			INSERT INTO iso_vertices 
			SELECT CASE WHEN start_cost > end_cost THEN st_startpoint(geom) ELSE st_endpoint(geom) END AS geom
			FROM multi_edges
			WHERE COST <= cutoff
			AND from_v = vid; 
			
		  	INSERT INTO isos 
		  	SELECT vid AS from_v, cutoff/60, ST_SETSRID(st_geomfromtext('POLYGON(('||REPLACE(plv8_concaveman(),',4',' 4')||'))'),4326) AS geom;
		  	
		END IF;
		END LOOP;  
    END LOOP;
	
    INSERT INTO multi_isochrones (objectid, coordinates, userid, step, speed, alphashape_parameter, modus, parent_id, routing_profile, geom)
    SELECT objectid_input,points_array AS coordinates,userid_input,step,speed_input,
    alphashape_parameter_input,modus_input,parent_id_input, routing_profile_input as routing_profile,ST_Union(geom) AS geom
    FROM isos
    GROUP BY step;
	
END;
$function$
LANGUAGE plpgsql;

/*
SELECT multi_isochrones(1,1,10,2,'walking_standard',15,0.00003,1,1,ARRAY[[11.2493, 48.1804],[11.2315,48.1778]])
*/