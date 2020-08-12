

--CREATE INDEX ON reached_pois_heatmap USING gin (accessibility_indices gin__int_ops)

EXPLAIN ANALYZE 
WITH x AS 
(
	SELECT gridids, accessibility_indices[1][1:]
	FROM reached_pois_heatmap 
	WHERE amenity IN ('kindergarten','nursery','primary_school','secondary_school','bar','biergarten','cafe','pub','fast_food','ice_cream','restaurant','theatre','sum_population','cinema','library','night_club','recycling',
	      'car_sharing','bicycle_rental','charging_station','bus_station','tram_station','subway_station','railway_station','taxi','bikesharing_ffb','carsharing_ffb','charging_station_marker_ffb','charging_station_other_ffb','charging_station_public_ffb','e_parking_ffb',
	      'l-station_ffb','s-station_prio1_ffb','s-station_prio2_ffb','hairdresser','atm','bank','dentist','doctors','pharmacy','post_box','post_office','fuel',
	      'bakery','butcher','clothes','convenience','general','fashion','florist','greengrocer','kiosk','mall','shoes','sports','supermarket','health_food','discount_supermarket',
	      'hypermarket','international_supermarket','chemist','organic','marketplace','hotel','museum','hostel','guest_house','viewpoint','gallery','playground','discount_gym','gym','yoga','outdoor_fitness_station'
	)
) 
SELECT grid_id,sum(accessibility_index) 
FROM x, UNNEST(x.gridids, x.accessibility_indices) AS u(grid_id, accessibility_index)
GROUP BY grid_id; 



--SELECT * FROM compute_accessibility_index(0.3, ARRAY[100,200,300,400,500,600,700]::SMALLINT[], ARRAY[300,400,500,700,800,1000,1300]::SMALLINT[], ARRAY[200000,250000, 300000, 350000, 400000, 450000])

DROP TABLE IF EXISTS test_edges;
CREATE TABLE test_edges AS 
SELECT start_cost[gridids # 233], end_cost[gridids # 233], GREATEST(start_cost[gridids # 233],end_cost[gridids # 233]), geom      
FROM reached_edges_heatmap reh  
WHERE gridids && ARRAY[233]

DROP TABLE IF EXISTS test_pois;
CREATE TABLE test_pois AS 
SELECT gridids # 233, r.gid, r.amenity, r.name, true_cost[gridids # 233], p.geom      
FROM reached_pois_heatmap r, pois p  
WHERE gridids && ARRAY[233]
AND r.gid = p.gid; 

