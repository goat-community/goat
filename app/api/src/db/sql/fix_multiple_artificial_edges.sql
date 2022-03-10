CREATE OR REPLACE FUNCTION basic.fix_multiple_artificial_edges(wid integer, s integer, t integer, c float, rc float, w_geom geometry, vids integer[],fractions float[])
 RETURNS TABLE (edge_id integer, COST float, reverse_cost float, SOURCE integer, target integer, geom geometry)
 LANGUAGE plpgsql
AS $function$
DECLARE 
	start_fraction float := 0;
	source_id integer := s;
	end_fraction float;
	start_id integer := s;
	cnt integer := 1;
BEGIN 
	fractions = array_append(fractions,1::float);
	vids = array_append(vids,t);

	FOREACH end_fraction IN ARRAY fractions
	LOOP 
		RETURN query
		WITH parts AS 
		(
			SELECT wid, c*(end_fraction-start_fraction) AS cost,rc*(end_fraction-start_fraction) AS reverse_cost, 
			source_id AS source, vids[cnt] AS target, ST_LINESUBSTRING(w_geom,start_fraction,end_fraction) AS geom
		)
		SELECT p.wid, p.cost, p.reverse_cost, p.source, p.target, p.geom
		FROM parts p
		WHERE p.cost <> 0;  

		start_fraction = end_fraction;
		source_id = vids[cnt];
		edge_id = edge_id - 1;
		cnt = cnt + 1;
	END LOOP;
	RETURN; 
END 
$function$;
