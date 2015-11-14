import time
import json

from cfnresponse import send, SUCCESS

def handler(event, context):
    if event['RequestType'] == 'Delete':
        send(event, context, SUCCESS)
        return
    print("Received event: " + json.dumps(event, indent=2))
    time.sleep(5)
    send(event, context, SUCCESS)
