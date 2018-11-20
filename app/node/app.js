const express = require('express');
const pool = require('./db');
const app = express();
const GeoJSON = require('geojson')
const cors = require('cors')
const bodyParser = require('body-parser');
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

var jsonParser = bodyParser.json()
	  // to support JSON-encoded bodies
var urlencodedParser = bodyParser.urlencoded({ extended: false })

app.get('/multiple_isochrones/:parameters',(request,response) => {
	let {parameters} = request.params;
	parameters = JSON.parse(parameters);
	let array_objectids = [];
	const {amenity,userid,minutes,step,speed,concavity,modus,parent_id} = parameters
	console.log(typeof(Array.from(amenity)))
	console.log(amenity)
	let multi_isochrone;
	pool.query(`SELECT ST_X(p.geom) x,ST_Y(p.geom) y FROM pois p, study_area_union s WHERE p.amenity::varchar in($1) and ST_Intersects(p.geom,s.geom)`,[amenity]
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
						SELECT st_union(st_intersection(i.geom,s.geom)) geom, s.sum_pop, i.step, s.name
						FROM isochrones i, study_area s
						WHERE st_intersects(i.geom,s.geom)
						AND objectid::varchar in($1)
						GROUP BY s.gid, i.step
					)
					SELECT u.geom, u.sum_pop, sum(p.population),
					sum(p.population)/(0.1+u.sum_pop) share_population,u.step, u.name --0.1 is added in order to avoid error division by zero
					FROM u, population p
					WHERE ST_Intersects(u.geom,p.geom)
					GROUP BY u.geom, u.sum_pop, u.step, u.name`,[array_objectids]
		,(err,res) => {
		if (err) return console.log(err);
		multi_isochrone = res.rows;
		})

	});
	response.send(multi_isochrone)



});

app.post('/userdata',jsonParser, (request,response) => {
	//CRUD OPERATION
	var mode = request.body.mode;
	function returnResult (err,res){
		if (err) return console.log(err);
			   response.send(res.rows);
	}
	if (mode == 'read'){ //read is used to fill tha array of ways delete features ids on the application startup
		pool.query('SELECT * FROM user_data where id = ($1)',[request.body.user_id], returnResult);
	} else if (mode == 'update'){	//update is used to fill the array with ways features that are not drawned by the user	
		pool.query('UPDATE user_data SET deleted_feature_ids=($2) WHERE id=($1)',[request.body.user_id,request.body.deleted_feature_ids],returnResult);
	} else if (mode == 'delete'){  //delete is used to delete the feature from ways_modified table if the user has drawned that feature by himself
		pool.query('DELETE FROM ways_modified WHERE id=($1)',[request.body.drawned_fid],returnResult); 
		//*later we can require guid (unique id) for security here, for the user to be able to delete the feature and use a nodejs library to prevent sql incjection attacks*//
	} else if (mode == 'insert' ){
		pool.query('INSERT INTO user_data (generated_id) VALUES ($1)',[request.body.generated_id],returnResult);	
	}
	
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
