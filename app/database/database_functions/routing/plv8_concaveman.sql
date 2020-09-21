CREATE OR REPLACE FUNCTION  plv8_concaveman()
RETURNS text AS $$
    var concaveman = require('concaveman');

   	var _rows = plv8.execute('SELECT array_agg(points_array)::text AS points_array FROM (SELECT ARRAY[ST_X(geom)::NUMERIC(6,4),ST_Y(geom)::NUMERIC(6,4)] as points_array FROM iso_vertices) x');
    var points = _rows[0].points_array.replace(/{/g, '[').replace(/}/g, ']');
   	var points = JSON.parse(points)
   	plv8.elog(NOTICE, points[1])
   	
    return concaveman(points, concavity = 2, lengthThreshold = 0.006);
$$ LANGUAGE plv8;

/*
SELECT ST_SETSRID(st_geomfromtext('POLYGON(('||REPLACE(plv8_concavehull(),',4',' 4')||'))'),4326) AS geom 

DROP TABLE test; 
CREATE TABLE test AS 
SELECT CASE WHEN start_cost > end_cost THEN st_startpoint(geom) ELSE st_endpoint(geom) END AS geom, COST 
FROM edges; 
*/
