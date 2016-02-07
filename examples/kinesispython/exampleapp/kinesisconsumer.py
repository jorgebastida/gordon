import json


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    print("Received context: " + json.dumps(context, indent=2))
