CREATE OR REPLACE FUNCTION public.pgrouting_edges_input(minutes integer, x numeric, y numeric, speed numeric, userid_input integer, objectid_input integer, modus integer)
 RETURNS SETOF type_catchment_vertices
 LANGUAGE plpgsql
AS $function$
	DECLARE
	point geometry;
	r type_edges;
	distance numeric;
	id_vertex integer;
	geom_vertex geometry;
	excluded_class_id text;
	excluded_ways_id text;
	userid_vertex integer;
	number_calculation_input integer;
	categories_no_foot text;
	begin
	--The speed AND minutes input are considered as distance
	distance=speed*minutes;
	userid_vertex = userid_input;
	-- input point
	point:= ST_SetSRID(ST_MakePoint(x,y), 4326);
	IF modus = 3  THEN
	userid_vertex = 1;
	userid_input = 1;

	ELSEIF modus = 4 THEN  	 
	userid_vertex = 1;
	END IF;

	SELECT select_from_variable_container('excluded_class_id_walking'),
	select_from_variable_container('categories_no_foot')
	INTO excluded_class_id, categories_no_foot;

	SELECT array_append(array_agg(id),0::bigint)::text INTO excluded_ways_id FROM (
	SELECT Unnest(deleted_feature_ids) id FROM user_data
	WHERE id = userid_input
	UNION ALL
	SELECT original_id modified
	FROM ways_modified 
	WHERE userid = userid_input AND original_id IS NOT null
	) x;

	SELECT id, geom INTO id_vertex, geom_vertex
	FROM ways_userinput_vertices_pgr
	WHERE userid is null or userid = userid_vertex
	AND (class_ids <@ excluded_class_id::int[]) IS false
	ORDER BY geom <-> point
	LIMIT 1;
	IF ST_Distance(geom_vertex::geography,point::geography)>250 THEN
	RETURN;
	END IF;
	IF modus <> 3 THEN 
		SELECT count(objectid) + 1 INTO number_calculation_input
		FROM starting_point_isochrones
		WHERE userid = userid_input; 
		INSERT INTO starting_point_isochrones(userid,geom,objectid,number_calculation)
		SELECT userid_input, v.geom, objectid_input, number_calculation_input
		FROM ways_userinput_vertices_pgr v
		WHERE v.id = id_vertex;
	END IF; 

	RETURN query 
	--In this case the routing is done on a modified table
	SELECT id_vertex, p.id1::integer AS node, p.id2::integer AS edge, p.cost::numeric, v.geom, objectid_input 
	FROM PGR_DrivingDistance(
		'SELECT id::int4, source, target, length_m as cost FROM ways_userinput 
		WHERE not class_id = any(''' || excluded_class_id || ''')   			
		AND geom && ST_Buffer('''||point::text||'''::geography,'||distance||')::geometry
		AND not id::int4 = any('''|| excluded_ways_id ||''') 
		AND (NOT foot = any('''||categories_no_foot||''') OR foot IS NULL)
		AND userid IS NULL OR userid='||userid_input,
		id_vertex, 
		distance, false, false
	) p, ways_userinput_vertices_pgr v
	WHERE p.id1 = v.id;
	RETURN;
	END ;
$function$