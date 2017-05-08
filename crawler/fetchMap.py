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



# retrieve the information in calender page
def retrieve_page(qaPage):
    locationsTable = qaPage.find('[summary="Map Index Content"]')
    locationTd = locationsTable.find('td')
    # print(locationTd.html())
    print(locationTd.text())
    # for td in locationTd.find('a').items():
    #     print(td.html())
    #     print(td.find('a').text())
    #     print('\n')
    buildinglist = locationTd.text().replace(' , ', ',').split(',')
    buildingName = []
    buildingNumber = []
    for index, building in enumerate(buildinglist):
        print(building)
        if index != 0:
            number = re.findall(r'^[0-9]+[A-Za-z0-9]* ', building)
            print(number)
            print(number)
            # the last one of the list
            lastOne = re.compile('^[0-9]+$')
            if lastOne.match(building):
                buildingNumber.append(building)
                break
            cleaner = re.compile('^[0-9]+[A-Za-z0-9]* ')
            cleantext = re.sub(cleaner, '', building)
            cleantext = re.sub(r'^ ', '', cleantext)
            print(cleantext)
            if cleantext:
                buildingName.append(cleantext)
            else:
                print('this is the last one')
            if len(number) > 0:
                buildingNumber.append(number[0].replace(' ', ''))
            else:
                buildingNumber.append('no id')
        else:
            print(building)
            buildingName.append(building)
    for index, item in enumerate(buildingName):
        print(index)
        print(buildingName[index] + ' ' + buildingNumber[index])
        connection.cursor().execute('''INSERT into location (building_name, building_number)
                    values (%s, %s)''', (buildingName[index], buildingNumber[index] ))
        connection.commit()


# start the program
def retrieve_pages():
    baseurl = "http://www.uq.edu.au/maps/mapindex.html?menu=1"
    page = jquery(url=baseurl)
    retrieve_page(page)

retrieve_pages()