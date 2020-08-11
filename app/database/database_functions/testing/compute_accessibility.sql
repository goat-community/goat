EXPLAIN ANALYZE 
WITH p AS 
(
	SELECT p.amenity, p.name, p.geom, e.edge, e.fraction, e.start_cost, e.end_cost
	FROM pois_userinput p
	CROSS JOIN LATERAL
	(
		SELECT f.edge, ST_LineLocatePoint(f.geom,p.geom) AS fraction, f.start_cost, f.end_cost 
		FROM reached_full_heatmap f
		WHERE f.geom && ST_Buffer(p.geom,0.0018)
		ORDER BY ST_CLOSESTPOINT(f.geom,p.geom) <-> p.geom
		LIMIT 1
	) AS e
	WHERE p.amenity IN (SELECT UNNEST(select_from_variable_container('pois_one_entrance')))
)
SELECT p.*, c.*
FROM p, compute_accessibility_index(fraction,start_cost,end_cost,ARRAY[200000, 250000, 300000, 350000, 400000, 450000]) c



CREATE OR REPLACE FUNCTION public.compute_accessibility_index(fraction float, arr_start_cost smallint[], arr_end_cost smallint[], sensitivities integer[])
RETURNS TABLE (arr_true_cost smallint[], accessibility_indices smallint[][]) 
AS $function$
DECLARE 
	cnt smallint := 0;
	start_cost smallint;
	end_cost smallint;
	true_cost smallint;
	arr_true_cost smallint[] := ARRAY[]::smallint[];
	sensitivity integer;
	accessibility_indices_helper SMALLINT[];
	accessibility_indices SMALLINT[][];
BEGIN 

	FOREACH start_cost IN ARRAY arr_start_cost
  	LOOP
  		cnt = cnt + 1;
  		end_cost = arr_end_cost[cnt];
  		IF start_cost < end_cost THEN
  			true_cost = (start_cost + (fraction * (end_cost-start_cost)))::smallint;
  		ELSE 
  			true_cost = (end_cost + ((1-fraction) * (start_cost - end_cost)))::smallint;
  		END IF;
  	
  		accessibility_indices_helper = ARRAY[]::float[];
		FOREACH sensitivity IN ARRAY sensitivities
		LOOP 
			accessibility_indices_helper = accessibility_indices_helper || ((EXP(-(true_cost^2)/sensitivity)::float) * 10000)::smallint; 
		END LOOP;
		accessibility_indices = accessibility_indices || ARRAY[accessibility_indices_helper];
		arr_true_cost = arr_true_cost | true_cost;
  	END LOOP;
  	
	RETURN query SELECT arr_true_cost, accessibility_indices; 
END;
$function$ LANGUAGE plpgsql immutable;
--SELECT * FROM compute_accessibility_index(0.3, ARRAY[100,200,300,400,500,600,700]::SMALLINT[], ARRAY[300,400,500,700,800,1000,1300]::SMALLINT[], ARRAY[200000,250000, 300000, 350000, 400000, 450000])
