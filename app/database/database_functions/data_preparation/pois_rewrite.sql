--- POIS_rewrite
/*Reclassificate pois from a specific category (old_amenity), into a (new amenity) based on name like (keyword) without delete pois from the first database
Arguments: 
old_amenity = amenity category to filter
new_amenity = new category to assign to data
keyword = keyword to be used to look into names to reclassify, should be written in lower
*/

CREATE OR REPLACE FUNCTION pois_rewrite (old_amenity TEXT, new_amenity TEXT, keyword TEXT )
	RETURNS void
	--- Reclassificate points based on specific condition in the column "name". 
	LANGUAGE plpgsql
AS $function$
BEGIN
	DROP TABLE IF EXISTS pois_temp;
	CREATE TEMP TABLE pois_temp (LIKE pois INCLUDING ALL);	
	INSERT INTO pois_temp
	SELECT * FROM pois WHERE amenity = old_amenity AND lower(name) LIKE keyword;
	UPDATE pois_temp
	SET amenity = new_amenity;

INSERT INTO pois
	SELECT * FROM pois_temp;
	
END
$function$;


/*SELECT pois_override('nursery','kindergarten','%kindergarten%')
 */
