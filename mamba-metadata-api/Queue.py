import boto3
import json
from boto3.dynamodb.conditions import Attr, Key
from random import sample
from random import randint


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
    N = randint(0,3)
    
    curlist = recomendRand(payload['artist'], N)
    try:
        while len(curlist) < 10:
            x = items[randint(0, len(items) - 1)]
            flag = False
            for item in curlist:
                if x["SongId"] == item["SongId"]:
                    flag = True
            if not flag:
                curlist.append(x)
    except:
        pass
    
    data = {"ids" : [ {"SongId":x["SongId"], "title":x["title"], "artist":x["artist"]} for x in curlist]}
    return respond(False,data)
    

def recomendRand(artist, N):
    result = table.query(
        IndexName="artist-likes_ct-index-copy",
        KeyConditionExpression = Key('artist').eq(artist),
        ScanIndexForward = False
    )
    retlist = []
    ctr = 0
    songsAdded = 0
    while songsAdded < N and ctr < len(result["Items"]):
        if randint(0,1) == 1:
            retlist.append(result["Items"][ctr])
            songsAdded += 1
        ctr += 1
    return retlist        

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

