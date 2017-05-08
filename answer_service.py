from nltk.corpus import stopwords
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


# get the keyword according to the original questions
def getKeywordFromText(text):
    text = text.lower()
    text = text.replace("?", "")
    text = text.replace("uq", "")
    text = text.replace('"', "")
    text = text.replace('(', "")
    text = text.replace(')', '')
    text = text.replace("what's", '')
    text = text.replace("'s", '')
    text = text.replace('.', '')
    text = text.replace('\n', '')
    words = text.split(" ")
    filtered_words = [word for word in words if word not in stopwords.words('english')]
    inserted = []
    for filtered in filtered_words:
        if filtered != "" and filtered not in inserted:
            inserted.append(filtered)
    inserted.sort()
    inserted = ','.join(inserted)
    print(inserted)
    return inserted


# fetch the value from parameter json expression
def getValueFromParameter(parameter):
    for key in parameter.keys():
        if parameter[key].encode('ASCII') != "":
            print(parameter[key])
            return parameter[key].upper()

def fetchCourseInfoFromDataBase(parameter, field_name):
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    name = getValueFromParameter(parameter)
    cursor.execute('''SELECT * FROM course WHERE name=%s''', [name])
    result = cursor.fetchone()
    if result is None:
        return 'No Such course in uq'
    return result[field_name]


# fetch all the data from database
def fetchAllDataFromDatabase(tablename):
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    queryString = "SELECT * FROM %s" % tablename
    cursor.execute(queryString)
    result = cursor.fetchall()
    if result is None:
        return None
    return result


def fetchInfoFromDatabase(table_name, field_name, filter_name, filter_value):
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    print(filter_value)
    queryString = "SELECT * FROM %s WHERE %s='%s'" % (table_name, filter_name, filter_value)
    cursor.execute(queryString)
    result = cursor.fetchone()
    print(result)
    if result is None:
        return None
    return result[field_name]


# process ask for the unit of a course
def fetchUnitFromDatabase(parameter):
    result = fetchCourseInfoFromDataBase(parameter, 'unit')
    return result


# process ask for the description of a course
def fetchDescriptionFromDatabase(parameter):
    result = fetchCourseInfoFromDataBase(parameter, 'description')
    return result

# process ask for the description of a course
def fetchCoordinatorFromDatabase(parameter):
    result = fetchCourseInfoFromDataBase(parameter, 'coordinator')
    return result

def fetchSchoolLocationFromDatabase(parameter):
    name = getValueFromParameter(parameter)
    result = fetchInfoFromDatabase('school', 'location', 'name', name)
    return result


def fetchSchoolEmailFromDatabase(parameter):
    name = getValueFromParameter(parameter)
    result = fetchInfoFromDatabase('school', 'email', 'name', name)
    return result


def fetchSchoolPhoneFromDatabase(parameter):
    name = getValueFromParameter(parameter)
    result = fetchInfoFromDatabase('school', 'phone', 'name', name)
    return result


# process request ask for some general questions
def process_general_question(original_question):
    keyword = getKeywordFromText(original_question)
    result = fetchInfoFromDatabase('general_question', 'answer', 'keyword', keyword)
    return result


# switch to the function according to
def process_request(intent_type, parameter, original_question):
    if intent_type == 'CourseDescriptionIntent':
        return fetchDescriptionFromDatabase(parameter)
    elif intent_type == 'CourseUnitIntent':
        return fetchUnitFromDatabase(parameter)
    elif intent_type == 'DefaultFallbackIntent':
        return process_general_question(original_question)
    elif intent_type == 'LocationIntent':
        return fetchSchoolLocationFromDatabase(parameter)
    elif intent_type == 'LecturerIntent':
        return fetchCoordinatorFromDatabase(parameter)
    elif intent_type == 'GeneralIntent':
        return process_general_question(original_question)
    else:
        return "Sorry, currently we do not have such service"


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
        print(data)
        result = data['result']
        parameter = result['parameters']
        intentType = result['metadata']['intentName']
        original_question = result['resolvedQuery']

        result = process_request(intentType, parameter, original_question)
        if result is None:
            result = 'Sorry, please say again'
        response = response_body
        response['speech'] = result
        response['displayText'] = result
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

all_general_questions = fetchAllDataFromDatabase('general_question')

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
