create or replace function plv8_concavehull()
returns text as $$
    var concaveman = require('concaveman');

   	var _rows = plv8.execute('SELECT array_agg(points_array)::text AS points_array FROM (SELECT ARRAY[ST_X(geom)::NUMERIC(6,4),ST_Y(geom)::NUMERIC(6,4)] as points_array FROM vertices) x');
    var points = _rows[0].points_array.replace(/{/g, '[').replace(/}/g, ']');
   	var points = JSON.parse(points)
   	plv8.elog(NOTICE, points[1])
   	
    return concaveman(points);
$$ language plv8;

SELECT ST_SETSRID(st_geomfromtext('POLYGON(('||REPLACE(plv8_concavehull(),',4',' 4')||'))'),4326)

