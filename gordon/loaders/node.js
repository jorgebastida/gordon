// Mock LambdaContext event
function LambdaContext(functionName, memoryLimitInMB, timeout){
    this.functionName = functionName;
    this.memoryLimitInMB = memoryLimitInMB;
    this.timeout = timeout;
    this.callbackWaitsForEmptyEventLoop = true;
    this.functionVersion = 'current';
    this.awsRequestId = 'awsRequestId';
    this.logGroupName = 'logGroupName';
    this.logStreamName = 'logStreamName';
    this.identity = null;
    this.clientContext = null;
    this.invokedFunctionArn = 'invoked_function_arn';

    var date = new Date();
    this.startTime = date.getTime();
}

LambdaContext.prototype.getRemainingTimeInMillis = function() {
    var date = new Date();
    return Math.max(this.timeout * 1000 - parseInt(date.getTime() - this.startTime), 0);
}

LambdaContext.prototype.succeed = function(message) {
    console.log("output: " + message);
}

LambdaContext.prototype.fail = function(error) {
    console.log("fail: " + error);
}

// This language needs more love
String.prototype.rsplit = function(sep, maxsplit) {
    var split = this.split(sep);
    return maxsplit ? [ split.slice(0, -maxsplit).join(sep) ].concat(split.slice(-maxsplit)) : split;
}

// Capture stdin before converting it into json
var stdin = process.stdin,
    stdout = process.stdout,
    inputChunks = [];

stdin.resume();
stdin.setEncoding('utf8');

stdin.on('data', function (chunk) {
    inputChunks.push(chunk);
});

// Once the stdin has finished, process it as JSON, load the
// the user module and invoque it.
stdin.on('end', function () {

    var inputJSON = inputChunks.join(),
        eventData = JSON.parse(inputJSON),
        handler_elements = process.argv[2].rsplit('.', 1),
        context = new LambdaContext(process.argv[4], process.argv[5], process.argv[6]),
        module = require('./' + handler_elements[0] + '.js');

    module[handler_elements[1]](eventData, context);

});
