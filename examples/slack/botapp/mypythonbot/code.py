import json
from urlparse import parse_qs


def handler(event, context):

    with open('.context', 'r') as f:
        gordon_context = json.loads(f.read())

    expected_token = gordon_context['token']

    req_body = event['body']
    params = parse_qs(req_body)

    # Check if the token is the correct one
    token = params['token'][0]
    if token != expected_token:
        raise Exception("Invalid request token")

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    command_text = params['text'][0]

    response = {
        'response_type': 'in_channel',
        'text': "Hello {}! you invoked {} while you were in {} with the following text: {}".format(user, command, channel, command_text),
        "attachments": [
            {
                "text": "This is some extra information!"
            }
        ]
    }
    return response
