DROP FUNCTION IF EXISTS split_long_way;
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
		RETURN NEXT st_linesubstring(geom,start_border,end_border);
	END LOOP; 
	
END;
$function$ LANGUAGE plpgsql immutable;

DROP FUNCTION IF EXISTS split_long_way_to_array;
CREATE OR REPLACE FUNCTION public.split_long_way_to_array(geom geometry, length_m numeric, max_length integer)
 RETURNS geometry[]
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
DECLARE 
	fraction NUMERIC;
	end_border NUMERIC :=0;
	start_border NUMERIC;
	retval geometry[] = array[]::geometry[];
BEGIN 
	fraction = 1/ceil(length_m/max_length);
	WHILE end_border < 1 LOOP 
		start_border = round(end_border,5);
		end_border = round(end_border+fraction,5);
		retval = array_append(retval,ST_LineInterpolatePoint(geom, start_border)); 
		IF end_border >= 1 THEN 
			end_border = 1;
			retval = array_append(retval,ST_EndPoint(geom));
			exit;
		END IF;
		
	END LOOP; 
	RETURN retval;
	
END;
$function$