import json
from cfnresponse import send, SUCCESS


def handler(event, context):
    print("Received Event: " + json.dumps(event, indent=2))

    if event['RequestType'] == 'Delete':
        # Implement Delete Operation
        send(event, context, SUCCESS)
        return

    if event['RequestType'] == 'Update':
        # Implement Update Operation
        pass

    if event['RequestType'] == 'Create':
        # Implement Create Operation
        pass

    # You'll be able to use Fn::GetAtt to query values returned as part
    # of the response_data dictionary.
    # "Fn::GetAtt": [
    #      "YouResource",
    #      "SomeProperty"
    # ]
    send(event, context, SUCCESS, response_data={'SomeProperty': "12345"})
