from pyquery import PyQuery as jquery
import MySQLdb
import re
host = 'https://future-students.uq.edu.au'

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


def retrieve_program_page(program_page):
    program_name = program_page.find('h1')
    print(program_page.html())


# retrieve one page
def retrieve_page(page):
    program_lists = page.find(".program__secondary-link")
    for program in program_lists.items():
        program_page = jquery(url=host + program.attr['href'])
        retrieve_program_page(program_page)


# start the program
def retrieve_pages():
    url = "https://future-students.uq.edu.au/study/find-a-program/listing/undergraduate"
    page = jquery(url=url)
    retrieve_page(page)

retrieve_pages()
