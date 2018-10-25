const express = require('express');
const pool = require('./db');
const app = express();
const GeoJSON = require('geojson')
const cors = require('cors');
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




app.post('/userdata',jsonParser, (request,response) => {
	//CRUD OPERATION
	var mode = request.body.mode;
	function returnResult (err,res){
		if (err) return console.log(err);
			   response.send(res.rows);
	}
	if (mode == 'read'){
		pool.query('SELECT * FROM user_data where id = ($1)',[request.body.id], returnResult);
	} else if (mode == 'update'){
		console.log(request.body.deleted_feature_ids);		
		pool.query('UPDATE user_data SET deleted_feature_ids=($2) WHERE id=($1)',[request.body.id,request.body.deleted_feature_ids],returnResult);
	}
	
});




module.exports = app;