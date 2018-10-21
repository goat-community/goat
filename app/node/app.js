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


app.get('/multiple_isochrone/:amenity',(request,response) => {
	const {amenity} = request.params;
	pool.query(`SELECT ST_X(geom) x,ST_Y(geom) y FROM pois WHERE amenity = '${amenity}'`
		, (err, res) => {
		if (err) return console.log(err);
		let array_objectids = [];
		for (i = 0; i < res.rows.length; i++){
			const objectid = Math.floor(Math.random() * 10000000);
			array_objectids.push(objectid);
			let sql_query = `INSERT INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id)
							 SELECT *,83.33 speed,0.99 concavity,1 modus,${objectid} objectid,1 parent_id 
							 FROM isochrones(1,10,${res.rows[i].x},${res.rows[i].y},1,83.33,0.99,1,${objectid},1)` 
			console.log(sql_query);
			pool.query(sql_query
			,(err,res) => {
				if(err) return console.log(err);
				console.log(res.rows)
			})
		}
		
	});
});

app.get('/load_ways', (request,response) => {
	pool.query(`select id, class_id, st_AsGeoJSON(geom) geom from ways
	where st_intersects(geom,st_buffer(st_setsrid(st_point(10.683605,47.575593),4326)::geography,1000))`, (err,res) => {
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
