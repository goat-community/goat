const express = require('express');
const pool = require('./db');
const app = express();
const GeoJSON = require('geojson')
const cors = require('cors')
// use it before all route definitions
app.use(cors({origin: '*'}));
app.use(function(request,response,next){
	response.header("Access-Control-Allow-Origin", "*");
	response.header("Access-Control-Allow-Methods" ,"POST, GET, PUT, DELETE, OPTIONS");
	response.header("Access-Control-Allow-Credentials", 'false');
	response.header("Access-Control-Max-Age",'86400'); // 24 hours
	if (request.method == 'OPTIONS') {
		  response.status(204).end();
	}
	else{
	  next();
	} 
});




app.get('/load_ways', (request,response) => {
  pool.query('select id, class_id, st_AsGeoJSON(geom) geom from ways', (err,res) => {
    if (err) return console.log(err);
    let rows = res.rows
  var obj, i;
	obj = {
		type: "FeatureCollection",
		features: []
	};

		for (i = 0; i < rows.length; i++) {
			var item, feature, geometry;
			item = rows[i];
	
			geometry = JSON.parse(item.geom);
			delete item.geom;
	
			feature = {
				type: "Feature",
				properties: item,
				geometry: geometry
			}
	
			obj.features.push(feature);
		} 

     response.send(obj);
  
  });
});





module.exports = app;

