/*
In order to use this function you need to install related Javascript module into DB.

DROP TABLE IF EXISTS plv8_js_modules;
CREATE TABLE plv8_js_modules (
	module text unique primary key,
	autoload bool default true,
	source text
);

# Download Javascript 
wget -O opening_hours.js https://openingh.openstreetmap.de/opening_hours.js/opening_hours+deps.min.js

# Run commands in psql 
psql <connection options>
goat=# \set opening_hours  `cat opening_hours.js`
goat=# insert into plv8_js_modules values ('opening_hours',true,:'opening_hours');

*/

drop function check_open_js(text, integer[],text);
create or replace function check_open_js(opening_hour text, ref_time integer[], country_code text default null, state text default null)
returns text as $$
    var opening_hours = require('opening_hours');
   	if (country_code) {
   		var oh = new opening_hours(opening_hour,{'address':{'country_code': country_code, 'state': state} });
   	} else {
    	var oh = new opening_hours(opening_hour,null);
	}
    var check_time = ref_time[0]+ " Nov 2019 " + ref_time[1] + ":" + ref_time[2]; 
	var date = new Date(check_time);
	return 	oh.getState(date);
$$ language plv8;


