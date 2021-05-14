
/*
This function receives a JSON-object containing the information if the building is classified residential or not 
based on different landuse datasets. If the classification is not the same for all landuse files, the dominant
classification will be determined with the function derive_dominant_class(bgid integer, categorization integer[], landuse_gids integer[], landuse_table TEXT).
0 ==> residential
1 ==> not_residential
2 ==> no landuse
*/
DROP FUNCTION IF EXISTS classify_building;
CREATE OR REPLACE FUNCTION classify_building(bgid integer, categorization jsonb)
 RETURNS integer
AS $$
DECLARE
   categorization_unique integer[][] := ARRAY[[]]::integer[][];
   cnt integer := 0;
   single_categorization jsonb;
   categories integer[];
   landuse_table TEXT;
   landuse_gids integer[];
   dominant_class integer;
BEGIN

	FOR single_categorization IN SELECT * FROM jsonb_array_elements(categorization)
	LOOP 
		
		categories = jsonb_array_int_array(single_categorization -> 'categorization');
  		landuse_table = single_categorization ->> 'table';
  		landuse_gids = jsonb_array_int_array((single_categorization -> (landuse_table || '_gid')));
  
  		IF categories = ARRAY[2]::integer[] THEN 
  			dominant_class = 2; 
  		ELSE 
  			dominant_class = derive_dominant_class(bgid,categories,landuse_gids,landuse_table);
  		END IF; 
  		categorization_unique = ARRAY_APPEND(categorization_unique,dominant_class); 

   	END LOOP;
   
   	IF ARRAY_LENGTH(uniq(categorization_unique),1) = 1 THEN 
   		RETURN categorization_unique[1];
   	ELSEIF categorization_unique[1] = categorization_unique[2] THEN 
   		RETURN categorization_unique[1];
   	ELSEIF categorization_unique[1] IN (0, 2) AND categorization_unique[2] = 1 THEN 
   		RETURN categorization_unique[2];
   	ELSEIF categorization_unique[2] IN (0, 2) AND categorization_unique[1] = 1 THEN 
   		RETURN categorization_unique[1];
   	ELSEIF categorization_unique[1] = 2 AND categorization_unique[2] = 2 THEN 
   		RETURN categorization_unique[3];
   	ELSE 
   		RETURN 0;
    END IF; 

END
$$ LANGUAGE plpgsql IMMUTABLE;
/*
SELECT classify_building(1,'[{"table": "landuse", "landuse_gid": [14484, 14595, 14500], "categorization": [0, 1, 1]}, {"table": "landuse_additional", "categorization": [0], "landuse_additional_gid": 
[3695]}, {"table": "landuse_osm", "categorization": [1, 0], "landuse_osm_gid": [5401, 5412]}]'::jsonb)
*/
