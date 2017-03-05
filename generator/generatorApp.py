from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2 import Environment
# example with jinja2
template = Template('Hello {{ name }}!')
result = template.render(name='John Doe')
print(result)

loader = Environment(loader=FileSystemLoader('./'))
js_template = loader.get_template('template.js')
result_js_string = js_template.render(name='hahaha')
print(result_js_string)

