Running lambdas locally
==========================

While developing lambdas it is quite useful to be able to run lambdas locally and see how they behave when receiving certain events.
This should not be consider a replacement for writing tests - You should write tests for your code!

In order to locally invoke your lambdas you can do so by running:

.. code-block:: bash

    $ echo '{... JSON ...}' | gordon run APP.LAMBDA


Gordon expects ``stdin`` to be the json formated event your lambda will receive. It is important to note that your lambda will
be executed after collecting all resources and applying the full ``build`` process, so you can expect dependencies to be available.

Python lambdas
----------------

Python lambdas don't require any specific setup, but you should keep in mind the limitations of of the mock ``LambdaContext`` object that gordon
uses as second argument of your lambda. You can find the current implementation `Python Loader <https://github.com/jorgebastida/gordon/blob/master/gordon/loaders/python.py>`_.

We'll try to make this mock more clever overtime. PR Welcome!


Node Lambdas
--------------------

Node lambdas don't require any specific setup, but you should keep in mind the limitations of of the mock ``LambdaContext`` object that gordon
uses as second argument of your lambda. You can find the current implementation `Node Loader <https://github.com/jorgebastida/gordon/blob/master/gordon/loaders/node.js>`_.

We'll try to make this mock more clever overtime. PR Welcome!


Java Lambdas
---------------

Java lambdas require you to write a new constructor which accepts a ``String`` as the first argument and ``Context`` as second.

.. code-block:: java


    package example;

    import com.amazonaws.services.lambda.runtime.Context;
    import org.json.JSONObject;


    public class Hello {

        public static class EventClass {

            ...

            public EventClass(String key1, String key2, String key3) {
                this.key1 = key1;
                this.key2 = key2;
                this.key3 = key3;
            }

        }

        public String handler(EventClass event, Context context) {
            System.out.println("value1 = " + event.key1);
            System.out.println("value2 = " + event.key2);
            System.out.println("value3 = " + event.key3);
            return String.format(event.key1);
        }

        public String handler(String json_event, Context context) {
            JSONObject event_data = new JSONObject(json_event);
            EventClass event = new EventClass(
                event_data.getString("key1"),
                event_data.getString("key2"),
                event_data.getString("key3")
            );
            return this.handler(event, context);
        }

    }


As you can see we have defined a constructor with the following signature ``public String handler(String json_event, Context context)`` which
calls our lambda handler after creating a ``EventClass`` instance using the data from the json in ``json_event``.

In a similar way than Python and Javascript lambdas you should keep in mind the limitations of of the ``MockContext`` object that gordon
uses as second argument of your lambda. You can find the current implementation `Java Loader <https://github.com/jorgebastida/gordon/blob/master/gordon/loaders/java/src/main/java/gordon/GordonLoader.java>`_.

We'll try to make this mock more clever overtime. PR Welcome!
