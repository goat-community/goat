CREATE OR REPLACE FUNCTION pois_multi_isochrones (pois text,userid integer, minutes integer,step integer, speed numeric,concavity numeric,modus integer,parent_id integer)
  RETURNS TABLE (geom geometry,population_administrative integer, reached_population integer, share_population float, step integer, name varchar, pois jsonb)
AS $$
 pois_array = [];
 pois_input = pois.split(',')
 poi_categories = list(plpy.execute("SELECT variable_array FROM variable_container WHERE identifier = 'poi_categories'")[0]["variable_array"])
 array_x = []
 array_y = [] 
 for i in pois_input:
 	if i in poi_categories:
 		pois_array.append(i)
 pois_array = str(pois_array)
 
 buffer_study_area = str(minutes * speed) 
 query = "SELECT ST_x(p.geom) x,ST_y(p.geom) y FROM pois p, study_area s \
		  WHERE p.geom && ST_Buffer(s.geom::geography,"+buffer_study_area+")::geometry \
		  AND p.amenity IN ("+pois_array[1:-1]+") UNION ALL "
 query = query + "SELECT ST_x(p.geom) x,ST_y(p.geom) y \
				  FROM public_transport_stops p, study_area s \
				  WHERE p.geom && ST_Buffer(s.geom::geography,"+buffer_study_area+")::geometry \
				  AND p.public_transport_stop IN ("+pois_array[1:-1]+");"
 for i in plpy.execute(query):
 	array_x.append(i["x"])
 	array_y.append(i["y"])
 query = "SELECT * FROM \
		  multi_isochrones ($1, $2, '{"+str(array_x)[1:-1]+"}','{"+str(array_y)[1:-1]+"}',$3, $4,$5,$6,$7)"
 plan = plpy.prepare(query,["integer","integer","integer","numeric","numeric","integer","integer"])
 response = plpy.execute(plan,[userid,minutes,step,speed,concavity,modus,parent_id])
 row_count  = response.nrows() 
 return response[0:row_count]
$$ LANGUAGE plpython3u;