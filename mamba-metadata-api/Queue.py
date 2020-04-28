import boto3
import json
from boto3.dynamodb.conditions import Attr
from random import sample
from random import randint

# this is for queuing the songs
dynamo = boto3.resource('dynamodb')
table = dynamo.Table('songs')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }


def get(payload):
    response = table.scan(
        Select = 'SPECIFIC_ATTRIBUTES',
        FilterExpression = Attr('artist').eq(payload['artist']),
        ProjectionExpression = 'SongId, title, artist'
    )
    items = response['Items']
    try:
        ids = sample(range(0, len(items)), 5)
    except ValueError:
        ids = [randint(0, len(items)-1) for i in range(5)]
    
    result = list(map(lambda x: items[x], ids))
    data = {'ids': result}

    return respond(None, data)


def lambda_handler(event, context):
    print(event)
    operation = event['httpMethod']

    if operation == 'GET':
        payload = event['queryStringParameters']
        if not ('CustomerId' and 'artist' in payload):
            return respond('ParametersUnspecified')
        else:
            return get(payload)
    else:
        return respond('Unsupported method "{}"'.format(operation))

