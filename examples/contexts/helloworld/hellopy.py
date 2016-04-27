import json

print('Loading function')

#
# Read context form .context
#
with open('.context', 'r') as f:
    gordon_context = json.loads(f.read())


def handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    print("value1 = " + event['key1'])
    print("value2 = " + event['key2'])
    print("value3 = " + event['key3'])
    print("CONTEXT = " + unicode(gordon_context))
    return gordon_context['c']  # Return back the c key of the
    # raise Exception('Something went wrong')
