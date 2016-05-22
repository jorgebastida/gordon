console.log('Loading function');

var gordon_context = JSON.parse(require('fs').readFileSync('.context', 'utf8'));

exports.handler = function(event, context) {
    console.log(JSON.stringify(gordon_context));
    context.succeed(gordon_context['bucket']);

};
