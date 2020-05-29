DROP FUNCTION IF EXISTS heatmap_dynamic_audience;
CREATE OR REPLACE FUNCTION public.heatmap_dynamic_audience(userid_input integer, impedance integer)
RETURNS TABLE(grid_id integer, original_audience_index INTEGER, delta_audience NUMERIC, audience_index NUMERIC, geom geometry)
LANGUAGE plpgsql
AS $function$

BEGIN
  	Return query
	WITH
	-- finds the deleted pois of a specific user from user_data table.
	-- Gets the amenity of the deleted point from pois_userinput.
	-- Finds the number of employees at the point from the variable container using the amenity.
	deleted_audience_points AS
	(
		SELECT gid, amenity, value::INTEGER * -1 AS employees, amenities.geom
		FROM jsonb_each(select_from_variable_container_o('poi_employees')) AS employees_per_amenity
		RIGHT JOIN
		(
			SELECT gid, amenity, pu.geom
			FROM user_data, pois_userinput pu 
			WHERE pu.gid = ANY(user_data.deleted_feature_ids ) AND user_data.userid = userid_input
		) as amenities
		ON amenities.amenity = employees_per_amenity.key
	),
	
	added_audience_points AS
	(
		SELECT id, amenity, employees, p.geom
		FROM pois_modified p
		WHERE userid = userid_input
	),
	
	modified_audience_points AS
	(
		SELECT * FROM deleted_audience_points
		UNION ALL
		SELECT * FROM added_audience_points
	),
	
	-- Makes a buffer around each deleted point.
	-- Gets the closest network node for the deleted point.
	-- The network node already has costs assigned to it how much it costs to reach the node from each cell.
	-- Takes the minimum cost if multiple nodes are inside the buffer.
	employees_and_cost_per_cell AS
	(
		SELECT rvh.grid_id, min(COST) AS cost, employees AS audience, map.gid
		FROM modified_audience_points map, reached_vertices_heatmap rvh 
		WHERE rvh.geom && ST_BUFFER(map.geom, 0.0009)
		GROUP BY rvh.grid_id, gid, employees
	),
	-- weights the audience according to cost and sums that up on each cell.
	-- this is how much lower the audience index is for each cell based on deleted user inputs!
	delta_audience_index AS
	(
		SELECT ecc.grid_id, sum(EXP(-(cost^2/impedance::NUMERIC))*audience) AS delta_audience
		FROM employees_and_cost_per_cell ecc
		GROUP BY ecc.grid_id
	)
	
	-- Joins the deltas in audience with the static audience index.
	SELECT s.grid_id, s.audience_index, coalesce(d.delta_audience, 0)::NUMERIC, (s.audience_index + coalesce(d.delta_audience, 0))::NUMERIC AS audience, s.geom
	FROM heatmap_static_audience(impedance) s
	LEFT JOIN delta_audience_index d ON s.grid_id = d.grid_id;
	
	
	

END;
$function$;


/*
SELECT * 
FROM heatmap_dynamic_audience(9775157, 150000)
*/