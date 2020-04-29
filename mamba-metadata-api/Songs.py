import boto3
import json
import datetime


dynamo = boto3.resource('dynamodb')
table = dynamo.Table('songs')


def delete(payload):
    response = table.delete_item(Key = {'SongId': payload['SongId']})
    if 'Item' in response:
        if 'likes' in response['Item']:
            del response['Item']['likes']
        if 'dislikes' in response['Item']:
            del response['Item']['dislikes']
        response['Item']['likes_ct'] = int(response['Item']['likes_ct'])
        response['Item']['dislikes_ct'] = int(response['Item']['dislikes_ct'])

    return respond(None, response)


def get(payload):
    response = table.get_item(Key = {'SongId': payload['SongId']})
    if 'Item' in response:
        if 'likes' in response['Item']:
            del response['Item']['likes']
        if 'dislikes' in response['Item']:
            del response['Item']['dislikes']
        response['Item']['likes_ct'] = int(response['Item']['likes_ct'])
        response['Item']['dislikes_ct'] = int(response['Item']['dislikes_ct'])

    return respond(None, response)


def put(payload):
    item = table.get_item(Key = {'SongId': payload['SongId']})
    if not 'Item' in item: # create new object
        if not ('title' and 'artist' and 'genre' in payload):
            return respond('Missing attributes for data creation')
        else:
            now = datetime.datetime.now()
            item = {
                'SongId': payload['SongId'],
                'title': payload['title'],
                'artist': payload['artist'],
                'genre': payload['genre'],
                'Timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
                'likes_ct': 0,
                'dislikes_ct': 0
            }

            if 'ArtId' in payload:
                item['ArtId'] = payload['ArtId']

            table.put_item(Item = item)
            
            return respond(None, item)

    else: # update existing object
        item = item['Item']
        update_str = 'SET '
        attributes = {}

        if 'title' in payload:
            attributes[':t'] = payload['title']
            update_str += 'title = :t, '
        if 'artist' in payload:
            attributes[':a'] = payload['artist']
            update_str += 'artist = :a, '
        if 'ArtId' in payload:
            attributes[':aid'] = payload['ArtId']
            update_str += 'ArtId = :aid, '
        if 'genre' in payload:
            attributes[':g'] = payload['genre']
            update_str += 'genre = :g, '

        update_str = update_str[:len(update_str)-2] # remove trailing comma
        if len(update_str) <= 4:
            return respond('Nothing to update')

        table.update_item(
            Key = {'SongId': payload['SongId']},
            UpdateExpression = update_str,
            ExpressionAttributeValues = attributes
        )  

        return respond(None, attributes)


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }


def lambda_handler(event, context):
    operations = {
        'DELETE': lambda x: delete(x),
        'GET': lambda x: get(x),
        'PUT': lambda x: put(x),
    }


    operation = event['httpMethod']

    if operation in operations:
        payload = event['queryStringParameters'] if operation != 'PUT' else json.loads(event['body'])
        if not 'SongId' in payload:
            return respond('No SongId specified')
        else:
            return operations[operation](payload)
    else:
        return respond('Unsupported method "{}"'.format(operation))

