CREATE OR REPLACE FUNCTION age_14_under()
RETURNS TABLE (gid integer, vi TEXT, geom geometry, age_14_under integer) AS
$$
	SELECT l.gid, l.vi, l.geom, 
	case
		when (age_0_2_share+age_3_5_share+age_6_14_share)*100 < 4 Then 1
		when (age_0_2_share+age_3_5_share+age_6_14_share)*100 < 8  and 
				(age_0_2_share+age_3_5_share+age_6_14_share)*100 >= 4 Then 2
		when (age_0_2_share+age_3_5_share+age_6_14_share)*100 < 12  and 
				(age_0_2_share+age_3_5_share+age_6_14_share)*100 >= 8 Then 3
		when (age_0_2_share+age_3_5_share+age_6_14_share)*100 < 16 and 
				(age_0_2_share+age_3_5_share+age_6_14_share)*100 >= 12 Then 4
		when (age_0_2_share+age_3_5_share+age_6_14_share)*100 >= 16 Then 5
	end as age_14_under
    FROM muc_age l, study_area s 
    WHERE ST_Intersects(l.geom,s.geom)
$$
LANGUAGE sql;

COMMENT ON FUNCTION age_14_under() 
IS '**FOR-API-FUNCTION** RETURNS col_names[gid, vi, age_14_under] **FOR-API-FUNCTION**';