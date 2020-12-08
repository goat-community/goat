DROP FUNCTION IF EXISTS interpolate_cost; 
		
CREATE OR REPLACE FUNCTION interpolate_cost(fraction float, start_cost SMALLINT[], end_cost SMALLINT[])
RETURNS smallint[] AS
$$
	SELECT ARRAY_AGG(CASE WHEN start_cost < end_cost THEN (start_cost + fraction * (end_cost-start_cost))::smallint
	ELSE (end_cost + (1-fraction) * (start_cost - end_cost))::smallint END)
	FROM (
		SELECT UNNEST(start_cost) start_cost, UNNEST(end_cost) end_cost
	) x;
	
$$
LANGUAGE sql immutable;

--SELECT * FROM interpolate_cost(0.5, ARRAY[100,200,300]::SMALLINT[], ARRAY[200,300,400]::SMALLINT[]);
