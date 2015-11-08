Gordon
=========

Gordon is a high-level framework which allows you to create, wire and deploy AWS Lambdas in an easy way.

Why?
------  
In an ideal world, this project should not exits. AWS Lambdas (as any other AWS resource) should be provisioned using CloudFormation - One of the best advantages of using AWS is not it's scalability nor the fancy services... ain't the price; It is the fact that reproducibility is at it's core and their ecosystem is full of services which encourage/enforce it. Their flagship is CloudFormation.

Then... why not use CloudFormation? Well, there are two reasons: First, not all AWS APIs are released when services are announced... ain't frameworks (boto3), ain't their integration with CloudFormation. You could wait for them to get released... but ain't nobody got time for that!

The second reason is complexity. CloudFormation stacks are defined using JSON templates which are a nightmare to write and maintain.

This project tries to solve these two issues by working around the lack of CloudFormation/Framework APIs (keeping in mind they will happen eventually) and trying to create a high level abstraction on top of CloudFormation so people without a deep understanding of it can write and deploy lambdas without shooting their foot.


Why should you use this project?
-----------------------------------
Because eventually you'll stop using it -ish. Once CloudFormation supports 100% of the AWS Lambda API, this project will be a really thin layer of sugar around the fact that writing CloudFormation templates sucks and some conventions around how to structure a project using Lambdas... and not much more, which is great!


How it works
-------------
It is easy - we want as much as possible to happen on CloudFormation, so every single thing which could be done with it... will be done with it. Any other resource or integration will be done as part of a pre or post script, before the stack is applied or after it succeeds.

You should not worry about what happens where and you should focus of developing whatever your product is. As soon as new APIs are released or CloudFormation get's new fancy stuff we'll do as much as possible to reduce the bolierplate.
