const { Pool } = require("pg");

const user = process.env.POSTGRES_USER;
const host = process.env.POSTGRES_HOST;
const database = process.env.POSTGRES_DBNAME;
const password = process.env.POSTGRES_PASS;
const port = process.env.POSTGRES_PORT;

const pool = new Pool({ user, host, database, password, port });

module.exports = pool;
