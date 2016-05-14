// RIPOFF example from:
//    https://snowulf.com/2015/08/28/tutorial-poc-telegram-bot-running-in-aws-lambda/
// TODO: Simplify this example using a telegram library

console.log('Loading event');
var AWS = require('aws-sdk');
var https = require('https');
var querystring = require('querystring');

var botAPIKey = '';

exports.handler = function(event, context) {
    // Log the basics, just in case
    console.log("Request received:\n", JSON.stringify(event));
    console.log("Context received:\n", JSON.stringify(context));

    // We're going to respond with the user's ID, reply to their message
    // and some text of our own.
    var post_data = querystring.stringify({
    	'chat_id': event.message.from.id,
    	'reply_to_message_id': event.message.message_id,
    	'text': "Hello " + event.message.from.first_name + " (aka " + event.message.from.username+"). I'm not very smart, but I agree with \""+event.message.text+"\". Good luck!"
    });

    // Build the post options
    var post_options = {
          hostname: 'api.telegram.org',
          port: 443,
          path: '/bot'+botAPIKey+'/sendMessage',
          method: 'POST',
          headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'Content-Length': post_data.length
          }
    };

    // Create the post request
    var body = '';
    var post_req = https.request(post_options, function(res) {
        res.setEncoding('utf8');

        // Save the returning data
        res.on('data', function (chunk) {
            console.log('Response: ' + chunk);
            body += chunk;
        });

        // Are we done yet?
        res.on('end', function() {
            console.log('Successfully processed HTTPS response');
            // If we know it's JSON, parse it
            if (res.headers['content-type'] === 'application/json') {
                body = JSON.parse(body);
            }

            // This tells Lambda that this script is done
            context.succeed(body);
        });
    });

    // Post the data
    console.log("write the post");
    post_req.write(post_data);
    post_req.end();

}
