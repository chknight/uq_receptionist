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
    return inserted

def compare_keyword(keywords_from_user, keywords, dataset):
    matched = []
    # finalList = []
    index = 0
    for row in keywords:
        matched.append(0)
        for keyword in keywords_from_user:
            if keyword in row:
                matched[index] += 1
        if matched[index] == 0:
            matched[index] = 0
        else:
            rate1 = (float(matched[index]) + 0) / (float(len(keywords_from_user)) + 0)
            rate2 = (float(matched[index]) + 0) / (float(len(row)) + 0 )
            matched[index] = rate1 + rate2
        # finalList.append(matched[index])
        index += 1

    sorted_x = sorted(range(len(matched)), key=lambda k: matched[k], reverse=True)
    print(matched[sorted_x[0]])
    index = sorted_x[0]
    print(index)
    if matched[index] >= 1:
        return dataset[index]['answer']
    else:
        return "Sorry, we could not answer this question."


# fetch the value from parameter json expression
def getValueFromParameter(parameter):
    for key in parameter.keys():
        if parameter[key].encode('ASCII') != "":
            print(parameter[key])
            return parameter[key].upper()
    return None

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

# if the fetch fail, learn from the user input
def storeNewQuestionAndAnswer(question, answer):
    keyword = getKeywordFromText(question)
    connection.cursor().execute('''INSERT into self_training_question (question, answer, keyword)
                values (%s, %s, %s)''', [question, answer, ','.join(keyword)])
    connection.commit()
    all_keywords_in_self_train.append(keyword)
    all_self_train_questions.append({'question': question, 'answer': answer})

def storeUserIntoDatabase(device_id, nationality):
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''INSERT into user (device_id, nationality)
                values (%s, %s)''', [device_id, nationality])
    connection.commit()


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


def fetchSchoolLocationFromDatabase(parameter, original_question):
    name = getValueFromParameter(parameter)
    if name is None:
        return process_general_question(original_question)
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
    result = compare_keyword(keyword, all_keywords_in_self_train, all_self_train_questions)
    if result == 'Sorry, we could not answer this question.':
        result = compare_keyword(keyword, all_keywords, all_general_questions)
    # result = fetchInfoFromDatabase('general_question', 'answer', 'keyword', keyword)
    return result


def process_program_question(fieldName, parameter, context):
    print(fieldName)
    device_id = context['parameters']['deviceId']
    user_info = fetchInfoFromDatabase('user', 'nationality', 'device_id', device_id)
    if user_info is None:
        return "Are you an international student?"
    if user_info == 1:
        title = getValueFromParameter(parameter)
        return fetchInfoFromDatabase('program_international', fieldName, 'title', title)
    else:
        title = getValueFromParameter(parameter)
        return fetchInfoFromDatabase('program_domestic', fieldName, 'title', title)

# switch to the function according to
def process_request(intent_type, parameter, original_question, context):
    if intent_type == 'CourseDescriptionIntent':
        return fetchDescriptionFromDatabase(parameter)
    elif intent_type == 'CourseUnitIntent':
        return fetchUnitFromDatabase(parameter)
    elif intent_type == 'DefaultFallbackIntent':
        return process_general_question(original_question)
    elif intent_type == 'LocationIntent':
        return fetchSchoolLocationFromDatabase(parameter, original_question)
    elif intent_type == 'LecturerIntent':
        return fetchCoordinatorFromDatabase(parameter)
    elif intent_type == 'GeneralIntent':
        return process_general_question(original_question)
    elif intent_type == 'EntryRequirementIntent':
        return process_program_question('entry_requirements', parameter, context)
    elif intent_type == 'ProgramCostIntent':
        return process_program_question('fee', parameter, context)
    elif intent_type == 'ProgramDurationIntent':
        return process_program_question('duration', parameter, context)
    elif intent_type == 'ProgramCourseListIntent':
        return process_program_question('courses', parameter, context)
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
        context = result['contexts'][0]
        intentType = result['metadata']['intentName']
        original_question = result['resolvedQuery']

        result = process_request(intentType, parameter, original_question, context)
        if result is None:
            result = 'Sorry, please say again'
        response = response_body
        response['speech'] = result
        response['displayText'] = result
        self.write(response)


# handle self training
class SelfTraingingHandler(tornado.web.RequestHandler):
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
        question = data['question']
        answer = data['answer']

        storeNewQuestionAndAnswer(question, answer)
        response = {
            'result': 'We already record your request.'
        }
        self.write(response)

# handle self training
class UserHandler(tornado.web.RequestHandler):
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
        device_id = data['deviceId']
        nationality = data['nationality']
        if nationality == '1':
            nationality = 1
        else:
            nationality = 0
        storeUserIntoDatabase(device_id, nationality)
        response = {
            'result': 'Store the user in database'
        }
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/selftraining", SelfTraingingHandler),
        (r"/nationality", UserHandler)
    ])

def prepare_keyword():
    temp = []
    for row in all_general_questions:
        keywords = row['keyword'].split(',')
        all_keywords.append(keywords)
    for row in all_self_train_questions:
        temp.append(row)
        keywords = row['keyword'].split(',')
        all_keywords_in_self_train.append(keywords)


all_general_questions = fetchAllDataFromDatabase('general_question')
all_self_train_questions = list(fetchAllDataFromDatabase('self_training_question'))
all_keywords = []
all_keywords_in_self_train = []
prepare_keyword()


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
