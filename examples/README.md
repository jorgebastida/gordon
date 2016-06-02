Gordon Examples
==================

Here you have quite a broad collection of working examples.

Most (if not) all of them can be deployed to your AWS account by simply running:

* ``$ gordon build``
* ``$ gordon apply``

Some of them like ``dynamodb``, ``kinesis`` and ``s3`` require you to configure
the source stream/bucket to be one that you own, obviously.

AWS Resource Notes
------------------

* Ensure your S3 bucket name is globally unique, not just to your account.
  See [S3 bucket documentation](http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html) for details.
