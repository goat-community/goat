
DROP FUNCTION IF EXISTS slope_impedance;
CREATE OR REPLACE FUNCTION public.slope_impedance(slope numeric)
 RETURNS SETOF numeric[]
 LANGUAGE plpgsql
AS $function$
DECLARE
    impedances NUMERIC[];
   	r_slope numeric := -slope;
	i NUMERIC;
	imp NUMERIC;
BEGIN 
    
    FOREACH i in ARRAY ARRAY[slope,r_slope]
    LOOP
        IF i > 9 THEN 
        	imp = 0;
        ELSEIF i < -9 OR i = 0 THEN 
        	imp = 1;
        ELSEIF i < 9 AND i > 0 THEN
        	imp = 1-i*0.0430815;
        ELSEIF i < 0 AND i > -6 THEN 
        	imp = 1-i*0.0363248;
        ELSEIF i < -6 AND i > -9 THEN
        	imp = 1.2179488+((6+i)*0.0703972);
        END IF;
       impedances = array_append(impedances,imp-1); 
    END LOOP;
   RETURN query SELECT impedances;

END ;
$function$;