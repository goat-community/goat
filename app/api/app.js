const express = require("express");
const pool = require("./db");
const app = express();
const GeoJSON = require("geojson");
const cors = require("cors");
const bodyParser = require("body-parser");
// use it before all route definitions
app.use(cors({ origin: "*" }));
app.use(function (request, response, next) {
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
  /*sample body: {"mode":"insert"}*/
  if (mode == "insert") {
    pool.query(
      "INSERT INTO user_data (username, pw) VALUES ('','') RETURNING userid",
      returnResult
    );
  } else if (mode == "delete") {
    /*sample body: {"mode":"delete", "userid":1}*/
    pool.query("DELETE FROM user_data WHERE userid = $1::bigint", [
      request.body.userid,
    ]);
  }
});

app.post("/api/scenarios", jsonParser, (request, response) => {
  var mode = request.body.mode;

  function returnResult(err, res) {
    if (err) return console.log(err);
    response.send(res.rows);
  }
  const translation_layers = {
    ways: "deleted_ways",
    pois: "deleted_pois",
    buildings: "deleted_buildings",
  };

  if (mode == "read_deleted_features") {
    /*sample body: {"mode":"read_deleted_feature","table_name":"pois" ,"scenario_id":"1" */
    pool.query(
      `SELECT ${
        translation_layers[request.body.table_name]
      } AS deleted_feature_ids FROM scenarios WHERE scenario_id = $1::bigint`,
      [request.body.scenario_id],
      returnResult
    );
  } else if (mode === "update_deleted_features") {
    /*sample body: {"mode":"update_deleted_feature","deleted_feature_ids":[2,3,4],"table_name":"pois" ,"scenario_id":"1" */

    pool.query(
      `UPDATE scenarios SET ${
        translation_layers[request.body.table_name]
      } = $1::bigint[] WHERE scenario_id = $2::bigint`,
      [request.body.deleted_feature_ids, request.body.scenario_id],
      returnResult
    );
  } else if (mode === "delete_feature") {
    //delete is used to delete the feature from modified table if the user has drawn that feature by himself
    pool.query(
      `DELETE FROM ${request.body.table_name}_modified WHERE scenario_id = $1::bigint AND original_id = ANY(($2));`,
      [request.body.scenario_id, request.body.deleted_feature_ids]
    );
    pool.query(
      `DELETE FROM ${request.body.table_name}_modified WHERE gid=($1)`,
      [request.body.drawned_fid],
      returnResult
    );
  } else if (mode == "insert") {
    /*sample body: {mode:"insert","userid":1}*/
    pool.query(
      "INSERT INTO scenarios (userid, scenario_name) VALUES ($1, $2) RETURNING scenario_id",
      [request.body.userid, request.body.scenario_name],
      returnResult
    );
  } else if (mode == "delete") {
    /*sample body: {mode:"delete","scenario_id":1}*/
    pool.query(
      "DELETE FROM scenarios WHERE scenario_id = $1::bigint",
      [request.body.scenario_id],
      returnResult
    );
  } else if (mode === "update_scenario") {
    pool.query(
      "UPDATE scenarios SET scenario_name = $1 WHERE scenario_id = $2::bigint",
      [request.body.scenario_name, request.body.scenario_id],
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
    const scenarioId = request.body.scenario_id;
    try {
      //1- Delete from scenario first
      await pool.query(
        `DELETE FROM scenarios WHERE scenario_id=${scenarioId}`,
        []
      );

      //2- Rerun upload for ways to reflect the changes.
      await pool.query(`SELECT * FROM network_modification(${scenarioId})`);

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
    "scenario_id",
    "minutes",
    "x",
    "y",
    "n",
    "speed",
    "concavity",
    "modus",
    "routing_profile",
  ];
  let queryValues = [];

  requiredParams.forEach((key) => {
    let value = request.body[key];
    console.log(value);
    if (!request.body.hasOwnProperty(key)) {
      response.send("An error happened");
      return;
    }
    queryValues.push(value);
  });

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
	FROM (SELECT * FROM isochrones_api($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,NULL,NULL,NULL)) inputs) features;`,
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
    "scenario_id",
    "minutes",
    "speed",
    "n",
    "routing_profile",
    "alphashape_parameter",
    "modus",
    "region_type",
    "region",
    "amenities",
  ];
  let queryValues = [];
  requiredParams.forEach((key) => {
    let value = request.body[key];
    console.log(value);
    if (!request.body.hasOwnProperty(key)) {
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
  FROM (SELECT * FROM multi_isochrones_api(${queryValues[0]},${queryValues[1]},${queryValues[2]},${queryValues[3]},${queryValues[4]},${queryValues[5]},${queryValues[6]},${queryValues[7]},${queryValues[8]},ARRAY[${queryValues[9]}],ARRAY[${queryValues[10]}])) inputs) features;`;
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
      "scenario_id",
      "modus",
      "minutes",
      "speed",
      "region_type",
      "region",
      "amenities",
    ];
    let queryValues = [];
    requiredParams.forEach((key) => {
      let value = request.body[key];

      if (!value) {
        response.send("An error happened");
        return;
      }
      queryValues.push(value);
      console.log(value);
    });

    console.log(queryValues[1]);

    // Make sure to set the correct content type

    response.set("content-type", "application/json");
    const sqlQuery = `
  SELECT jsonb_build_object(
    'type',       'Feature',
    'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'geom'
  ) AS feature 
  FROM (SELECT count_pois,region_name, geom FROM count_pois_multi_isochrones(${queryValues[0]},${queryValues[1]},${queryValues[2]},${queryValues[3]},${queryValues[4]},${queryValues[5]},'${queryValues[6]}',ARRAY[${queryValues[7]}])) inputs;`;
    pool.query(sqlQuery, (err, res) => {
      if (err) return console.log(err);
      console.log(res);
      response.send(res.rows[0]);
    });
  }
);

