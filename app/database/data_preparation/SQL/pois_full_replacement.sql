------------------------------------------------------------------------------------
------------------GOAT POIS FULL CATEGORY REPLACEMENT FUNCTION ---------------------
------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION pois_full_replacement (input_table TEXT, input_amenity TEXT, pois_amenity TEXT )
RETURNS void
LANGUAGE plpgsql
AS $function$
BEGIN
	DELETE FROM pois
	WHERE amenity = pois_amenity;

EXECUTE 'INSERT INTO pois
		SELECT	NULL, pfr.origin_geo, NULL,NULL, pfr.amenity, NULL, NULL, NULL, NULL, pfr."name", NULL, NULL, NULL, NULL, pfr.opening_ho, NULL, NULL, pfr.geom, pfr.wheelchair
FROM (SELECT * FROM '||quote_ident(input_table)||' WHERE amenity = '||quote_literal(input_amenity)||') AS pfr';

END;
$function$;

-- Population_array_per_hexagon
-- DESCRIPTION:				This FUNCTION DELETE ALL the amenity=INPUT_amenity FROM POIS AND REPLACE FOR a NEW DATA IN INput_table FOR the respective amenity
-- INPUT PARAMETERS:
-- input_table (text) 		Select the table that contains the new pois.
-- input_amenity (text) 	Select the amenity category to be replaced.
-- pois_amenity (text) 		Select the amenity category to be replaced in pois.

-- Example
-- SELECT pois_full_replacement('pois_full_replacement','kindergarten','kindergarten');

SELECT * FROM pois_userinput;
