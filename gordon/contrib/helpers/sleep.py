import time
import json

from cfnresponse import send, SUCCESS

def handler(event, context):
    if event['RequestType'] == 'Delete':
        send(event, context, SUCCESS)
        return
    time.sleep(int(event['ResourceProperties']['Time']))
    send(event, context, SUCCESS)
