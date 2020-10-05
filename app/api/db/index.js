const { Pool } = require("pg");

const user = "goat"//process.env.POSTGRES_USER;
const host = "localhost"//process.env.POSTGRES_HOST;
const database = "goat"//process.env.POSTGRES_DBNAME;
const password = "earlmanigault"//process.env.POSTGRES_PASS;
const port = 65432//process.env.POSTGRES_PORT;

const pool = new Pool({ user, host, database, password, port });

module.exports = pool;
