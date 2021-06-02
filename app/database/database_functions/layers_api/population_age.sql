CREATE OR REPLACE FUNCTION population_14_under()
RETURNS TABLE (age_14_under float, gid integer, vi TEXT, geom geometry) AS
$$
	SELECT (age_0_2_share+age_3_5_share+age_6_14_share)*100 as age_14_under, l.gid, l.vi, l.geom 
    FROM muc_age l, study_area s 
    WHERE ST_Intersects(l.geom,s.geom)
$$
LANGUAGE sql;

COMMENT ON FUNCTION population_14_under() 
IS '**FOR-API-FUNCTION** RETURNS col_names[age_14_under, gid, vi] **FOR-API-FUNCTION**';

CREATE OR REPLACE FUNCTION population_15_64()
RETURNS TABLE (age_15_64 float, gid integer, vi TEXT, geom geometry) AS
$$
	SELECT age_15_64_share*100 as age_15_64, l.gid, l.vi, l.geom 
    FROM muc_age l, study_area s 
    WHERE ST_Intersects(l.geom,s.geom)
$$
LANGUAGE sql;

COMMENT ON FUNCTION population_15_64() 
IS '**FOR-API-FUNCTION** RETURNS col_names[age_15_64, gid, vi] **FOR-API-FUNCTION**';

CREATE OR REPLACE FUNCTION population_65_over()
RETURNS TABLE (age_65_over float, gid integer, vi TEXT, geom geometry) AS
$$
	SELECT (age_65_74_share+age_over_75_share)*100 as age_65_over, l.gid, l.vi, l.geom 
    FROM muc_age l, study_area s 
    WHERE ST_Intersects(l.geom,s.geom)
$$
LANGUAGE sql;

COMMENT ON FUNCTION population_65_over() 
IS '**FOR-API-FUNCTION** RETURNS col_names[age_65_over, gid, vi] **FOR-API-FUNCTION**';

SELECT jsonb_pretty(metadata) FROM layer_metadata;

