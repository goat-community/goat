DROP FUNCTION IF EXISTS interpolate_cost;
CREATE OR REPLACE FUNCTION public.interpolate_cost(fraction float, arr_start_cost smallint[], arr_end_cost smallint[])
RETURNS TABLE (arr_true_cost smallint[]) 
AS $function$
DECLARE 
	cnt smallint := 0;
	start_cost smallint;
	end_cost smallint;
	true_cost smallint;
	_true_cost smallint;
	arr_true_cost smallint[] := ARRAY[]::smallint[];
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
  	  
	RETURN query SELECT arr_true_cost; 
END;
$function$ LANGUAGE plpgsql IMMUTABLE;

--SELECT * FROM interpolate_cost(0.5, ARRAY[100,200,300]::SMALLINT[], ARRAY[200,300,400]::SMALLINT[]);
