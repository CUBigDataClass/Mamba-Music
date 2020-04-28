import boto3
import json


dynamo = boto3.resource('dynamodb')
table = dynamo.Table('users')


def delete(payload):
    response = table.delete_item(Key = {'CustomerId': payload['CustomerId']})
    if 'Item' in response:
        if 'likes' in response['Item'] and response['Item']['likes'] != None:
            response['Item']['likes'] = list(response['Item']['likes'])
        if 'dislikes' in response['Item'] and response['Item']['dislikes'] != None:
            response['Item']['dislikes'] = list(response['Item']['dislikes'])

    return respond(None, response)


def get(payload):
    response = table.get_item(Key = {'CustomerId': payload['CustomerId']})
    if 'Item' in response:
        if 'likes' in response['Item'] and response['Item']['likes'] != None:
            response['Item']['likes'] = list(response['Item']['likes'])
        if 'dislikes' in response['Item'] and response['Item']['dislikes'] != None:
            response['Item']['dislikes'] = list(response['Item']['dislikes'])

    return respond(None, response)


def put(payload):
    item = table.get_item(Key = {'CustomerId': payload['CustomerId']})
    if not 'Item' in item: # create new object
        if not ('first_name' and 'last_name' in payload):
            return respond('Missing attributes for data creation')
        else:
            item = {
                'CustomerId': payload['CustomerId'],
                'first_name': payload['first_name'],
                'last_name': payload['last_name']
            }

            table.put_item(Item = item)
            
            return respond(None, item)

    else: # update existing object
        item = item['Item']
        update_str = 'SET '
        attributes = {}

        if 'first_name' in payload:
            attributes[':fname'] = payload['first_name']
            update_str += 'first_name = :fname, '
        if 'last_name' in payload:
            attributes[':lname'] = payload['last_name']
            update_str += 'last_name = :lname, '

        # If you are reading this, welcome to hell
        # Markers for updating the likes and dislikes lists.
        # 'a' is what the request called, 'b' is the other field.
        # This is to prevent a song from being simultaneously liked and disliked.
        a = None
        b = None
        songTable = None
        songUpdate = None
        songAttr = None
        if 'likes' in payload:
            a = 'likes'
            b = 'dislikes'
        elif 'dislikes' in payload:
            a = 'dislikes'
            b = 'likes'

        if a != None and b != None:
            update_str += a + ' = :' + a[0] + ', '

            if not a in item or item[a] == None: # If list doesn't exist, create it and add
                attributes[':' + a[0]] = set([payload[a]])
            else: # Otherwise, add/remove from existing set
                if payload[a] in item[a]: # Remove
                    attributes[':' + a[0]] = item[a].remove(payload[a])
                else: # Add
                    attributes[':' + a[0]] = item[a].add(payload[a])

            # Song can't be simultaneously liked and disliked
            if b in item and payload[a] in item[b]:
                attributes[':' + b[0]] = item[b].remove(payload[a])
                update_str += b + ' = :' + b[0] + ', '

            # If we update user like list, reflect the same change in song db
            # Do the same stuff for the songs
            songTable = dynamo.Table('songs')
            songUpdate = 'SET ' + a + ' = :' + a[0] + ', ' + a + '_ct = :ct1, ' 
            songAttr = {}

            songItem = songTable.get_item(Key = {'SongId': payload[a]})
            if not 'Item' in songItem:
                return respond('SongIdNotValid')
            songItem = songItem['Item']

            if not a in songItem or songItem[a] == None:
                songAttr[':' + a[0]] = set([payload['CustomerId']])
                songAttr[':ct1'] = 1
            else:
                if payload['CustomerId'] in songItem[a]:
                    songAttr[':' + a[0]] = songItem[a].remove(payload['CustomerId'])
                    songAttr[':ct1'] = songItem[a + '_ct'] - 1
                else:
                    songAttr[':' + a[0]] = songItem[a].add(payload['CustomerId'])
                    songAttr[':ct1'] = songItem[a + '_ct'] + 1

            if b in songItem and payload['CustomerId'] in songItem[b]:
                songAttr[':' + b[0]] = songItem[b].remove(payload['CustomerId'])
                songUpdate += b + ' = :' + b[0] + ', ' + b + '_ct = :ct2, '
                songAttr[':ct2'] = songItem[b + '_ct'] - 1

            songUpdate = songUpdate[:len(songUpdate)-2]

            songTable.update_item(
                Key = {'SongId': payload[a]},
                UpdateExpression = songUpdate,
                ExpressionAttributeValues = songAttr
            )  


        update_str = update_str[:len(update_str)-2] # remove trailing comma
        if len(update_str) <= 4:
            return respond('Nothing to update')

        table.update_item(
            Key = {'CustomerId': payload['CustomerId']},
            UpdateExpression = update_str,
            ExpressionAttributeValues = attributes
        )  

        # set is not json serializable :) :) :) :) :) :) :)):):):
        if ':l' in attributes: 
            if attributes[':l']: # Empty set can't convert to list
                attributes[':l'] = list(attributes[':l'])
            else:
                attributes[':l'] = []
        if ':d' in attributes:
            if attributes[':d']:
                attributes[':d'] = list(attributes[':d'])
            else:
                attributes[':l'] = []

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
        if not 'CustomerId' in payload:
            return respond('No CustomerId specified')
        else:
            return operations[operation](payload)
    else:
        return respond('Unsupported method "{}"'.format(operation))
