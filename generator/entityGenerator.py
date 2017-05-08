# -*- coding: utf-8 -*-
from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2 import Environment
import MySQLdb


# set up database connection
connection = MySQLdb.connect('localhost', 'root', '19941005', 'uq_receptionist')
connection.set_character_set('utf8')
connection.cursor().execute('SET NAMES utf8;')
connection.cursor().execute('SET CHARACTER SET utf8;')
connection.cursor().execute('SET character_set_connection=utf8;')

#define some const variable
max_entity = 15000

# process string to generate json
def processString(string):
    processed = string.replace('\n', ' ').replace('\"', '\\",').replace('>', 'to')
    processed = processed.replace('(', '').replace(')', '').replace(':', '')
    processed = processed.replace('  ', ' ')
    return processed

# fetch the value according to the entity
def fetchValuesFromDataBase(entry):
    tablename = entry['tablename']
    fieldname = entry['fieldname']
    tablekey = entry['key']
    print(tablename)
    print(fieldname)
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    queryString = "SELECT * FROM %s" % tablename
    cursor.execute(queryString)
    results = []
    row = cursor.fetchone()
    while row is not None:
        if row[fieldname]:
            results.append({ 'value': processString(row[fieldname]), 'key': processString(row[tablekey])})
        row = cursor.fetchone()
    return results

def fetchEntitesFroDataBase():
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''SELECT * FROM entry''')
    rows = cursor.fetchall()
    return rows

entries = fetchEntitesFroDataBase()


def generateTemplates(valueToPut, oneEntry):
    currentNumber = 0
    index = 1
    valuesInOneJson = []
    for value in valueToPut:
        valuesInOneJson.append(value)
        if currentNumber >= max_entity:
            loader = Environment(loader=FileSystemLoader('./template/'))
            entry_template = loader.get_template('entityTemplate.json')
            name = oneEntry['name'] + str(index)
            entryId = oneEntry['name'] + str(index)
            resultString = entry_template.render(entityName=name, id=entryId, entries=valuesInOneJson)
            # write to entry file
            with open("./generatedResult/" + name + ".json", 'bw') as out:
                out.write(resultString.encode('utf-8'))
            valuesInOneJson = []
            currentNumber = 0
            index += 1
        else:
            currentNumber += 1
    if len(valuesInOneJson):
        loader = Environment(loader=FileSystemLoader('./template/'))
        entry_template = loader.get_template('entityTemplate.json')
        name = oneEntry['name'] + str(index)
        entryId = oneEntry['name'] + str(index)
        resultString = entry_template.render(entityName=name, id=entryId, entries=valuesInOneJson)
        # write to entry file
        with open("./generatedResult/" + name + ".json", 'bw') as out:
            out.write(resultString.encode('utf-8'))


for entry in entries:
    values = fetchValuesFromDataBase(entry)
    generateTemplates(values, entry)
