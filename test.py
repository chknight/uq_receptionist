# -*- coding: utf-8 -*-

import os, os.path, codecs
import json
import csv
import operator
import MySQLdb
from nltk.corpus import stopwords

conn = MySQLdb.connect(host= "localhost",
                  user="root",
                  passwd="17255832",
                  db="robot")
cursor = conn.cursor()

keywords = {}
with open("general_question.csv", "rb") as in_file:
    reader = csv.reader(in_file)
    index = 1
    for data in reader:
        text = data[1].lower()
        text = text.replace("?", "")
        text = text.replace("uq", "")
        words = text.split(" ")
        filtered_words = [word for word in words if word not in stopwords.words('english')]
        insert = ""
        for filtered in filtered_words:
            if (filtered != ""):
                insert = insert+filtered+","
        print insert
        try:
            cursor.execute('insert into generalKeywords values("%s", "%s")' % \
             (index, insert))
            conn.commit()
        except MySQLdb.Error as e:
            print e
        index=index+1

conn.close()