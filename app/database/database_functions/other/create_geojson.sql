CREATE OR REPLACE FUNCTION public.create_geojson(arr_json_attributes jsonb[], arr_geom geometry[])
 RETURNS SETOF jsonb
 LANGUAGE plpgsql
AS $function$
 
BEGIN 
	RETURN query 
	
	SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(features.feature)
	)
	FROM (
	SELECT jsonb_build_object(
		'type',       'Feature',
	    'id',         ROW_NUMBER() OVER(),
	    'geometry',   ST_AsGeoJSON(inputs.geom)::jsonb,
	    'properties', inputs.json_attributes
	) AS feature 
	FROM 
	(
		SELECT UNNEST(arr_json_attributes) AS json_attributes, unnest(arr_geom) AS geom 
	) inputs) features; 
END;
$function$

/*SELECT create_geojson(ARRAY[jsonb_build_object('a','abc'),jsonb_build_object('a','dfg')],ARRAY[ST_MAKEPOINT(11.2333,48.2132),ST_MAKEPOINT(11.3352,48.1328)])*/
