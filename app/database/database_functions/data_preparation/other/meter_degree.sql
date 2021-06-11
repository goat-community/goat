DROP FUNCTION IF EXISTS meter_degree();
CREATE OR REPLACE FUNCTION public.meter_degree()
RETURNS NUMERIC AS
$$
	SELECT select_from_variable_container_s('one_meter_degree')::numeric;
$$
LANGUAGE sql;

--SELECT meter_degree() 