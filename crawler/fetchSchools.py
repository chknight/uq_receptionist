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


def retrieve_school_page(school_page):
    block = school_page.find('#content-primary').find('td').find('p')
    items = list(block.items())
    head = items[0].text().replace('Head of School: ', '').replace('Head: ', '')
    homepage = items[1].text().replace('Homepage: ', '')
    email =''
    phone = ''
    fax = ''
    office = ''
    for item in block.items():
        text = item.text()
        if "Head: " in text:
            head = text.replace('Head of School: ', '').replace('Head: ', '')
        elif 'Homepage: ' in text:
            homepage = text.replace('Homepage: ', '')
        elif 'Email Address: ' in text:
            email = text.replace('Email Address: ', '')
        elif 'Phone:' in text:
            phone = text.replace('Phone: ', '')
        elif 'Fax: ' in text:
            fax = text.replace('Fax: ', '')
        elif 'Main Office: ' in text:
            office = text.replace('Main Office: ', '')
    connection.cursor().execute('''INSERT into school (head, homepage, email, phone, fax, location)
                values (%s, %s, %s, %s, %s, %s)''', (head, homepage, email, phone, fax, office))
    connection.commit()

# retrieve the information in calender page
def retrieve_page(qaPage):
    base_url = 'http://www.uq.edu.au/departments/'
    all_links = qaPage.find('#content-primary>a')
    for link in all_links.items():
        url = base_url + link.attr['href']
        retrieve_school_page(jquery(url=url))

# start the program
def retrieve_pages():
    baseurl = "http://www.uq.edu.au/departments/unit_types.html?type=5"
    page = jquery(url=baseurl)
    retrieve_page(page)

retrieve_pages()