app.post("/api/export_scenario", jsonParser, (request, response) => {
  const scenarioId = request.body.scenario_id;
  pool.query(
    `SELECT * FROM export_changeset_scenario(${scenarioId})`,
    (err, res) => {
      if (err) return console.log(err);
      const zipCompresser = new require("node-zip")();
      if (res.rows.length > 0 && res.rows[0].export_changeset_scenario) {
        const scenarioChangeset = res.rows[0].export_changeset_scenario;
        for (const layer in scenarioChangeset) {
          zipCompresser.file(
            `${layer}.geojson`,
            JSON.stringify(scenarioChangeset[layer])
          );
        }
      }
      const data = zipCompresser.generate({
        base64: false,
        compression: "DEFLATE",
      });
      response.type("zip");
      response.send(new Buffer.from(data, "binary"));
    }
  );
});

app.post("/api/import_scenario", jsonParser, (request, response) => {
  const { user_id, scenario_id, payload, layerName } = request.body;
  if (!user_id || !scenario_id || !payload || !layerName) {
    response.send(`An error happened. Missing parameters`);
  }
  console.log(payload);
  const sql = `SELECT import_changeset_scenario(${scenario_id}, ${user_id},jsonb_build_object('${layerName}',$$${JSON.stringify(
    payload
  )}$$::jsonb))`;
  console.log(sql);
  pool.query(sql, (err, res) => {
    if (err) return console.log(err);
    if (
      res.rows.length > 0 &&
      res.rows[0].import_changeset_scenario[layerName]
    ) {
      response.send(res.rows[0].import_changeset_scenario[layerName]);
    } else {
      response.send(0);
    }
  });
});

app.post("/api/upload_all_scenarios", jsonParser, async (request, response) => {
  const scenarioId = request.body.scenario_id;
  try {
    //1- Delete from scenario first
    await pool.query(`SELECT * FROM network_modification(${scenarioId});`, []);

    //2- Rerun upload for ways to reflect the changes.
    await pool.query(`SELECT * FROM population_modification(${scenarioId});`);

    response.send("success");
  } catch (err) {
    console.log(err.stack);
    response.send("error");
  }
});

// respond with "pong" when a GET request is made to /ping (HEALTHCHECK)
app.get("/ping", function (_req, res) {
  res.send("pong");
});

module.exports = app;
