import json
print('Loading function')

with open('.context', 'r') as f:
    context = json.loads(f.read())


def handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    print("value1 = " + event['key1'])
    print("value2 = " + event['key2'])
    print("value3 = " + event['key6'])
    return context['c']  # Echo back the first key value
    # raise Exception('Something went wrong')
