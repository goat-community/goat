CREATE OR REPLACE FUNCTION test()
  RETURNS TABLE (geom geometry,cost numeric)
AS $$

 query = "SELECT t1.cost, t2.geom \
		FROM PGR_DrivingDistance( \
		'SELECT id::int4, source, target, length_m as cost \
		FROM ways',1,83.33, false, false) t1, "+"ways"+" t2 WHERE t1.id2 = t2.id"
 plan = plpy.prepare(query)
 response = plpy.execute(plan)
 row_count  = response.nrows() 
 return response[0:row_count]
$$ LANGUAGE plpython3u;   
   