Telegram Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/telegram.svg)

This project defines one API Gateway called ``telegramexampleapi``and connects one
lambda written in javascript called ``javascript_bot`` with the ``/my-js-bot-webhook`` url.

In order to create your bot, you'll need to follow the steps described in the [Telegram Bots:An introduction for developers](https://core.telegram.org/bots) page.

As a ``tl;dr`` version, you can follow this:
* Install Telegram and open [Botfather](https://telegram.me/botfather).
* Type ``/newbot`` and answer the questions. At the end it will give you a token like:
  * ``12345678:AAAAAAAAAAAAAAAAAAAAAAAAAAAA``.
* Add that token to ``Token`` in ``parameters/dev.yml``.
* Run ``$ gordon build && gordon apply`` and copy the url of your service.
* After replacing $URL and $TOKEN run the following command in order to tell Telegram which is your webhook url:
  * ``curl -F "url=$URL" https://api.telegram.org/bot$TOKEN/setWebhook``
  * i.e ``curl -F "url=https://xxxxxxx.execute-api.us-east-1.amazonaws.com/dev/my-js-bot-webhook" https://api.telegram.org/bot12345678:AAAAAAAAAAAAAAAAAAAAAAAAAAAA/setWebhook``


Your lambda will be called every time somebody talks to your bot.

The bot is not very clever, and only replies saying ``Hello from gordon!``


Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [APIGateway](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/apigateway.html)
 * [Telegram API](https://core.telegram.org/)
