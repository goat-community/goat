----------------------------------------
--------- TAZ Trips FUNCTION -----------
----------------------------------------

DROP FUNCTION IF EXISTS trips_visualization;
CREATE OR REPLACE FUNCTION public.trips_visualization(userid_input integer, zone_type TEXT, zone_id int, trans_mode varchar)
RETURNS TABLE (
	zone_number numeric,
	transport_mode varchar,
	number_of_trips numeric,
	category numeric,
	geom geometry
)
LANGUAGE plpgsql
AS $function$
DECLARE 
	zone_group TEXT;
	zone_map TEXT;
	map_type TEXT;
	total_trips NUMERIC;
BEGIN
	IF zone_type = 'origin_zone' THEN 
		zone_group = 'origin_zone';
		zone_map = 'destination_zone';
	ELSE 
		zone_group = 'destination_zone';
		zone_map = 'origin_zone';
	END IF;

	DROP TABLE IF EXISTS temp_od_table;

	CREATE TABLE temp_od_table (zone NUMERIC, transport_mode varchar, trips NUMERIC, geom geometry, category NUMERIC);
	EXECUTE '
	INSERT INTO temp_od_table
		SELECT m.'||quote_ident(zone_group)||' , '||quote_literal(trans_mode)||', sum(m.'||quote_ident(trans_mode)||'), t.geom
		FROM taz t
		RIGHT JOIN matrix m
			ON m.'||quote_ident(zone_map)||' = t.zat
			WHERE m.'||quote_ident(zone_map)||' = '||zone_id||' GROUP BY m.'||quote_ident(zone_group)||', '||quote_ident(trans_mode)||', t.geom';
	
	---- Noise compression, discard trips to zones farther than a radius of 2500m ---

	DROP TABLE IF EXISTS od_table_cleaned;
	CREATE TABLE od_table_cleaned (LIKE temp_od_table INCLUDING ALL);
	EXECUTE '
	INSERT INTO od_table_cleaned
	WITH selected_taz AS (SELECT ST_buffer(t.geom::geography, 2500) AS geometry FROM taz t WHERE zat = '||quote_literal(zone_id)||'),
	filtered_taz AS (SELECT t.* FROM taz t, selected_taz st WHERE ST_Intersects(t.geom::geometry, st.geometry::geometry))
	
	SELECT t.zone, t.transport_mode, t.trips, ft.geom, t.category FROM temp_od_table t
	INNER JOIN filtered_taz ft
	ON t.ZONE = ft.zat';			
	---- Calculate % of trips from/to surrounding areas

	SELECT sum(trips) into total_trips FROM od_table_cleaned;

	UPDATE od_table_cleaned	
	SET category = trips/total_trips;

	RETURN query
	EXECUTE '
	SELECT z.zat, '||quote_literal(trans_mode)||'::varchar, COALESCE (trips::NUMERIC,0), COALESCE(round(t.category,6)::NUMERIC,0), z.geom FROM od_table_cleaned t
	RIGHT JOIN taz z
	ON t.zone = z.zat';

END;
$function$

-- Example
-- SELECT * FROM trips_visualization(1, 'destination_zone', 100, 'walking_trips');
-- Variables User input
-- 			zone_type (char) between origin_zone or destination_zone
--			zone_id (int) zone identifier for filters
--			trans_mode(char) between walking_trips or cycling_trips

-- Test table for create visualization style


/*
DROP TABLE IF EXISTS visualization;
CREATE TABLE visualization (zone_number NUMERIC, transport_mode varchar,number_of_trips numeric, category numeric,geom geometry);

INSERT INTO visualization
SELECT * FROM trips_visualization(1, 'origin_zone', 336, 'walking_trips') ORDER BY category desc;

 */




