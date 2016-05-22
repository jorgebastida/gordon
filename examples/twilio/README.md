Twilio Example
===========================

![gordon](http://gordondoc.s3-website-eu-west-1.amazonaws.com/_static/examples/twilio.svg)

This project defines one API Gateway called ``twilioexample``and connects one
lambda written in python called ``helloworld`` with the ``/`` url.

This Lambda returns one super-simple ``TWIML`` response that will make your twilio phone
number reply to any call saying ``Hello, this is Twilio powered by Gordon!``.

Once you have deployed this project, you'll need to configure your phone number:
* Go to [Manage Phone Numbers](https://www.twilio.com/console/phone-numbers/)
* Click on the number you want to configure, and in the ``A CALL COMES IN`` select ``Webhook`` and add as value the url of your API Gateway.
* Save the changes and call your number!


Documentation relevant to this example:
 * [Lambdas](http://gordondoc.s3-website-eu-west-1.amazonaws.com/lambdas.html)
 * [APIGateway](http://gordondoc.s3-website-eu-west-1.amazonaws.com/eventsources/apigateway.html)
 * [TWIML Reference](https://www.twilio.com/docs/api/twiml)
