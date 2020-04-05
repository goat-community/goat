const express = require("express");
const pool = require("./db");
const app = express();
const GeoJSON = require("geojson");
const cors = require("cors");
const bodyParser = require("body-parser");
// use it before all route definitions
app.use(cors({ origin: "*" }));
app.use(function(request, response, next) {
  response.header("Access-Control-Allow-Origin", "*");
  response.header(
    "Access-Control-Allow-Methods",
    "POST, GET, PUT, DELETE, OPTIONS"
  );
  response.header("Access-Control-Allow-Credentials", "false");
  response.header("Access-Control-Max-Age", "86400"); // 24 hours
  if (request.method == "OPTIONS") {
    response.status(204).end();
  } else {
    next();
  }
});

var jsonParser = bodyParser.json();
// to support JSON-encoded bodies
var urlencodedParser = bodyParser.urlencoded({ extended: false });

app.post("/api/userdata", jsonParser, (request, response) => {
  //CRUD OPERATION
  var mode = request.body.mode;
  function returnResult(err, res) {
    if (err) return console.log(err);
    response.send(res.rows);
  }
  if (mode == "read") {
    //read is used to fill tha array of delete features ids on the application startup
    pool.query(
      "SELECT * FROM user_data where userid = ($1) AND layer_name = ($2)",
      [request.body.user_id, request.body.layer_name],
      returnResult
    );
  } else if (mode == "update") {
    //update is used to fill the array with features that are not drawn by the user
    pool.query(
      "UPDATE user_data SET deleted_feature_ids=($2) WHERE userid=($1) AND  layer_name=($3)",
      [
        request.body.user_id,
        request.body.deleted_feature_ids,
        request.body.layer_name
      ],
      returnResult
    );
  } else if (mode == "delete") {
    //delete is used to delete the feature from modified table if the user has drawn that feature by himself
    pool.query(
      `DELETE FROM ${request.body.layer_name}_modified WHERE userid=($1) AND original_id = ANY(($2));`,
      [
        request.body.user_id,
        request.body.deleted_feature_ids,
      ]
    );
    pool.query(
      `DELETE FROM ${request.body.layer_name}_modified WHERE id=($1)`,
      [
        request.body.drawned_fid
      ],
      returnResult
    );
    //*later we can require guid (unique id) for security here, for the user to be able to delete the feature and use a nodejs library to prevent sql incjection attacks*//
  } else if (mode == "insert") {
    pool.query(
      "INSERT INTO user_data (userid, layer_name) VALUES ($1,$2)",
      [request.body.user_id, request.body.layer_name],
      returnResult
    );
  }
});

/**
 * Deletes all the rows of the user from "_modified" and "user_data" table
 */
app.post(
  "/api/deleteAllScenarioData",
  jsonParser,
  async (request, response) => {
    const layerNames = request.body.layer_names;
    const userId = request.body.user_id;
    try {
      //1- Delete from user_data first
      await pool.query(
        `UPDATE user_data SET deleted_feature_ids='{}' WHERE userid=${userId}`,
        []
      );

      //2- Delete from every layer modified table
      for (const layerName of layerNames) {
        await pool.query(
          `DELETE FROM ${layerName}_modified WHERE userid=${userId};`,
          []
        );
      }

      //3- Rerun upload to reflect the changes.
      await pool.query(`select * from network_modification(${userId})`);

      response.send("success");
    } catch (err) {
      console.log(err.stack);
      response.send("error");
    }
  }
);

app.post("/api/isochrone", jsonParser, (request, response) => {
  let requiredParams = [
    "user_id",
    "minutes",
    "x",
    "y",
    "n",
    "speed",
    "concavity",
    "modus",
    "routing_profile"
  ];
  let queryValues = [];

  requiredParams.forEach(key => {
    let value = request.body[key];
    if (!value) {
      response.send("An error happened");
      return;
    }
    queryValues.push(value);
  });

  console.log(queryValues);
  // Make sure to set the correct content type
  response.set("content-type", "application/json");

  pool.query(
    `SELECT jsonb_build_object(
		'type',     'FeatureCollection',
		'features', jsonb_agg(features.feature)
	)
	FROM (
	SELECT jsonb_build_object(
		'type',       'Feature',
		'id',         gid,
		'geometry',   ST_AsGeoJSON(geom)::jsonb,
		'properties', to_jsonb(inputs) - 'gid' - 'geom'
	) AS feature 
	FROM (SELECT * FROM isochrones_api($1,$2,$3,$4,$5,$6,$7,$8,$9,NULL,NULL,NULL)) inputs) features;`,
    queryValues,
    (err, res) => {
      if (err) return console.log(err);
      console.log(res);
      response.send(res.rows[0].jsonb_build_object);
    }
  );
});

app.post("/api/pois_multi_isochrones", jsonParser, (request, response) => {
  let requiredParams = [
    "user_id",
    "minutes",
    "speed",
    "n",
    "routing_profile",
    "alphashape_parameter",
    "modus",
    "region_type",
    "region",
    "amenities"
  ];
  let queryValues = [];

  requiredParams.forEach(key => {
    let value = request.body[key];
    console.log(value);
    if (!value) {
      response.send("An error happened");
      return;
    }
    queryValues.push(value);
  });

  console.log(queryValues);
  // Make sure to set the correct content type

  response.set("content-type", "application/json");
  const sqlQuery = `SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(features.feature)
  )
  FROM (
  SELECT jsonb_build_object(
    'type',       'Feature',
    'id',         gid,
    'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'gid' - 'geom'
  ) AS feature 
  FROM (SELECT * FROM multi_isochrones_api(${queryValues[0]},${queryValues[1]},${queryValues[2]},${queryValues[3]},${queryValues[4]},${queryValues[5]},${queryValues[6]},${queryValues[7]},ARRAY[${queryValues[8]}],ARRAY[${queryValues[9]}])) inputs) features;`;
  console.log(sqlQuery);
  pool.query(sqlQuery, (err, res) => {
    if (err) return console.log(err);
    response.send(res.rows[0].jsonb_build_object);
  });
});

app.post(
  "/api/count_pois_multi_isochrones",
  jsonParser,
  (request, response) => {
    let requiredParams = [
      "user_id",
      "modus",
      "minutes",
      "speed",
      "region_type",
      "region",
      "amenities"
    ];
    let queryValues = [];
    requiredParams.forEach(key => {
      let value = request.body[key];
      console.log(value);
      if (!value) {
        response.send("An error happened");
        return;
      }
      queryValues.push(value);
    });

    console.log(queryValues);
    // Make sure to set the correct content type

    response.set("content-type", "application/json");
    const sqlQuery = `
  SELECT jsonb_build_object(
    'type',       'Feature',
    'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'geom'
  ) AS feature 
  FROM (SELECT count_pois,region_name, geom FROM count_pois_multi_isochrones(${queryValues[0]},${queryValues[1]},${queryValues[2]},${queryValues[3]},${queryValues[4]},ARRAY[${queryValues[5]}],ARRAY[${queryValues[6]}])) inputs;`;
    pool.query(sqlQuery, (err, res) => {
      if (err) return console.log(err);
      console.log(res);
      response.send(res.rows[0]);
    });
  }
);

// respond with "pong" when a GET request is made to /ping (HEALTHCHECK)
app.get("/ping", function(_req, res) {
  res.send("pong");
});

module.exports = app;
