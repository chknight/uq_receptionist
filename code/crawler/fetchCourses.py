import urllib2
import time
from openpyxl import Workbook
from pyquery import PyQuery as jquery
import MySQLdb
import socket

host = 'https://www.uq.edu.au'

connection = MySQLdb.connect('localhost', 'root', '19941005', 'uq')
connection.set_character_set('utf8')
connection.cursor().execute('SET NAMES utf8;')
connection.cursor().execute('SET CHARACTER SET utf8;')
connection.cursor().execute('SET character_set_connection=utf8;')

def save_to_database(description, level, unit, content, assessment, coordinator, name, code, duration):
    connection.cursor().execute('''INSERT into COURSE (description, level, unit, content, assessment, coordinator, name, code, duration)
        values (%s, %s,%s, %s,%s, %s, %s, %s, %s)''', (description, level, unit, content, assessment, coordinator, name, code, duration))
    connection.commit()

def retrieve_course_page(course_page, code):
    description = course_page.find('#course-summary').text().encode("utf-8")
    level = course_page.find("#course-level").text().encode("utf-8")
    unit = course_page.find("#course-units").text().encode("utf-8")
    content = course_page.find("#course-contact").text().encode("utf-8")
    assessment = course_page.find("#course-assessment-methods").text().encode("utf-8")
    coordinator = course_page.find("#course-coordinator").text().encode("utf-8")
    name = course_page.find("#course-title").text().encode("utf-8")
    duration = course_page.find("#course-duration").text().encode("utf-8")
    save_to_database(description, level, unit, content, assessment, coordinator, name, code, duration)


def retrieve_course_list_page(courselist_page):
    courses = courselist_page.find('tr>td:first>a')
    index = 0
    while index < courses.size():
        course_url = host + courses.eq(index).attr("href")
        course_page = jquery(course_url)
        print courses.eq(index).text()
        retrieve_course_page(course_page, courses.eq(index).text())
        index += 1




def retrieve_program_page(program_page):
    if program_page.find("a.green") is not None:
        try:
            courselist_url = host + program_page.find("a.green").attr("href")
            print courselist_url
            courselist_page = jquery(url=courselist_url)
            retrieve_course_list_page(courselist_page)
        except Exception, err:
            print err




def retrieve_page(page):
    program_lists = page.find(".plan")
    first = True
    print program_lists.size()
    index = 1
    while index < program_lists.size():
        program = program_lists.eq(index)
        index += 1
        if program.text() != "":
            print program.text()
            program_url = host + program.find('a').attr("href")
            print program_url
            try:
                program_page = jquery(url=program_url)
                retrieve_program_page(program_page)
            except:
                print "error"




def retrieve_pages():
    url = "https://www.uq.edu.au/study/browse.html?level=ugpg"
    page = jquery(url=url)
    retrieve_page(page)

retrieve_pages()
