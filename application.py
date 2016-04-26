from flask import Flask
from boto import dynamodb2
import boto3
import json
import decimal
from botocore.exceptions import ClientError
from boto.dynamodb2.table import Table
import os
import operator

FLASK_DEBUG = 'false' if os.environ.get('FLASK_DEBUG') is None else os.environ.get('FLASK_DEBUG')

application = Flask(__name__)

# Load config values specified above
application.config.from_object(__name__)

# Load configuration vals from a file
application.config.from_envvar('APP_CONFIG', silent=True)


application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']


ddb_conn = dynamodb2.connect_to_region(application.config['AWS_REGION'])
table = Table(table_name=application.config['WORD_COUNT'],
                  connection=ddb_conn)

dynamodb = boto3.resource('dynamodb', region_name=application.config['AWS_REGION'])
table1 = dynamodb.Table(application.config['WORD_COUNT'])
#client = boto3.client('dynamodb')


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


@application.route("/")
def hello():
    return "Hello World!"


# How: localhost   curl --data '' http://127.0.0.1:5000/String/a%20b%20c
#      online      curl --data '' http://flask3.qst6ftqmmz.us-west-2.elasticbeanstalk.com/String/a%20b%20c
# TODO: check param, Call db
@application.route("/String/<param>", methods=['POST'])
def write(param):
    strs = param.split()
    count = 0
    word_map = {}
    for s in strs:
        count += 1
        word_map[s] = word_map.get(s,0) + 1
        create_word_record(table1, s)
    sorted_word_map = sorted(word_map.items(), key=operator.itemgetter(1), reverse=True)
    top_words = {}
    length = min(10,len(sorted_word_map))
    for i in range(0,length):
        top_words[sorted_word_map[i][0]] = sorted_word_map[i][1]
    r = {'count':count,'top_words':top_words}
    return json.dumps(r)



# How: localhost   http://127.0.0.1:5000/Counts/a,b
#      online      http://flask3.qst6ftqmmz.us-west-2.elasticbeanstalk.com/Counts/a,b
# TODO: check param, Call db
@application.route("/Counts/<words>", methods=['GET'])
def read(words):
    wordsArray = filter(lambda x: x != '', words.split(','))
    # Call db api
    query = []
    count = 0
    for word in wordsArray:
        query.append({'word':word})
    results = batch_read_word_record(table, query)
    return json.dumps(results)


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


def batch_read_word_record(table, words):
    try:
        response = table.batch_get(
            keys=words,
            consistent=True
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        results = {}
        for w in response:
            results[w['word']] = long(w['word_count'])
        return results

if __name__ == "__main__":
    application.run(debug=True)