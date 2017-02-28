import MySQLdb

connection = MySQLdb.connect('localhost', 'root', '19941005', 'uq_receptionist')
connection.set_character_set('utf8')
connection.cursor().execute('SET NAMES utf8;')
connection.cursor().execute('SET CHARACTER SET utf8;')
connection.cursor().execute('SET character_set_connection=utf8;')


def fetch_all_data():
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM course''')
    results = cursor.fetchall()
    for result in results:
      index = result[0].index("(")
      if result[0][index - 1] == " ":
        replace = result[0][0:index - 1]
      else:
        replace = result[0][0:index]
      print replace  
      cursor.execute ("""
       UPDATE course
       SET name=%s
       WHERE id=%s
        """, (replace, result[2]))
    connection.commit()
    connection.close()
fetch_all_data()