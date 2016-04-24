from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
from botocore.exceptions import ClientError
from boto.dynamodb2.table import Table
from boto.dynamodb2.layer1 import DynamoDBConnection
import pprint

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


#to connect to local db
conn = DynamoDBConnection(aws_access_key_id='AKIAI4EYFOGUXGPDXHLQ',
                          aws_secret_access_key='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',
                          host='localhost',
                          port=8000,
                          is_secure=False)

table = Table('WordCount', connection=conn)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")

table1 = dynamodb.Table('WordCount')


def create_word_record(table, word):
    response = table.update_item(
        Key={
            'word': word,
        },
        UpdateExpression="ADD word_count :val",
        ExpressionAttributeValues={
            ':val': decimal.Decimal(1)
        },
        ReturnValues="UPDATED_NEW"
    )
    return response['Attributes']['word_count']


def read_word_record(table, word):
    try:
        response = table.get_item(
            Key={
                'word': word
            },
            ConsistentRead=True
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']['word_count']


def batch_read_word_record(table, words):
    try:
        response = table.batch_get(
            keys=words
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        for w in response:
            pprint.pprint(w['word'])
            pprint.pprint(long(w['word_count']))
        #pprint.pprint(response['Responses'])
        #print(json.dumps(response, indent=4, cls=DecimalEncoder))

if __name__ == "__main__":
    word = 'temp'
    word2 = 'temp2'
    words = [{'word':'temp'},{'word':'temp2'}]
    create_word_record(table1, word)
    create_word_record(table1, word2)
    count = read_word_record(table1, word)
    batch_read_word_record(table, words)
    #print(word + ' : ' + str(count))