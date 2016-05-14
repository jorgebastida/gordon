import json


def handler(event, context):
    data = "Hello World!"
    print(data)
    print("Received Event: " + json.dumps(event, indent=2))
    return data
