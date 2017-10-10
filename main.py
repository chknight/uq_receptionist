from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import tornado.ioloop
import tornado.web
import pymysql
import json


def mysql_connection():
    conn = pymysql.connect('localhost', 'root', 'bcbcslcj0310', 'uq_robot_receptionist', charset='utf8')
    cur = conn.cursor()
    # Error: UnicodeEncodeError: 'latin-1' codec can't encode character
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')
    return conn


# word lemmatization
lemmatizer = WordNetLemmatizer()


response_body = {
    "speech": "",
    "displayText": "",
    "data": {},
    "contextOut": [],
    "source": "me"
}


# get keywords of questions from generalQA text.
def keyword_extraction(generalQA_text):
    text1 = generalQA_text.lower()
    text2 = text1.replace('?', '')
    text3 = text2.replace('uq', '')
    text4 = text3.replace('"', '')
    text5 = text4.replace('(', '')
    text6 = text5.replace(')', '')
    text7 = text6.replace("what's", '')
    text8 = text7.replace("'s", '')
    text9 = text8.replace('.', '')
    text = text9.replace('\n', '')
    word_list = text.split(' ')
    filtered_words = [w for w in word_list if not w in stopwords.words('english')]
    inserted = []
    for filtered_word in filtered_words:
        if filtered_word != '' and filtered_word not in inserted:
            inserted.append(filtered_word)
    return inserted


# compare extracted keywords between user's query and general question
def keyword_comparision(user_query_keyword, general_question_keyword, dataset):
    match_item = []
    index = 0
    for row in general_question_keyword:
        match_item.append(0)
        for word in user_query_keyword:
            keyword = lemmatizer.lemmatize(word)
            if keyword in row:
                match_item[index] += 1
        if match_item[index] == 0:
            match_item[index] = 0
        else:
            match_rate1 = (float(match_item[index]) + 0) / (float(len(user_query_keyword)) + 0)
            match_rate2 = (float(match_item[index]) + 0) / (float(len(row)) + 0)
            match_item[index] = match_rate1 + match_rate2
        index += 1

    sort_item = sorted(range(len(match_item)), key = lambda k: match_item[k], reverse = True)
    print(match_item[sort_item[0]])
    index = sort_item[0]
    print(index)
    if match_item[index] >= 1.6:
        return dataset[index]['answer']
    else:
        return None


#  fetch the value from parameter json expression
def getValueFromJsonParameter(parameter):
    for key in parameter.keys():
        if parameter[key].encode('ASCII') != '':
            print(parameter[key])
            return parameter[key]
    return None


def fetchDomesticProgramInfoFromDB(title, column_name):
    conn = mysql_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from domestic_Program where title = %S" % [title]
    cur.execute(sql)
    fetch_result = cur.fetchone()
    conn.close()
    if fetch_result is None:
        return "No such program in UQ"
    return fetch_result[column_name]


def fetchInternationalProgramInfoFromDB(title, column_name):
    conn = mysql_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from international_Program where title = %S" % [title]
    cur.execute(sql)
    fetch_result = cur.fetchone()
    conn.close()
    if fetch_result is None:
        return "No such program in UQ"
    return fetch_result[column_name]


# fetch all data from database
def fetchAllDataFromDB(table_name):
    conn = mysql_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from %s" % table_name
    cur.execute(sql)
    fetch_result = cur.fetchall()
    conn.close()
    if fetch_result is None:
        return None
    return fetch_result


def fetchInfoFromDB(table_name, column_name, filter_name, filter_value):
    conn = mysql_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    print(filter_value)
    sql = "select * from %s where %s = '%s'" % (table_name, filter_name, filter_value)
    cur.execute(sql)
    fetch_result = cur.fetchone()
    conn.close()
    if fetch_result is None:
        return None
    return fetch_result[column_name]


