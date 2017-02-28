import nltk
import MySQLdb
from cPickle import dump
connection = MySQLdb.connect('localhost', 'root', '19941005', 'uq')
connection.set_character_set('utf8')
connection.cursor().execute('SET NAMES utf8;')
connection.cursor().execute('SET CHARACTER SET utf8;')
connection.cursor().execute('SET character_set_connection=utf8;')


def fetch_all_data():
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM COURSE''')
    results = cursor.fetchall()
    print len(results)
    for result in results:
        print result[9]
    return results

allData = fetch_all_data()
courseDictionary = {}
for data in allData:
    courseDictionary[data] = "course"

output = open('course_code.pkl', 'wb')
dump(courseDictionary, output, -1)
output.close()
