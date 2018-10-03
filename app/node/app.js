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
  pool.query('select id, class_id, st_AsGeoJSON(geom) geom from ways limit 100', (err,res) => {
    if (err) return console.log(err);
    let rows = res.rows
    let features = [];
    for (row of rows){
    	let geojson = JSON.parse(row.geom)
	    geojson.properties = { id: row.id, class_id: row.class_id}
	    features.push(geojson)
    }
    
    response.send(features);
  
  });
});

module.exports = app;

