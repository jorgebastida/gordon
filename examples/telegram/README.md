Telegram Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/telegram.svg)

This project defines one API Gateway called ``telegramexampleapi``and connects one
lambda written in javascript called ``javascript_webhook`` with the ``/my-js-bot-webhook`` url.

You can now point your Telegram bot webhook to your API url, and it will be called
every time somebody talks to it. The bot is not very clever, and only replies saying
that it agrees with you.

Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [APIGateway](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/apigateway.html)
 * [Telegram API](https://core.telegram.org/)

How to deploy it?
------------------

* ``$ gordon build``
* ``$ gordon apply``
