import json

def handler(event, context):
    print "party"
    print("Received event: " + json.dumps(event, indent=2))
