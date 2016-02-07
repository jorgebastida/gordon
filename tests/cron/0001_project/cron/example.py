def handler(event, context):
    print("value1 = " + event['key1'])
    return event['key1']
