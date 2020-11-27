DROP FUNCTION IF EXISTS compute_accessibility_index;
CREATE OR REPLACE FUNCTION public.compute_accessibility_index(fraction float, arr_start_cost smallint[], arr_end_cost smallint[], sensitivities integer[])
RETURNS TABLE (arr_true_cost smallint[], accessibility_indices smallint[][]) 
AS $function$
DECLARE 
	cnt smallint := 0;
	start_cost smallint;
	end_cost smallint;
	true_cost smallint;
	_true_cost smallint;
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
		arr_true_cost = arr_true_cost || true_cost;
  	END LOOP;
  	  
	FOREACH sensitivity IN ARRAY sensitivities
	LOOP 
		accessibility_indices_helper = ARRAY[]::float[];
		FOREACH _true_cost IN ARRAY arr_true_cost 
  		LOOP
			accessibility_indices_helper = accessibility_indices_helper || ((EXP(-(_true_cost^2)/sensitivity)::float) * 10000)::smallint; 
		END LOOP;
		accessibility_indices = accessibility_indices || ARRAY[accessibility_indices_helper];
  	END LOOP;
  
	RETURN query SELECT arr_true_cost, accessibility_indices; 
END;
$function$ LANGUAGE plpgsql IMMUTABLE;

--SELECT * FROM compute_accessibility_index(0.5, ARRAY[100,200,300]::SMALLINT[], ARRAY[200,300,400]::SMALLINT[], ARRAY[250000,300000,350000])
