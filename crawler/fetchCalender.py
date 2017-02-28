# get the information from uq calender
from pyquery import PyQuery as jquery


# retrieve the information in calender page
def retrieve_page(calender_page):
    all_li = calender_page.items('li.event_row')
    for li in all_li:
        # get the event name
        print('event name:')
        print(li.find('ul').find('li.description-calendar-view').find('a').text())
        # get the event period
        print('event period')
        print(li.find('ul').find('li.first').text())
        print('\n')


# start the program
def retrieve_pages():
    url = "http://www.uq.edu.au/events/calendar_view.php?category_id=16"
    page = jquery(url=url)
    retrieve_page(page)

retrieve_pages()