CREATE OR REPLACE FUNCTION ways_lit()
RETURNS TABLE (lit text, lit_classified text, highway text, surface text, geom geometry) AS
$$
    WITH variables AS 
    (
        SELECT variable_object AS lit ,
        select_from_variable_container('excluded_class_id_walking') AS excluded_class_id_walking,
        select_from_variable_container('categories_no_foot') AS categories_no_foot,
        select_from_variable_container('categories_sidewalk_no_foot') AS categories_sidewalk_no_foot
        FROM variable_container
        WHERE identifier='lit'
    )
    SELECT lit, lit_classified, highway, surface, w.geom
    FROM ways w, study_area s
    WHERE class_id::text NOT IN (SELECT UNNEST(excluded_class_id_walking) FROM variables)
    AND (foot IS NULL OR foot NOT IN (SELECT UNNEST(categories_no_foot) FROM variables))
    AND (sidewalk IS NULL OR sidewalk NOT IN (SELECT UNNEST(categories_sidewalk_no_foot) FROM variables))
    AND ST_Intersects(s.geom,w.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_lit() 
IS '**FOR-API-FUNCTION** RETURNS col_names[lit,lit_classified,highway,surface,geom] **FOR-API-FUNCTION**';