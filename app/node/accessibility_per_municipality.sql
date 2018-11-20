WITH u AS
(
	SELECT st_union(st_intersection(i.geom,s.geom)) geom, s.sum_pop
	FROM isochrones i, study_area s
	WHERE step = 10
	AND st_intersects(i.geom,s.geom)
	GROUP BY s.gid
)
SELECT u.geom, u.sum_pop, sum(p.population),sum(p.population)/u.sum_pop
FROM u, population p
WHERE ST_Intersects(u.geom,p.geom)
GROUP BY u.geom, u.sum_pop
