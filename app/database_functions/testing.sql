with x as (
	select  *
	from 
		heatmap(convert_from(decode('W3siJ2tpbmRlcmdhcnRlbiciOjF9XQ==','base64'),'UTF-8'),'index_0_001')
),
y as (
	SELECT x.grid_id,x.accessibility_index,x.geom, ntile(5) over 
	(order by x.accessibility_index) AS percentile_accessibility, g.percentile_population, 
	g.percentile_population-ntile(5) over (order by x.accessibility_index) AS population_accessibility
	FROM x, grid_500 g WHERE accessibility_index <> 0
	AND g.grid_id = x.grid_id
	ORDER BY grid_id
)
select * from y;

