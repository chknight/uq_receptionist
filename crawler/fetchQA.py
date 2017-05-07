# get the information from uq calender
from pyquery import PyQuery as jquery


def retrieve_answer_page(answerPage):
    question = answerPage.find('.rn_DataValue').eq(0)
    answer = answerPage.find('.rn_DataValue').eq(1)
    for content in question.contents():
        print(content)
    for child in answer.children():
        if child.tag is 'p':
            print('Node is a p')
            print(child.text.replace('<!--stopindex-->', '').replace('<!--startindex-->', ''))
        elif child.tag is 'blockquote':
            print('Node is blockquote')
            print(child.children())



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