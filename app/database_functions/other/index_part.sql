SELECT grid_id, part_accessibility_index((pois -> 'atm'),0.01) FROM grid_500

CREATE OR REPLACE FUNCTION public.part_accessibility_index(traveltime_array jsonb, beta numeric)
RETURNS SETOF NUMERIC 

LANGUAGE sql
AS $function$
	WITH index_part AS 
	(
		SELECT EXP(beta*jsonb_array_elements(traveltime_array)::text::numeric) AS part
	)
	SELECT sum(part) 
	FROM index_part;
$function$