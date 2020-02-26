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
	v_death_end BOOLEAN;
BEGIN
	
	IF modus <> 1  THEN
		userid_vertex = userid_input;
	END IF;

	no_foot = select_from_variable_container('categories_no_foot');	
	excluded_class_id = select_from_variable_container('excluded_class_id_walking')::int[];	

	IF routing_profile = 'walking_wheelchair' THEN 
		no_wheelchair = ARRAY['no'];
	ELSE 
		no_wheelchair = ARRAY[]::text[];
	END IF;

	IF routing_profile = 'walking_safe_night' THEN 
		no_safe_night = ARRAY['no'];
	ELSE 
		no_safe_night = ARRAY[]::text[];
	END IF;
-- input point
	point:= ST_SetSRID(ST_MakePoint(x,y), 4326);

	raise notice '%', ST_AsText(point);
	raise notice '%', no_foot;
	raise notice '%', no_safe_night;
	raise notice '%', no_wheelchair;


  	SELECT w.id, w.geom,death_end 
  	INTO id_vertex, geom_vertex, v_death_end
	FROM ways_userinput_vertices_pgr w
	WHERE (userid IS NULL OR userid = userid_vertex)
	AND (class_ids <@ excluded_class_id) IS FALSE
	AND ((foot <@ no_foot) IS FALSE OR foot = ARRAY[]::text[])
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

/*SELECT * FROM public.closest_vertex(1 ,11.5669,48.1546, 50, 1, 'walking_standard');
*/