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
    this.invokedFunctionArn = '';

    this.getRemainingTimeInMillis = function() {
        return 0;
    }

    this.succeed = function(message) {
        console.log(message);
    }
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
        eventData = JSON.parse(inputJSON);
        context = new LambdaContext(process.argv[4], process.argv[5], process.argv[6]),
        module = require('./' + process.argv[2] + '.js');
    module[process.argv[3]](eventData, context);
});
