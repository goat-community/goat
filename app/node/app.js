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


app.get('/multiple_isochrones/:parameters',(request,response) => {
	let {parameters} = request.params;
	parameters = JSON.parse(parameters);
	let array_objectids = [];
	const {amenity,userid,minutes,step,speed,concavity,modus,parent_id} = parameters
	pool.query(`SELECT ST_X(p.geom) x,ST_Y(p.geom) y FROM pois p, study_area_union s WHERE p.amenity = '${amenity}' and ST_Intersects(p.geom,s.geom)`
		, (err, res) => {
		if (err) return console.log(err);
		for (i = 0; i < res.rows.length; i++){
			const objectid = Math.floor(Math.random() * 10000000);
			array_objectids.push(objectid);

			let sql_query = `INSERT INTO isochrones(userid,id,step,geom,speed,concavity,modus,objectid,parent_id)
							 SELECT *,$1 speed,$2 concavity,$3,$4 objectid,$5 parent_id 
							 FROM isochrones($6,$7,$8,$9,$10,$11,$12,$13,$14,$15)` 
	
			pool.query(sql_query, [speed,concavity,modus,objectid,parent_id,userid,minutes,res.rows[i].x,res.rows[i].y,step,speed,concavity,modus,objectid,parent_id]
			,(err,res) => {
				if(err) return console.log(err);
				console.log(res.rows)
			})
		}
		console.log(array_objectids);
		pool.query(`WITH u AS
					(
						SELECT st_union(st_intersection(i.geom,s.geom)) geom, s.sum_pop
						FROM isochrones i, study_area s
						WHERE step = 10
						AND st_intersects(i.geom,s.geom)
						AND objectid in($1)
						GROUP BY s.gid
					)
					SELECT u.geom, u.sum_pop, sum(p.population),sum(p.population)/u.sum_pop
					FROM u, population p
					WHERE ST_Intersects(u.geom,p.geom)
					GROUP BY u.geom, u.sum_pop`,[array_objectids]
		,(err,res) => {
		if (err) return console.log(err);
		console.log(res.rows);
		})
	});



});

/*
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
*/

module.exports = app;
