CREATE OR REPLACE FUNCTION select_reached_edges(id_calc integer,objectid_input integer,calc_step numeric) 
RETURNS SETOF geometry 
LANGUAGE plpgsql
AS $function$
DECLARE 
	id_calc_text text := id_calc::text;
	sql_select text;
BEGIN 
	
	RETURN query
    SELECT v_geom
    FROM edges_multi_extrapolated
    WHERE objectid = objectid_input
    AND cost = calc_step
    UNION ALL
    SELECT v_geom
    FROM edges_multi
    WHERE objectid = objectid_input AND 
    ((node_cost_1 -> id_calc_text) IS NOT NULL OR (node_cost_2 -> id_calc_text) IS NOT NULL)
    AND greatest(COALESCE((node_cost_1 -> id_calc_text)::float,0),
    COALESCE((node_cost_1 -> id_calc_text)::float,0)) < calc_step;

END;
$function$;