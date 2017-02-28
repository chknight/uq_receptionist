import nltk
import tornado.ioloop
import tornado.web
import MySQLdb

input.close()
connection = MySQLdb.connect('localhost', 'root', '19941005', 'uq_receptionist')
connection.set_character_set('utf8')
connection.cursor().execute('SET NAMES utf8;')
connection.cursor().execute('SET CHARACTER SET utf8;')
connection.cursor().execute('SET character_set_connection=utf8;')

keyword = {'name': 0, 'description': 1, 'level': 3, 'unit': 4, 'content': 5, 'assessment': 6, 'coordinator': 7, 'duration': 8, 'code': 9}


def fetchDataFromDataBase(key, target):
    cursor = connection.cursor()
    print(key)
    print(target)
    key.upper()
    cursor.execute('''SELECT * FROM course WHERE name=%s''', key)
    result = cursor.fetchone()

    return result[keyword[target]]

class MainHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        self.write("Hello, world")

    def post(self):
        self.set_header("Content-Type", "text/plain")
        massage = self.get_body_argument("name")
        target = self.get_body_argument('target')
        result = fetchDataFromDataBase(massage, target)
        self.write("{result:" + result + "}")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
