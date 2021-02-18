CREATE OR REPLACE FUNCTION ways_wheelchair()
RETURNS TABLE (wheelchair text, wheelchair_classified text, highway text, incline text, smoothness text, surface text, sidewalk text, 
sidewalk_both_width numeric, sidewalk_right_width numeric, sidewalk_left_width numeric, width numeric, geom geometry) AS
$$
    WITH variables AS 
    (
        SELECT variable_object AS wheelchair ,
        select_from_variable_container('excluded_class_id_walking') AS excluded_class_id_walking,
        select_from_variable_container('categories_no_foot') AS categories_no_foot,
        select_from_variable_container('categories_sidewalk_no_foot') AS categories_sidewalk_no_foot
        FROM variable_container
        WHERE identifier='wheelchair'
    )
    SELECT wheelchair, wheelchair_classified, highway, incline, smoothness, surface, sidewalk, 
    sidewalk_both_width, sidewalk_right_width, sidewalk_left_width, width, w.geom
    FROM ways w, study_area s
    WHERE class_id::text NOT IN (SELECT UNNEST(excluded_class_id_walking) FROM variables)
    AND (foot IS NULL OR foot NOT IN (SELECT UNNEST(categories_no_foot) FROM variables))
    AND (sidewalk IS NULL OR sidewalk NOT IN (SELECT UNNEST(categories_sidewalk_no_foot) FROM variables))
    AND ST_Intersects(s.geom,w.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_wheelchair() 
IS '**FOR-API-FUNCTION** RETURNS col_names[wheelchair,wheelchair_classified,highway,incline,smoothness,surface,sidewalk,sidewalk_both_width,sidewalk_right_width,sidewalk_left_width,width,geom] **FOR-API-FUNCTION**';