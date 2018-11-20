////////REVERSE PROXY///////
var host = process.env.HOST || '0.0.0.0';
// Listen on a specific port via the PORT environment variable
var port = process.env.PORT || 9090;

 
var cors_proxy = require('cors-anywhere');
cors_proxy.createServer({
    originWhitelist: [], // Allow all origins
    requireHeader: ['origin', 'x-requested-with'],
    removeHeaders: ['cookie', 'cookie2']
}).listen(port, host, function() {
    console.log('Running CORS Anywhere on ' + host + ':' + port);
});

////////APP///////
const Bundler = require('parcel-bundler');
const express = require('express');

let bundler = new Bundler('./index.html');
let app = express();




app.use(bundler.middleware());
app.listen(8585);