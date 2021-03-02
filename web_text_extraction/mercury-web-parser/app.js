const express = require('express') ;
const app = express() ;
const port = 8888  ;
app.get('/myapp/', function (req, res) {
    const Mercury = require('@postlight/mercury-parser');
    const url = req.query.url;
    console.log('Request for: ' + url);
    Mercury.parse(url).then(result => {  res.send(result);  } );  })
app.listen(port)
