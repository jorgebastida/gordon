Running lambdas in AWS
==========================

Once you have deployed your lambdas to AWS, it might me interesting for you to run them
from your command line. After running ``$ gordon apply``, you'll get the full arn of each
of the lambdas you deployed.

In order to do so, you can use the official ``aws-cli`` tool

.. code-block:: bash

    $ aws lambda invoke \
    --function-name $ARN \
    --log-type Tail \
    --payload '{"key1":"value1", "key2":"value2", "key3":"value3"}' \
    output.txt \
    | jq -r .LogResult | base64 --decode


As you can see we use ``jq`` in order to slice the output JSON and ``base64`` to decode it.
