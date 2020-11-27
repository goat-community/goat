CREATE OR REPLACE FUNCTION append_geojson(arr_geojson jsonb, layer_geojson jsonb, layer_name text)
RETURNS jsonb AS
$$

	SELECT CASE 
	WHEN layer_geojson <> '{"type": "FeatureCollection", "features": null}' 
	THEN arr_geojson || jsonb_build_object(layer_name,layer_geojson) 
	ELSE arr_geojson END;

$$
LANGUAGE sql immutable;