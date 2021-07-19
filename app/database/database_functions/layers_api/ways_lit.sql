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
    SELECT lit, lit_classified, highway, surface, f.geom
    FROM footpath_visualization f, study_area s
    WHERE ST_Intersects(s.geom,f.geom);
$$
LANGUAGE sql;
    
COMMENT ON FUNCTION ways_lit() 
IS '**FOR-API-FUNCTION** RETURNS col_names[lit,lit_classified,highway,surface,geom] **FOR-API-FUNCTION**';