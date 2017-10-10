from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2 import Environment
import pymysql


conn = pymysql.connect('localhost', 'root', 'bcbcslcj0310', 'uq_robot_receptionist', charset='utf8')
cur = conn.cursor()
# Error: UnicodeEncodeError: 'latin-1' codec can't encode character
cur.execute('SET NAMES utf8;')
cur.execute('SET CHARACTER SET utf8;')
cur.execute('SET character_set_connection=utf8;')


# process string to generate json
def processString(string):
    process1 = string.replace('\n', ' ').replace('\"', '\\",').replace('>', 'to')
    process2 = process1.replace('(', '').replace(')', '').replace(':', '')
    processed = process2.replace('  ', ' ')
    return processed


# fetch the value according to the entity_name
def fetchValueFromDB(entry):
    tableName = entry['table_name']
    branchName = entry['column_name']
    tableKey = entry['key']
    print(tableName)
    print(branchName)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from %s" % tableName
    cur.execute(sql)
    fetch_result = []
    row = cur.fetchone()
    while row is not None:
        if row[branchName]:
            fetch_result.append({ 'value': processString(row[branchName]), 'key': processString(row[tableKey])})
        row = cur.fetchone()
    return fetch_result


# fetch all entities in table 'entry'
def fetchEntityfromDB():
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from entry"
    cur.execute(sql)
    rows = cur.fetchall()
    return rows


entities = fetchEntityfromDB()


def template_generator(reference_value, synonym_entity):
    all_value = []
    for value in reference_value:
        all_value.append(value)
    if len(all_value):
        load = Environment(loader=FileSystemLoader('./entities_Template/'))
        entity_template = load.get_template('en_Template.json')
        name = synonym_entity['entity_name']
        entityId = synonym_entity['entity_name']
        outputString = entity_template.render(entity_name = name, entity_id = entityId, entities = all_value)

        # write to entity file
        with open("/Users/tree/Documents/workspace/uq_robot_receptionist/src/entities/" + name + ".json", 'bw') as output:
            output.write(outputString.encode('utf-8'))


for entity in entities:
    value = fetchValueFromDB(entity)
    template_generator(value, entity)

