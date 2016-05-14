exports.handler = function(event, context) {
    var data = "Hello World!";
    console.log(data);
    console.log('Received Event:', JSON.stringify(event, null, 2));
    context.succeed(data);
};
