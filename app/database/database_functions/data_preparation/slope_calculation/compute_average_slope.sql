/*This function computes the average slope for given array of elevations, linkLength and lengthInterval between to points
The last point is expected to not meet the average lengthInterval and therefore the remaining distance is computed.
*/
DROP FUNCTION IF EXISTS compute_average_slope;
CREATE OR REPLACE FUNCTION public.compute_average_slope(elevs float[], linkLength float, lengthInterval float)
 RETURNS SETOF float 
 LANGUAGE plpgsql
AS $function$
DECLARE
	slope float;
BEGIN 

	WITH elevs AS
	(
		SELECT ROW_NUMBER() OVER() gid, 
		CASE WHEN ((ROW_NUMBER() OVER()-1) * lengthInterval) > linkLength 
		THEN linkLength - ((ROW_NUMBER() OVER()-2) * lengthInterval) 
		ELSE lengthInterval END AS len, linkLength, elev 
		FROM LATERAL UNNEST(elevs) elev
	)
	SELECT SUM(abs(((t2.elev - t1.elev) / t2.len)) * (t2.len/t2.linkLength)) * 100 
	INTO slope
	FROM elevs t1, elevs t2 
	WHERE t1.gid + 1 = t2.gid;

	RETURN NEXT slope;

END ;
$function$ IMMUTABLE;
/*
SELECT compute_average_slope(elevs, length_m, elevs_interval ) 
FROM (SELECT * FROM elevs_ways e LIMIT 1) x 
*/