# process questions about program detail
def fetchDomesticProgramOverview(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchDomesticProgramInfoFromDB(title, 'overview')
    return title, fetch_result


def fetchInternationalProgramOverview(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchInternationalProgramInfoFromDB(title,'overview')
    return title, fetch_result


def fetchDomesticProgramFee(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchDomesticProgramInfoFromDB(title, 'fee')
    return title,fetch_result


def fetchInternationalProgramFee(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchInternationalProgramInfoFromDB(title,'fee')
    return title,fetch_result


def fetchDomesticProgramEntryRequirement(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchDomesticProgramInfoFromDB(title, 'entry_requirement')
    return title, fetch_result


def fetchInternationalProgramEntryRequirement(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchInternationalProgramInfoFromDB(title, 'entry_requirement')
    return title, fetch_result


def fetchDomesticProgramFaculty(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchDomesticProgramInfoFromDB(title, 'faculty')
    return title, fetch_result


def fetchInternationalProgramFaculty(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchInternationalProgramInfoFromDB(title, 'faculty')
    return title, fetch_result


def fetchDomesticProgramDuration(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchDomesticProgramInfoFromDB(title, 'duration')
    return title, fetch_result


def fetchInternationalProgramDuration(parameter):
    title = getValueFromJsonParameter(parameter)
    fetch_result = fetchInternationalProgramInfoFromDB(title, 'duration')
    return title, fetch_result


# process general question
def process_general_question(original_question):
    keyword = keyword_extraction(original_question)
    result = fetchInfoFromDB('generalQA', 'answer', 'question', original_question)
    if result is None:
        result = keyword_comparision(keyword, all_keywords, all_general_question)
    else:
        result = result
    return result


# switch to the function according to
def process_request(intent_type, parameter, original_question, context):
    if intent_type == 'ProgramInfo_Domestic':
        title, result = fetchDomesticProgramOverview(parameter)
        return result
    elif intent_type == 'ProgramInfo_International':
        title, result = fetchInternationalProgramOverview(parameter)
        return result
    elif intent_type == 'DefaultFallbackIntent':
        result = process_general_question(original_question)
        return result
    elif intent_type == 'QAofUQ':
        result = process_general_question(original_question)
        return result
    elif intent_type == 'ProgramRequirement_Domestic':
        title, result = fetchDomesticProgramEntryRequirement(parameter)
        if result is not None:
            result = 'The entry requirements of ' + title + ' is: ' + result
        return result
    elif intent_type == 'ProgramRequirement_International':
        title, result = fetchInternationalProgramEntryRequirement(parameter)
        if result is not None:
            result = 'The entry requirements of ' + title + ' is: ' + result
        return result
    elif intent_type == 'ProgramFee_Domestic':
        title, result = fetchDomesticProgramFee(parameter)
        if result is not None:
            result = 'The cost of ' + title + ' is: ' + result + ' dollar per year'
    elif intent_type == 'ProgramFee_International':
        title, result = fetchInternationalProgramFee(parameter)
        if result is not None:
            result = 'The cost of ' + title + ' is: ' + result + ' dollar per year'
        return result
    elif intent_type == 'ProgramFaculty_Domestic':
        title, result = fetchDomesticProgramFaculty(parameter)
        if result is not None:
            result = 'The duration of ' + title + ' is: ' + result
        return result
    elif intent_type == 'ProgramFaculty_International':
        title, result = fetchInternationalProgramFaculty(parameter)
        if result is not None:
            result = 'The duration of ' + title + ' is: ' + result
        return result
    elif intent_type == 'ProgramDuration_Domestic':
        title, result = fetchDomesticProgramDuration(parameter)
        if result is not None:
            result = 'The duration of ' + title + ' is: ' + result
        return result
    elif intent_type == 'ProgramDuration_International':
        title, result = fetchInternationalProgramDuration(parameter)
        if result is not None:
            result = 'The duration of ' + title + ' is: ' + result
        return result
    else:
        return "Sorry, currently we do not have such service"


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def get(self):
        self.write("Hello, world")

    def post(self):
        self.set_header("Content-Type", "text/plain")
        data = json.loads(self.request.body.decode('ascii'))
        print(data)
        result = data['result']
        parameter = result['parameters']
        if len(result['contexts']) > 0:
            context = result['contexts'][0]
        else:
            context = ""
        intentType = result['metadata']['intentName']
        original_question = result['resolvedQuery']

        result = process_request(intentType, parameter, original_question, context)
        print(result)
        if result is None:
            result = 'Sorry, we could not answer this question.'
        response = response_body
        response['speech'] = result
        response['displayText'] = result
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

'''
def prepare_keyword():
    for row in all_general_questions:
        keywords = row['keyword'].split(',')
        processed_keywords = []
        for keyword in keywords:
            keyword = lemmatizer.lemmatize(keyword)
            print(keyword)
            processed_keywords.append(keyword)
        all_keywords.append(processed_keywords)
'''


all_general_questions = fetchAllDataFromDB('generalQA')
all_keywords = []
#prepare_keyword()


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()