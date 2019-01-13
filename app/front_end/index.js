////////REVERSE PROXY///////
var host = process.env.HOST || '0.0.0.0';
// Listen on a specific port via the PORT environment variable
var port = process.env.PORT || 9090;

const proxy = require('http-proxy-middleware')
const Bundler = require('parcel-bundler');
const express = require('express');
let bundler = new Bundler('./index.html');
let app = express();

var geoserverProxy =  proxy({target: 'http://localhost:8080',changeOrigin: true});
var nodeProxy =  proxy({target: 'http://localhost:3000',changeOrigin: true});

app.use('/geoserver',geoserverProxy);
app.use('/node',nodeProxy);
app.use('/markers', express.static('markers'));
app.use(express.static('css'));
app.use(express.static('lib'))
app.use(bundler.middleware());
app.listen(8585);