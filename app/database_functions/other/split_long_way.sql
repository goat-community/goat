CREATE OR REPLACE FUNCTION public.split_long_way(geom geometry, length_m NUMERIC, max_length integer)
RETURNS SETOF geometry
AS $function$
DECLARE 
	fraction NUMERIC;
	end_border NUMERIC :=0;
	start_border NUMERIC;
BEGIN 
	fraction = 1/ceil(length_m/max_length);
	WHILE end_border < 1 LOOP 
		start_border = round(end_border,5);
		end_border = round(end_border+fraction,5);
		IF end_border > 1 THEN 
			end_border = 1;
		END IF;
		RETURN NEXT st_line_substring(geom,start_border,end_border);
	END LOOP; 
	
END;
$function$ LANGUAGE plpgsql immutable;