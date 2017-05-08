# get the information from uq calender
from pyquery import PyQuery as jquery
import re
import MySQLdb


connection = MySQLdb.connect('localhost', 'root', '19941005', 'uq_receptionist')
connection.set_character_set('utf8')
connection.cursor().execute('SET NAMES utf8;')
connection.cursor().execute('SET CHARACTER SET utf8;')
connection.cursor().execute('SET character_set_connection=utf8;')


# clean the tag in html
def clean_text(raw_html):
    cleaner = re.compile('<.*?>')
    cleantext = re.sub(cleaner, '', raw_html)
    cleantext = cleantext.replace('\n', ' ')
    cleantext = re.sub(' +', ' ', cleantext)
    return cleantext


def retrieve_answer_page(answerPage):
    question = answerPage.find('.rn_DataValue').eq(0)
    answer = answerPage.find('.rn_DataValue').eq(1)
    question = clean_text(question.html())
    answer = clean_text(answer.html())
    # for child in answer.items():
    print(question)
    print(answer)
    connection.cursor().execute('''INSERT into general_question (question, answer)
            values (%s, %s)''', (question, answer))
    connection.commit()
        # if child.tag == 'p':
        #     print('Node is a p')
        #     print(child.text.replace('<!--stopindex-->', '').replace('<!--startindex-->', ''))
        # elif child.tag == 'blockquote':
        #     print('Node is blockquote')
        #     print(child.children())



# retrieve the information in calender page
def retrieve_page(qaPage):
    baseurl = 'https://uqfuture.custhelp.com'
    listHolder = qaPage.find('.rn_Content')
    all_link = listHolder.find('a')
    for li in all_link:
        if li.text:
            url = baseurl + li.attrib['href']
            answerPage = jquery(url=url)
            retrieve_answer_page(answerPage=answerPage)


# start the program
def retrieve_pages():
    max = 43
    baseurl = "https://uqfuture.custhelp.com/app/answers/list/st/4/page/"
    index = 1
    while(index <= max):
        print(index)
        url = baseurl + str(index)
        page = jquery(url=url)
        retrieve_page(page)
        index += 1

retrieve_pages()