CREATE OR REPLACE FUNCTION public.multiple_artificial_edges(wid integer, s integer, t integer, c float, rc float, w_geom geometry, vids bigint[],fractions float[])
 RETURNS SETOF void
 LANGUAGE plpgsql
AS $function$
DECLARE 
	start_fraction float := 0;
	source_id integer := s;
	end_fraction float;
	start_id integer := s;
	cnt integer := 1;
	edge_id integer := (SELECT min(id)-1 FROM artificial_edges);
BEGIN 
	fractions = array_append(fractions,1::float);
	vids = array_append(vids,t::bigint);
	

	FOREACH end_fraction IN ARRAY fractions
	LOOP 
		INSERT INTO artificial_edges 
		SELECT wid, edge_id, c*(end_fraction-start_fraction),rc*(end_fraction-start_fraction), 
		source_id, vids[cnt], ST_LINESUBSTRING(w_geom,start_fraction,end_fraction);
		
		start_fraction = end_fraction;
		source_id = vids[cnt];
		edge_id = edge_id - 1;
		cnt = cnt + 1;
	END LOOP;
END 
$function$;
