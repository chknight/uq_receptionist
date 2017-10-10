import re
import pymysql
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import  WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *


conn = pymysql.connect('localhost', 'root', 'bcbcslcj0310', 'uq_robot_receptionist', charset='utf8')
cur = conn.cursor()
# Error: UnicodeEncodeError: 'latin-1' codec can't encode character
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')

baseURL = 'https://future-students.uq.edu.au'

browser = webdriver.PhantomJS()
browser.maximize_window()
#browser.set_page_load_timeout(30)


def cleanHtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    cleantext = cleantext.replace('\n', ' ')
    cleantext = cleantext.replace('&gt;', ' ')
    cleantext = cleantext.replace('&nbsp;', ' ')
    cleantext = re.sub(' +', ' ', cleantext)
    #print(cleantext)
    return cleantext


def retrieveCoursePage(course_url):
    course_list = pq(url = course_url)
    courses = course_list.find('tbody>tr>td:nth-child(3)')
    course_name = []
    course_num = 50
    index = 0
    for course in courses.items():
        index += 1
        print(course.text())
        course_name.append(course.text())
        if index >= course_num:
            return ','.join(course_name) + "- More courses and detail on UQ website"
    return ','.join(course_name)


def retrieveProgramPage(program_url):
    browser.get(url = program_url)
    browser.save_screenshot('screenshot.png')

    try:
        if browser.find_element_by_xpath("//a[text()=\"I'm an international student\"]"):
            browser.find_element_by_xpath("//a[text()=\"I'm an international student\"]").click()
    except:
        print("You already on international student page!")
    try:
        raw_title = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//h1')))
        title = cleanHtml(raw_title.text)
        print(title)

        htmlPage = pq(browser.find_element_by_css_selector("html").get_attribute('innerHTML').replace('&gt;', '>'))

        # Program description
        program_description = htmlPage.find("[data-sinet='WHYSTUDY']").text()
        description = cleanHtml(program_description)
        print(description)

        # Program details
        program_code = htmlPage('.program__table').find("[data-sinet='CODE']").text()
        QTAC_code = htmlPage('.program__table').find("[data-sinet='StudentInfo > Domestic > QTAC > QTAC_KEY']").text()
        program_faculty = htmlPage('.program__table').find("[data-sinet='Faculty > FACULTY_KEY']").text()
        duration = htmlPage('.program__table').find("[data-sinet='StudentInfo > International > PROGRAM_DURATION']").text()
        commencing = htmlPage('.program__table').find("[data-sinet='Semester']").text()
        program_level = htmlPage('.program__table').find("[data-sinet='LEVEL_VALUE']").text()
        units = htmlPage('.program__table').find("[data-sinet='UNITS']").text()
        delivery_location = htmlPage('.program__table').find("[data-sinet='LOCATION']").text()
        AQF = htmlPage('.program__table').find("[data-sinet='AQF_LEVEL']").text()
        CRICOS_code = htmlPage('.program__table').find("[data-sinet='StudentInfo > International > CRICOSCODE OR Overridden']").text()

        print(program_code)
        print (QTAC_code)
        print(program_faculty)
        print(duration)
        print(commencing)
        print(program_level)
        print(units)
        print(delivery_location)
        print(AQF)
        print(CRICOS_code)

        # Majors
        majors = []
        majorTitles = htmlPage.find('h3[data-sinet="[Plan] TITLE"]')
        for majorTitle in majorTitles.items():
            print(majorTitle.text())
            majors.append(majorTitle.text())
        majors = ','.join(majors)

        # Fees and scholarships
        browser.find_element_by_xpath("//a[text()='Fees and scholarships']").click()
        fee = htmlPage.find('span[data-sinet="StudentInfo > Domestic > IndicativeFee > CSP"]').text()
        print(fee)

        # Courses
        course_url_pyquery = htmlPage.find('#program-structure > a:nth-child(2)')
        course_url = course_url_pyquery.attr['href']
        print(course_url)
        courses = "Sorry! The course list is not available."
        if course_url is not None:
            courses = retrieveCoursePage(course_url)

        # Entry requirements
        entry_requirements = htmlPage.find('#entry-requirements')
        entry_requirement = cleanHtml(entry_requirements.text().replace('Entry requirements', ''))
        print(entry_requirement)

        cur.execute('''INSERT into international_Program (title, overview, program_code, QTAC_code, faculty, duration, commencing, program_level, unit, delivery_location, AQF, CRICOS_code, entry_requirement, major, fee, course)
                                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (
            title, description, program_code, QTAC_code, program_faculty, duration, commencing, program_level, units, delivery_location, AQF, CRICOS_code, entry_requirement, majors, fee, courses))
        conn.commit()
    except TimeoutException:
        print('No such program for international student')


# retrieve one of three  pages
def retrievePage(page):
    programList = page.find('.program__secondary-link')
    for program in programList.items():
        result_url = baseURL + program.attr['href']
        retrieveProgramPage(result_url)


# Undergraduate, Postgraduate, Research
def retrieveTriPages():
    url1 = 'https://future-students.uq.edu.au/study/find-a-program/listing/undergraduate'
    underPage = pq(url = url1)
    retrievePage(page = underPage)

    url2 = 'https://future-students.uq.edu.au/study/find-a-program/listing/postgraduate'
    postPage = pq(url = url2)
    retrievePage(page = postPage)

    url3 = 'https://future-students.uq.edu.au/study/find-a-program/listing/research'
    rsPage = pq(url = url3)
    retrievePage(page = rsPage)


retrieveTriPages()
