import boto3
import json
import datetime


dynamo = boto3.resource('dynamodb')
table = dynamo.Table('songs')


def delete(payload):
    response = table.delete_item(Key = {'SongId': payload['SongId']})
    return respond(None, response)


def get(payload):
    response = table.get_item(Key = {'SongId': payload['SongId']})
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
                'Timestamp': now.strftime('%Y-%m-%d %H:%M:%S')
            }

            if 'likes' in payload:
                item['likes'] = set(payload['likes'])
                item['like_ct'] = len(item['likes'])
            else:
                item['like_ct'] = 0

            if 'dislikes' in payload:
                item['dislikes'] = set(payload['likes'])
                item['dislike_ct'] = len(item['dislikes'])
            else:
                item['dislike_ct'] = 0

            if 'ArtId' in payload:
                item['ArtId'] = payload['ArtId']

            table.put_item(Item = item)
            
            # set is not json serializable :) :) :) :) :) :) :)):):):
            if 'likes' in item: 
                item['likes'] = list(item['likes'])
            if 'dislikes' in item:
                item['dislikes'] = list(item['likes'])

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

        if 'action' in payload: # is like/dislike an addition or a deletion?
            if payload['action'] == 'add': # if addition, union to existing set
                if 'likes' in payload:
                    if 'likes' in item:
                        attributes[':l'] = set(item['likes']) | set(payload['likes'])
                    else:
                        attributes[':l'] = set(payload['likes'])
                    update_str += 'likes = :l, '
                    attributes[':lc'] = len(attributes[':l'])
                    update_str += 'like_ct = :lc, '

                if 'dislikes' in payload:
                    if 'dislikes' in item:
                        attributes[':dl'] = set(item['dislikes']) | set(payload['dislikes'])
                    else:
                        attributes[':dl'] = set(payload['dislikes'])
                    update_str += 'dislikes = :dl, '
                    attributes[':dlc'] = len(attributes[':dl'])
                    update_str += 'dislike_ct = :dlc, '

            elif payload['action'] == 'del': # if deletion, remove from existing set
                if 'likes' in payload:
                    if 'likes' in item:
                        ct = 0
                        for l in payload['likes']:
                            if l in item['likes']:
                                item['likes'].remove(l)
                                ct += 1
                        attributes[':l'] = item['likes']
                        if attributes[':l'] == set(): # can't store empty set, so use list
                            attributes[':l'] = []
                        update_str += 'likes = :l, '

                        if ct:
                            update_str += 'like_ct = :lc, '
                            attributes[':lc'] = int(item['like_ct'] - ct)

                if 'dislikes' in payload:
                    if 'dislikes' in item:
                        ct = 0
                        for l in payload['dislikes']:
                            if l in item['dislikes']:
                                item['dislikes'].remove(l)
                                ct += 1
                        attributes[':dl'] = item['dislikes']
                        if attributes[':dl'] == set(): # can't store empty set, so use list
                            attributes[':dl'] = []
                        update_str += 'dislikes = :dl, '

                        if ct:
                            update_str += 'dislike_ct = :dlc, '
                            attributes[':dlc'] = int(item['dislike_ct'] - ct)

        update_str = update_str[:len(update_str)-2] # remove trailing comma
        if len(update_str) <= 4:
            return respond('Nothing to update')

        table.update_item(
            Key = {'SongId': payload['SongId']},
            UpdateExpression = update_str,
            ExpressionAttributeValues = attributes
        )  

        # set is not json serializable :) :) :) :) :) :) :)):):):
        if ':l' in attributes: 
            attributes[':l'] = list(attributes[':l'])
        if ':dl' in attributes:
            attributes[':dl'] = list(attributes[':dl'])

        return respond(None, attributes)


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    operations = {
        'DELETE': lambda x: delete(x),
        'GET': lambda x: get(x),
        'PUT': lambda x: put(x),
    }

    operation = event['requestContext']['http']['method']
    if operation in operations:
        payload = json.loads(event['body'])
        if operation != 'PUT':
            payload = payload['queryStringParameters']
        if not 'SongId' in payload:
            return respond('No SongId specified')
        else:
            return operations[operation](payload)
    else:
        return respond('Unsupported method "{}"'.format(operation))
