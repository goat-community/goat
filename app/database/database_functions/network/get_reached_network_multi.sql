DROP FUNCTION IF EXISTS get_reached_network_multi;
CREATE OR REPLACE FUNCTION public.get_reached_network_multi(ids_calc integer[],max_cost NUMERIC, number_isochrones integer, edges_to_exclude bigint[],objectid_input integer)
RETURNS void AS
$$
DECLARE
	border_cost NUMERIC;
	ids_calc_text text[] := ids_calc::text[]; 
	id_calc_text text;
	step_isochrone NUMERIC := max_cost/number_isochrones;
BEGIN
	INSERT INTO edges_multi
	SELECT * 
	FROM 
	(
		SELECT w.id,s.node,CASE WHEN s.min_cost > f.min_cost THEN s.min_cost ELSE f.min_cost END AS min_cost,
		w.geom,s.geom AS v_geom,objectid_input,
		CASE WHEN f.ids_calc <> s.ids_calc THEN f.node_cost - 
		(	
			CASE WHEN array_length(f.ids_calc,1) < array_length(s.ids_calc,1) THEN (s.ids_calc - f.ids_calc)::text[] 
			WHEN array_length(f.ids_calc,1) > array_length(s.ids_calc,1) THEN (f.ids_calc - s.ids_calc)::text[]
			ELSE ((s.ids_calc || f.ids_calc) - (s.ids_calc & f.ids_calc))::text[] END
		) 
		ELSE f.node_cost END AS node_cost_1,
		CASE WHEN f.ids_calc <> s.ids_calc THEN s.node_cost - 
		(	
			CASE WHEN array_length(f.ids_calc,1) < array_length(s.ids_calc,1) THEN (s.ids_calc - f.ids_calc)::text[] 
			WHEN array_length(f.ids_calc,1) > array_length(s.ids_calc,1) THEN (f.ids_calc - s.ids_calc)::text[]
			ELSE ((s.ids_calc || f.ids_calc) - (s.ids_calc & f.ids_calc))::text[] END
		)
		ELSE s.node_cost END AS node_cost_2
		FROM temp_reached_vertices f, temp_reached_vertices s, temp_fetched_ways w 
		WHERE f.node = w.source 
		AND s.node = w.target
	) e
	WHERE e.node_cost_1 <> '{}'::jsonb  AND e.node_cost_2 <> '{}'::jsonb;

	FOREACH id_calc_text IN ARRAY ids_calc_text	
	LOOP
		FOR border_cost IN SELECT generate_series(step_isochrone,max_cost,step_isochrone)
		LOOP
			
			INSERT INTO edges_multi_extrapolated
			SELECT x.id AS edge, x.node, border_cost AS cost,
			ST_LINESUBSTRING(x.geom,1-((border_cost-agg_cost)/x.cost),1) AS geom,
			ST_STARTPOINT(ST_LINESUBSTRING(x.geom,1-((border_cost-agg_cost)/x.cost),1)) AS v_geom, id_calc_text::integer,objectid_input 
			FROM 
			(
				SELECT w.id, v.node, (v.node_cost ->> id_calc_text)::NUMERIC AS agg_cost, w.cost, w.geom
				FROM temp_reached_vertices v, temp_fetched_ways w
				WHERE v.node = w.target
				AND w.death_end IS NULL 
				AND (v.node_cost ->> id_calc_text)::NUMERIC < border_cost
				AND (v.node_cost ->> id_calc_text) IS NOT NULL  
			) x
			LEFT JOIN 
			(	SELECT * FROM edges_multi e 
				WHERE greatest((node_cost_1 ->> id_calc_text)::NUMERIC,(node_cost_2 ->> id_calc_text)::NUMERIC)::NUMERIC < border_cost 
				AND greatest((node_cost_1 ->> id_calc_text)::NUMERIC,(node_cost_2 ->> id_calc_text)::NUMERIC) IS NOT NULL
			) e
			ON x.id = e.edge 
			WHERE e.edge IS NULL
			AND x.id NOT IN(SELECT UNNEST(edges_to_exclude))
			UNION ALL 
			SELECT x.id AS edge, x.node, border_cost AS cost,
			ST_LINESUBSTRING(x.geom,0,1-((border_cost-agg_cost)/x.cost)) AS geom,
			ST_STARTPOINT(ST_LINESUBSTRING(x.geom,0,1-((border_cost-agg_cost)/x.cost))) AS v_geom, id_calc_text::integer,objectid_input
			FROM 
			(
				SELECT w.id, v.node, (v.node_cost ->> id_calc_text)::NUMERIC AS agg_cost, w.cost, w.geom
				FROM temp_reached_vertices v, temp_fetched_ways w
				WHERE v.node = w.source
				AND w.death_end IS NULL 
				AND (v.node_cost ->> id_calc_text)::NUMERIC < border_cost
				AND (v.node_cost ->> id_calc_text) IS NOT NULL  
			) x
			LEFT JOIN 
			(	SELECT * FROM edges_multi e 
				WHERE greatest((node_cost_1 ->> id_calc_text)::NUMERIC,(node_cost_2 ->> id_calc_text)::NUMERIC)::NUMERIC < border_cost 
				AND greatest((node_cost_1 ->> id_calc_text)::NUMERIC,(node_cost_2 ->> id_calc_text)::NUMERIC) IS NOT NULL
			) e
			ON x.id = e.edge 
			WHERE e.edge IS NULL
			AND x.id NOT IN(SELECT UNNEST(edges_to_exclude));
		END LOOP;
	END LOOP;
	

	INSERT INTO edges_multi	
	SELECT w.id AS edge,v.node, v.min_cost, w.geom,
	CASE WHEN w.source = v.node THEN ST_ENDPOINT(w.geom) ELSE ST_STARTPOINT(w.geom) END AS v_geom, objectid_input,
	CASE WHEN w.SOURCE = v.node THEN add_value_to_object(node_cost,w.cost,max_cost) 
	ELSE add_value_to_object(node_cost,w.reverse_cost,max_cost)  END AS node_cost_1, NULL 
	FROM temp_reached_vertices v, temp_fetched_ways w 
	WHERE v.death_end = TRUE 
	AND v.node = w.death_end;
	
END;
$$ LANGUAGE plpgsql;



