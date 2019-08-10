CREATE OR REPLACE FUNCTION multi_isochrones (userid integer, minutes integer, x numeric[], y numeric[], step integer, speed numeric,concavity numeric,modus integer,parent_id integer)
  RETURNS TABLE (geom geometry,population_administrative integer, reached_population integer, share_population float, step integer, name_administrative varchar, pois jsonb)
AS $$
 lon = x;
 lat = y;
 objectids = [];
 for i in range(len(lon)):
  objectid = plpy.execute("SELECT random_between(1,100000000) objectid")[0]["objectid"]
  objectids.append(str(objectid))
  plan = plpy.prepare('''INSERT INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id) 
					   SELECT *,$1 speed,$2 concavity,$3,$4 objectid,$5 parent_id 
					   FROM isochrones($6,$7,$8,$9,$10,$11,$12,$13,$14,$15)''', 
					   ["numeric","numeric","integer","integer","integer","integer","integer","numeric","numeric","integer","numeric","numeric","integer","integer","integer"])
  
  plpy.execute(plan,[speed,concavity,modus,objectid,parent_id,userid,minutes,lon[i],lat[i],step,speed,concavity,modus,objectid,parent_id])

 query = '''WITH u AS
			(
				SELECT st_union(st_intersection(i.geom,s.geom)) geom, s.sum_pop, i.step, s.name_administrative
				FROM isochrones i, study_area s
				WHERE st_intersects(i.geom,s.geom)
				AND objectid in('''+str(objectids)[1:-1]+''')
				GROUP BY s.gid, i.step
			),
			v as (
				SELECT u.geom, u.sum_pop::integer population_administrative, sum(p.population)::integer reached_population,
				sum(p.population)/(0.1+u.sum_pop) share_population,u.step, u.name_administrative --0.1 is added in order to avoid error division by zero
				FROM u, population p
				WHERE ST_Intersects(u.geom,p.geom)
				GROUP BY u.geom, u.sum_pop, u.step, u.name_administrative
			),
			p AS (
				SELECT p.amenity,count(*), v.geom
				FROM pois p, v, variable_container vc 
				WHERE st_intersects(p.geom,v.geom)
				AND amenity = any(vc.variable_array) 
				AND identifier = '''+"'poi_categories'"+'''
				GROUP BY amenity,v.geom
				UNION ALL
				SELECT p.public_transport_stop,count(*), v.geom
				FROM public_transport_stops p, v
				WHERE st_intersects(p.geom,v.geom)
				GROUP BY p.public_transport_stop,v.geom
			),
			jp AS (
				SELECT jsonb_object(array_agg(p.amenity),array_agg(p.count::text)) pois, p.geom 
				FROM p
				GROUP BY p.geom
			)
			SELECT v.*, jp.pois 
			FROM v,jp
			WHERE v.geom = jp.geom		
	'''
				
 response = plpy.execute(query)
 row_count  = response.nrows()
 return response[0:row_count]
$$ LANGUAGE plpython3u;