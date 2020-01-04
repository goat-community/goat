-- Add a column for slope values
ALTER TABLE ways ADD COLUMN slope float;

-- Update with: (elevation of end pt - elev of start pt )/length of segment
UPDATE ways SET slope=c.slope
from 
	(select a.id, (((b.elevation_b - a.elevation_a)/a.length_m)*100) as slope from
			(SELECT w.id, w.length_m, ST_Value(r.rast, ST_StartPoint(w.geom)) as elevation_a
			FROM ways AS w, dem as r
			WHERE ST_Intersects(r.rast, ST_StartPoint(w.geom)) and w.length_m != 0) as a
		natural join 
			(SELECT w.id, ST_Value(r.rast, ST_EndPoint(w.geom)) as elevation_b
			FROM ways AS w, dem as r
			WHERE ST_Intersects(r.rast, ST_EndPoint(w.geom))) as b) as c
where ways.id = c.id
;


ALTER TABLE ways ADD COLUMN length_dynamic float;

UPDATE ways SET length_dynamic=c.length_dynamic
from 
	(select a.id, 
	(a.length_m*(CASE WHEN a.way_type_factor IS NULL THEN 1 ELSE a.way_type_factor END)*(CASE WHEN b.surface_factor IS NULL THEN 1 ELSE b.surface_factor END)) as length_dynamic FROM
		(SELECT s.id, s.osm_id, length_m, w.way_type_factor
		FROM (public.ways s left join way_type_factor w on s.class_id=w.class_id)) a 
	left join (select p.osm_id, sf.surface_factor
	 	FROM(SELECT osm_id, surface FROM public.planet_osm_roads)p left join public.surface_factor sf on p.surface=sf.surface) b 
	 	on a.osm_id=b.osm_id) as c
where ways.id=c.id
;


ALTER TABLE ways ADD COLUMN bicycle text;
ALTER TABLE ways ADD COLUMN foot text;

UPDATE ways w SET bicycle = p.bicycle FROM planet_osm_line p WHERE w.osm_id=p.osm_id;
UPDATE ways w SET foot = p.foot FROM planet_osm_line p WHERE w.osm_id=p.osm_id;