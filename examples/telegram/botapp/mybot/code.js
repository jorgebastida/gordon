var TelegramBot = require('node-telegram-bot-api');

var gordon_context = JSON.parse(require('fs').readFileSync('.context', 'utf8'));

exports.handler = function(event, context) {
    console.log("Request received:\n", JSON.stringify(event));
    console.log("Context received:\n", JSON.stringify(context));

    var bot = new TelegramBot(gordon_context['token']);
    bot.sendMessage(event.message.from.id, "Hello from gordon!");
}
