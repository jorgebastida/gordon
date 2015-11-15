import json

def handler(event, context):
    print "risky"
    print("Received event: " + json.dumps(event, indent=2))
