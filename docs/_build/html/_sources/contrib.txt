gordon.contrib
=================

When using gordon, you'll quickly see ``contrib`` apps take an important role while
deploying and wiring your lambdas.

Gordon uses ``CloudFormation`` a lot. It is a great AWS service, but it's API doesn't
always include the latest services AWS is releasing almost every week! These services
will eventually make it into ``CloudFormation``, but in the meantime we need to use
low-level APIs to interact with them.

We could (as some other projects) decide to fill the gaps streaming API commands...
but we decided to do things differently.

We believe ``CloudFormation`` is the way to move forward, and the advantages it provides
surpass some of the gotchas, so we decided to fill the gaps using Lambdas and custom
``CloudFormation`` resources.

But... how could you use Lambdas and ``CloudFormation`` to create Lambdas in ``CloudFormation``?

Easy - eating your own dog food; That's ``gordon.contrib``!

``gordon.contrib`` is a set of reusable gordon applications your gordon projects use to
be able to deploy your resources and fill the gaps in ``CloudFormation`` until AWS fills them.


When will AWS allow us to create those resources "natively"?
--------------------------------------------------------------

We have no idea, but we have make a big effort trying to make our Custom ``CloudFormation``
resources look as similar as possible to what we think those resources will look like. Once
AWS releases those APIs in ``CloudFormation``, subsequent versions of gordon will stop
using our lambda-based Resources and use native ones.


Available ``contrib`` apps
---------------------------

``contrib.lambdas``
^^^^^^^^^^^^^^^^^^^^^^^^

This application exposes two ``CloudFormation`` resources:

    * **version**: Creates Versions for our lambda functions. Nothing super fancy under the hood: https://github.com/jorgebastida/gordon/blob/master/gordon/contrib/lambdas/version/version.py


``contrib.s3``
^^^^^^^^^^^^^^^^^^^^^^^^

This application exposes one ``CloudFormation`` resource:

    * **bucket_notification_configuration**: This resource allows us to manage S3 bucket notifications. This is a complex resource because the API AWS has develop around... it is not very nice (imho). You can see more details here: https://github.com/jorgebastida/gordon/blob/master/gordon/contrib/s3/bucket_notification_configuration/bucket_notification_configuration.py


``contrib.helpers``
^^^^^^^^^^^^^^^^^^^^^^^^

This application exposes one simple ``CloudFormation`` resource called ``Sleep``. Yes, this is lame ``¯\_(ツ)_/¯`` but
it was the only possible way to make resilient integrations with streams such as ``kinesis`` and ``dynamodb``.

This is because the IAM role of the lambda is not propagated fast enough uppon creation, and ``CloudFormation`` checks
if the referenced lambda has permission to consume this stream on creation time. A small sleep fixes the problem. We
will probably try fix this in the future with a generic ``make-sure-this-is-ready`` lambda.
