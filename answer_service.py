import nltk
import tornado.ioloop
import tornado.web
import MySQLdb
import json


connection = MySQLdb.connect('localhost', 'root', '19941005', 'uq_receptionist')
connection.set_character_set('utf8')
connection.cursor().execute('SET NAMES utf8;')
connection.cursor().execute('SET CHARACTER SET utf8;')
connection.cursor().execute('SET character_set_connection=utf8;')

response_body = {
    "speech": "",
    "displayText": "",
    "data": {},
    "contextOut": [],
    "source": "me"
}

def getKeywrodFromParameter(parameter):
    for key in parameter.keys():
        if parameter[key].encode('ASCII') != "":
            print(parameter[key])
            return parameter[key].upper()

def fetchCourseInfoFromDataBase(parameter, field_name):
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    print(parameter)
    name = getKeywrodFromParameter(parameter)
    print(name)
    cursor.execute('''SELECT * FROM course WHERE name=%s''', [name])
    result = cursor.fetchone()
    print(result)
    if result is None:
        return 'No Such course in uq'

    return result[field_name]

def fetchUnitFromDatabase(parameter):
    result = fetchCourseInfoFromDataBase(parameter, 'unit')
    return result

def fetchDescriptionFromDatabase(parameter):
    result = fetchCourseInfoFromDataBase(parameter, 'description')
    return result


def process_request(intentType, parameter):
    return {
        'CourseDescriptionIntent': fetchDescriptionFromDatabase(parameter),
        'CourseUnitIntent': fetchUnitFromDatabase(parameter)
    }.get(intentType)

class MainHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        self.write("Hello, world")

    def post(self):
        self.set_header("Content-Type", "text/plain")
        data = json.loads(self.request.body.decode('ascii'))
        result = data['result']
        parameter = result['parameters']
        intentType = result['metadata']['intentName']

        result = process_request(intentType, parameter)
        response = response_body
        response['speech'] = result
        response['displayText'] = result
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
