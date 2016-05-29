'use strict';
let exec = require('child_process').exec;

exports.handler = (event, context) => {
    const child = exec("./code_go_compiled", (error) => {
        context.succeed(error, 'Process complete!');
    });
    child.stdout.on('data', console.log);
    child.stderr.on('data', console.error);
};
