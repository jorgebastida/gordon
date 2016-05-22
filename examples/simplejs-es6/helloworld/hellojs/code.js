const HelloMessage = "Hello from ES6!"
console.log('Loading function');

exports.handler = function(event, context) {
    context.succeed(HelloMessage);
};
