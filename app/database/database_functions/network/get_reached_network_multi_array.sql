DROP FUNCTION IF EXISTS get_reached_network_multi_array;
CREATE OR REPLACE FUNCTION public.get_reached_network_multi_array(ids_calc_input integer[],max_cost NUMERIC, number_isochrones integer, edges_to_exclude bigint[],objectid_input integer)
RETURNS void AS
$$
DECLARE
	border_cost NUMERIC;
	step_isochrone NUMERIC := max_cost/number_isochrones;
	id_calc integer;
BEGIN
	INSERT INTO edges_multi
	SELECT w.id,s.node,CASE WHEN s.min_cost > f.min_cost THEN s.min_cost ELSE f.min_cost END AS min_cost,
	w.geom,s.geom AS v_geom,objectid_input objectid, f.ids_calc|s.ids_calc duplicates, f.ids_calc || s.ids_calc combi_ids, 
	f.costs || s.costs combi_costs
	FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
	WHERE f.node = w.source 
	AND s.node = w.target
	AND w.death_end IS NULL; 


	FOREACH id_calc IN ARRAY ids_calc_input	
	LOOP
		FOR border_cost IN SELECT generate_series(step_isochrone,max_cost,step_isochrone)
		LOOP
			
			INSERT INTO edges_multi_extrapolated
			SELECT x.id AS edge, x.node, border_cost AS cost, ST_LINESUBSTRING(x.geom,1-((border_cost-agg_cost)/x.cost),1) AS geom,
			ST_STARTPOINT(ST_LINESUBSTRING(x.geom,1-((border_cost-agg_cost)/x.cost),1)) AS v_geom, 
			id_calc, objectid_input
			FROM 
			(
				SELECT w.id, v.node, costs[array_position(ids_calc,id_calc)] AS agg_cost, w.cost, w.geom
				FROM temp_reached_vertices v, temp_fetched_ways w
				WHERE v.node = w.target
				AND w.death_end IS NULL 
				AND costs[array_position(ids_calc,id_calc)]  < border_cost
				AND costs[array_position(ids_calc,id_calc)]  IS NOT NULL 
			) x
			LEFT JOIN 
			(	
				SELECT edge
				FROM 
				(	
					SELECT e.edge,array_positions(combi_ids,id_calc) AS positions,combi_costs,e.geom  
					FROM edges_multi e
					WHERE objectid = objectid_input
				) p
				WHERE p.positions <> array[]::integer[] 
				AND p.positions[1] IS NOT NULL 
				AND p.positions[2] IS NOT NULL
				AND greatest(combi_costs[p.positions[1]],combi_costs[p.positions[2]]) < border_cost
			) e
			ON x.id = e.edge 
			WHERE e.edge IS NULL
			AND x.id NOT IN(SELECT UNNEST(edges_to_exclude))
			UNION ALL 
			SELECT x.id AS edge, x.node, border_cost AS cost,ST_LINESUBSTRING(x.geom,0,1-((max_cost-agg_cost)/x.cost)) AS geom,
			ST_STARTPOINT(ST_LINESUBSTRING(x.geom,0,1-((border_cost-agg_cost)/x.cost))) AS v_geom, id_calc, objectid_input
			FROM 
			(
				SELECT w.id, v.node, costs[array_position(ids_calc,id_calc)] AS agg_cost, w.cost, w.geom
				FROM temp_reached_vertices v, temp_fetched_ways w
				WHERE v.node = w.source
				AND w.death_end IS NULL 
				AND costs[array_position(ids_calc,id_calc)]  < border_cost
				AND costs[array_position(ids_calc,id_calc)]  IS NOT NULL 
			) x
			LEFT JOIN 
			(	
				SELECT edge
				FROM 
				(	
					SELECT e.edge,array_positions(combi_ids,id_calc) AS positions,combi_costs,e.geom  
					FROM edges_multi e
					WHERE objectid = objectid_input
				) p
				WHERE p.positions <> array[]::integer[] 
				AND p.positions[1] IS NOT NULL 
				AND p.positions[2] IS NOT NULL
				AND greatest(combi_costs[p.positions[1]],combi_costs[p.positions[2]]) < max_cost
			) e
			ON x.id = e.edge 
			WHERE e.edge IS NULL
			AND x.id NOT IN(SELECT UNNEST(edges_to_exclude));

		END LOOP;
	END LOOP;

	INSERT INTO edges_multi
	SELECT w.id AS edge,v.node, v.min_cost, w.geom,
	CASE WHEN w.source = v.node THEN ST_ENDPOINT(w.geom) ELSE ST_STARTPOINT(w.geom) END AS v_geom, 1 AS objectid,
	CASE WHEN w.SOURCE = v.node THEN add_value_to_array(v.costs,w.cost,max_cost) 
	ELSE add_value_to_array(v.costs,w.reverse_cost,max_cost) END AS costs, NULL 
	FROM temp_reached_vertices v, temp_fetched_ways w 
	WHERE v.death_end = TRUE 
	AND v.node = w.death_end;

	
END;
$$ LANGUAGE plpgsql; 	

--SELECT get_reached_network_multi_array(ARRAY[1,2,3,4],1200,1,ARRAY[999999998,999999997,999999996,999999995,999999994,999999993,999999992,999999991],1);
