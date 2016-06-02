Slack Slash command example
==============================

This project defines one API Gateway called ``slackexampleapi`` and connects one
lambda written in python called ``python_bot`` with the ``/my-python-bot-webhook`` url.

If you configure a new slash command in your slack account to invoque this endpoint, you'll get something similar like this:

![slack](http://gordon.readthedocs.io/en/latest/_static/examples/slack_demo.png)

In order to create your slash command in Slack, you'll need to follow a few steps:

* Open ``https://<your-team-domain>.slack.com/services/new`` and search for "Slash Commands".
* Enter a name for your command and click "Add Slash Command Integration".
* Copy the token string and add it to ``Token`` in ``parameters/dev.yml``.
* Now you can deploy your bot doing ``$ gordon build`` and ``$ gordon apply``
* Copy the ``ApigatewaySlackexampleapi`` URL, and add it to Slack integration configuration page in the URL field.
* Done! You should be able to use your slash command.

Documentation relevant to this example:
 * [Lambdas](http://gordon.readthedocs.io/en/latest/lambdas.html)
 * [APIGateway](http://gordon.readthedocs.io/en/latest/eventsources/apigateway.html)
 * [Slack Outgoing Webhooks](https://api.slack.com/outgoing-webhooks)
 * [Slack Icomming Webhooks](https://api.slack.com/incoming-webhooks)
 * [Slack Slash Commands](https://api.slack.com/slash-commands)
