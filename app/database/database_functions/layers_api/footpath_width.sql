CREATE OR REPLACE FUNCTION footpath_width()
RETURNS TABLE (sidewalk text, width numeric, highway text, geom geometry) AS
$$
	SELECT f.sidewalk, (f.width ->> 'width')::numeric AS width, f.highway, f.geom FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom) AND (f.width ->> 'width') IS NOT NULL 
    UNION 
    SELECT f.sidewalk, (f.width ->> 'sidewalk_both_width')::numeric AS width, f.highway, f.geom FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom) AND (f.width ->> 'sidewalk_both_width') IS NOT NULL
    UNION 
    SELECT f.sidewalk, (f.width ->> 'sidewalk_left_width')::numeric AS width, f.highway, f.geom FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom) AND (f.width ->> 'sidewalk_left_width') IS NOT NULL
    UNION 
    SELECT f.sidewalk, (f.width ->> 'sidewalk_right_width')::numeric AS width, f.highway, f.geom FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom) AND (f.width ->> 'sidewalk_right_width') IS NOT NULL
    UNION 
    SELECT f.sidewalk, (f.width)::numeric AS width, f.highway, f.geom FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom) AND width IS NULL
    ;
$$
LANGUAGE sql;

COMMENT ON FUNCTION footpath_width() 
IS '**FOR-API-FUNCTION** RETURNS col_names[sidewalk,width,highway,geom] **FOR-API-FUNCTION**';

--TODO: build average for sidewalk: both and different values for left & right