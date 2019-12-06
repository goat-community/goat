DROP FUNCTION IF EXISTS check_open;
CREATE OR REPLACE FUNCTION check_open (opening_hour text, ref_time integer[])
  RETURNS text
AS $$
	import humanized_opening_hours 
	from datetime import datetime
	import datetime
	try:
		oh = humanized_opening_hours.OHParser(opening_hour)
		dt=datetime.datetime(2019,11,ref_time[0],ref_time[1],ref_time[2])
		x=str(oh.is_open(dt))
	except AttributeError:
		x="Error"
	return x
$$ LANGUAGE plpython3u;

/*SELECT gid,amenity,opening_hours,check_open(opening_hours,array[21, 9, 0]) FROM pois WHERE opening_hours IS NOT NULL AND amenity = 'supermarket'
*/


