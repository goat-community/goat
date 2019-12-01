DROP FUNCTION IF EXISTS closest_vertex;
CREATE OR REPLACE FUNCTION public.closest_vertex(userid_input integer,x NUMERIC,y NUMERIC, snap_distance NUMERIC, modus integer, routing_profile text)
 RETURNS SETOF text[]
 LANGUAGE plpgsql
AS $function$
DECLARE
	point geometry;
	geom_vertex geometry;
	excluded_class_id int[];
	id_vertex bigint;
	userid_vertex integer := 1;
	no_foot text[];
	no_wheelchair text[];
	no_safe_night text[];
BEGIN
	
	IF modus <> 1  THEN
		userid_vertex = userid_input;
	END IF;

	no_foot = select_from_variable_container('categories_no_foot');	
	excluded_class_id = select_from_variable_container('excluded_class_id_walking');	

	IF routing_profile = 'wheelchair' THEN 
		no_wheelchair = ARRAY['no'];
	END IF;

	IF routing_profile = 'safe_night' THEN 
		no_safe_night = ARRAY['no'];
	END IF;
-- input point
	point:= ST_SetSRID(ST_MakePoint(x,y), 4326);

  	SELECT w.id, w.geom 
  	INTO id_vertex, geom_vertex
  	FROM ways_userinput_vertices_pgr w
  	WHERE (userid IS NULL OR userid = userid_vertex)
  	AND (class_ids <@ excluded_class_id) IS FALSE
  	AND (foot <@ no_foot) IS FALSE
  	AND (wheelchair_classified <@ no_wheelchair) IS FALSE
  	AND (lit_classified <@ no_safe_night) IS FALSE
  	ORDER BY geom <-> point
  	LIMIT 1;
  	IF ST_Distance(geom_vertex,point)>snap_distance THEN
    	RETURN;
  	END IF;
	
  	RETURN query SELECT ARRAY[id_vertex::text, geom_vertex::text];
END ;
$function$;


SELECT * FROM variable_container

SELECT select_from_variable_container('categories_no_foot')

SELECT closest_vertex(1,11.5838,48.1926,0.0058,1,'standard')


SELECT select_from_variable_container('categories_no_foot')

SELECT * FROM ways


SELECT w.id, w.geom 
FROM ways_userinput_vertices_pgr w
WHERE (userid IS NULL OR userid = 1)
AND (class_ids <@ ARRAY[0,101,102,103,104,105,106,107,501,502,503,504,701,801]) IS FALSE
AND (foot <@ ARRAY['use_sidepath','no']) IS FALSE
AND (wheelchair_classified <@ ARRAY[]::text[]) IS FALSE
AND (lit_classified <@ ARRAY['no']) IS FALSE
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(11.5838,48.1926), 4326);


SELECT *,(foot <@ ARRAY['use_sidepath','no'])
FROM ways_userinput_vertices_pgr
WHERE (foot <@ ARRAY['use_sidepath','no']) IS FALSE
AND (wheelchair_classified <@ ARRAY['no']) IS FALSE
AND (class_ids <@ ARRAY[0,101,102,103,104,105,106,107,501,502,503,504,701,801]) IS FALSE


SELECT * FROM variable_container

SELECT array_remove(foot, null)
FROM ways_vertices_pgr


SELECT closest_vertex(1,11.5838,48.1926,0.0018,1,'wheelchair')