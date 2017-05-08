# -*- coding: utf-8 -*-

import os, os.path, codecs
import json
import csv
import operator
import MySQLdb
from nltk.corpus import stopwords

conn = MySQLdb.connect(host= "localhost",
                  user="root",
                  passwd="19941005",
                  db="uq_receptionist")
cursor = conn.cursor(MySQLdb.cursors.DictCursor)


# fetch general question
def fetch_data_from_database():
    cursor.execute('''SELECT * FROM general_question''')
    result = cursor.fetchall()
    print(result)
    return result

data = fetch_data_from_database()

for row in data:
    text = row['question'].lower()
    text = text.replace("?", "")
    text = text.replace("uq", "")
    text = text.replace('"', "")
    text = text.replace('(', "")
    text = text.replace(')', '')
    text = text.replace("what's", '')
    text = text.replace("'s", '')
    words = text.split(" ")
    filtered_words = [word for word in words if word not in stopwords.words('english')]
    insert = []
    for filtered in filtered_words:
        if filtered != "" and filtered not in insert:
            insert.append(filtered)
    insert.sort()
    insert = ','.join(insert)
    cursor.execute("""
       UPDATE general_question
       SET keyword=%s
       WHERE id=%s
        """, [insert, row['id']])
conn.commit()
conn.close()
