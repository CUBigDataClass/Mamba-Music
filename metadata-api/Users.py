import boto3
import json


dynamo = boto3.resource('dynamodb')
table = dynamo.Table('users')


def delete(payload):
    response = table.delete_item(Key = {'CustomerId': payload['CustomerId']})
    return respond(None, response)


def get(payload):
    response = table.get_item(Key = {'CustomerId': payload['CustomerId']})
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
            if 'likes' in payload:
                item['likes'] = set(payload['likes'])
            if 'dislikes' in payload:
                item['dislikes'] = set(payload['likes'])

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

        if 'first_name' in payload:
            attributes[':fname'] = payload['first_name']
            update_str += 'first_name = :fname, '
        if 'last_name' in payload:
            attributes[':lname'] = payload['last_name']
            update_str += 'last_name = :lname, '

        if 'action' in payload: # is like/dislike an addition or a deletion?
            if payload['action'] == 'add': # if addition, union to existing set
                if 'likes' in payload:
                    if 'likes' in item:
                        attributes[':l'] = set(item['likes']) | set(payload['likes'])
                    else:
                        attributes[':l'] = set(payload['likes'])
                    update_str += 'likes = :l, '

                if 'dislikes' in payload:
                    if 'dislikes' in item:
                        attributes[':dl'] = set(item['dislikes']) | set(payload['dislikes'])
                    else:
                        attributes[':dl'] = set(payload['dislikes'])
                    update_str += 'dislikes = :dl, '

            elif payload['action'] == 'del': # if deletion, remove from existing set
                if 'likes' in payload:
                    if 'likes' in item:
                        for l in payload['likes']:
                            if l in item['likes']:
                                item['likes'].remove(l)
                        attributes[':l'] = item['likes']
                        if attributes[':l'] == set(): # can't store empty set, so use list
                            attributes[':l'] = []
                        update_str += 'likes = :l, '

                if 'dislikes' in payload:
                    if 'dislikes' in item:
                        for l in payload['dislikes']:
                            if l in item['dislikes']:
                                item['dislikes'].remove(l)
                        attributes[':dl'] = item['dislikes']
                        if attributes[':dl'] == set(): # can't store empty set, so use list
                            attributes[':dl'] = []
                        update_str += 'dislikes = :dl, '

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
        if not 'CustomerId' in payload:
            return respond('No CustomerId specified')
        else:
            return operations[operation](payload)
    else:
        return respond('Unsupported method "{}"'.format(operation))
