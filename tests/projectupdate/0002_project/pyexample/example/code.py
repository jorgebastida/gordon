def handler(event, context):
    print("value2 = " + event['key2'])
    return event['key2']
