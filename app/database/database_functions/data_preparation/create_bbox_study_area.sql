CREATE OR REPLACE FUNCTION create_bbox_study_area(buffer float)
RETURNS TEXT 
LANGUAGE SQL AS 
$$
	WITH bbox AS 
	(
		SELECT ST_EXTENT(ST_MakePolygon(geom)) AS geom 
		FROM 
		(
		   SELECT ST_ExteriorRing((ST_Dump(st_union(ST_BUFFER(geom, buffer)))).geom) As geom
		   FROM study_area
		) s
		WHERE ST_AREA(ST_MakePolygon(geom)::geography) > 10000
		GROUP BY ST_MakePolygon(geom)
	)
	SELECT string_agg(format('--bounding-box top=%s left=%s bottom=%s right=%s', 
	st_ymax(geom)::text, st_xmin(geom)::text,st_ymin(geom)::TEXT, st_xmax(geom)::TEXT), ' \n')  
	FROM bbox;
$$
/*SELECT create_bbox_study_area(0.0045)*/