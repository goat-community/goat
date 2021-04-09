CREATE OR REPLACE FUNCTION return_meter_srid_4326()
RETURNS FLOAT AS
$$
	SELECT r.radius AS meter_in_degree
	FROM study_area_union, LATERAL ST_MinimumBoundingRadius(ST_TRANSFORM(ST_BUFFER(ST_CENTROID(geom)::geography,1)::geometry, 4326)) r
$$
LANGUAGE sql;