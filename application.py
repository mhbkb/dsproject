from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    return "Hello World!"


# How: localhost   curl --data '' http://127.0.0.1:5000/hostname/String/a%20b%20c
#      online      curl --data '' http://flask3.qst6ftqmmz.us-west-2.elasticbeanstalk.com/hostname/String/a%20b%20c
# TODO: check param, Call db
@application.route("/hostname/String/<param>", methods=['POST'])
def write(param):
	strs = param.split(' ')
	# Call db api
	print str(strs)

	return ', '.join(str(x) for x in strs)


# How: localhost   http://127.0.0.1:5000/hostname/Counts/a,b
#      online      http://flask3.qst6ftqmmz.us-west-2.elasticbeanstalk.com/hostname/Counts/a,b
# TODO: check param, Call db
@application.route("/hostname/Counts/<words>", methods=['GET'])
def read(words):
	wordsArray = words.split(',')
	# Call db api

	return ', '.join(str(x) for x in wordsArray)



if __name__ == "__main__":
    application.run(debug=True)