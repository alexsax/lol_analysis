var express = require('express');
var app = express();
var child_process = require('child_process');
child_process.exec('pip install -r ' + __dirname + "/requirements.txt",  function (error, stdout, stderr) {
		console.log("stdout: " + stdout)
		console.log("stderr: " + stderr)
		// Could do something here
	});

app.set('port', (process.env.PORT || 5000));

app.use(express.static(__dirname + '/public'));

// // views is directory for all template files
// app.set('views', __dirname + '/views');
// app.set('view engine', 'ejs');

app.get('/fetch_matches', function(request, response) {
	child_process.exec('python ' + __dirname + '/aggregation/get_latest_game.py', function (error, stdout, stderr) {
		console.log("stdout: " + stdout)
		console.log("stderr: " + stderr)
		// Could do something here
	});
  response.send(':)')
});

app.listen(app.get('port'), function() {
  console.log('Node app is running on port', app.get('port'));
});


