Golang Example
===========================

This project defines one lambda called ``helloworld`` which is programed using Golang.

Yes, Golang is not one of the supported runtimes by AWS, but we wrap the binary file
around a Javascript launcher.

Then, we only need to customize the ``build`` process of our lambda in order to compile
the Go source code, and... done!

Documentation relevant to this example:
 * [Lambdas](https://gordon.readthedocs.io/en/latest/lambdas.html)
