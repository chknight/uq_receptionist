import re
from pyquery import PyQuery as pq
import pymysql


conn = pymysql.connect('localhost', 'root', 'bcbcslcj0310', 'uq_robot_receptionist', charset='utf8')
cur = conn.cursor()
# Error: UnicodeEncodeError: 'latin-1' codec can't encode character
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')


def cleanHtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    cleantext = cleantext.replace('\n', ' ')
    cleantext = re.sub(' +', ' ', cleantext)
    #print(cleantext)
    return cleantext

def retrieveAnswerPage(aPage):
    questions = aPage.find('.rn_DataValue').eq(0)
    #print(question)
    answers = aPage.find('.rn_DataValue').eq(1)
    question = cleanHtml(questions.html())
    answer = cleanHtml(answers.html())
    print(question)
    print(answer)

    cur.execute('''insert into generalQA (question, answer) value (%s, %s)''', (question, answer))
    conn.commit()

    
def retrievePage(qPage):
    questionList = qPage.find('.rn_Content')
    #print(questionList.text())
    
    links = questionList.find('a')
    for link in links:
        baseURL = 'https://uqfuture.custhelp.com'
        result_url = baseURL + link.attrib['href']
        answerPage = pq(url = result_url)
        retrieveAnswerPage(aPage = answerPage)
       

def retrieveMultiPages():
    index = 1
    total_page = 50 # actually total 46 pages now, the extra pages will be set for future update
    while(index < total_page):
        print(index)
        baseURL = 'https://uqfuture.custhelp.com/app/answers/list/st/4/page/' 
        result_url = baseURL + str(index)
        questionPage = pq(url = result_url)
        retrievePage(questionPage)
        index += 1
    
    
retrieveMultiPages()

