import time
import urllib2

import json

SUCCESS = "SUCCESS"
FAILED = "FAILED"

def send(event, context, responseStatus, responseData=None, physicalResourceId=None):
    responseData = responseData or {}
    response_body = json.dumps(
        {
            'Status': responseStatus,
            'Reason': "See the details in CloudWatch Log Stream: " + context.log_stream_name,
            'PhysicalResourceId': physicalResourceId or context.log_stream_name,
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            'Data': responseData
        }
    )

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(event['ResponseURL'], data=response_body)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(response_body))
    request.get_method = lambda: 'PUT'
    try:
        response = opener.open(request)
        print "Status code: ", response.getcode()
        print "Status message: ", response.msg
        return True
    except urllib2.HTTPError, exc:
        print "Failed executing HTTP request: ", exc.code
        return False
