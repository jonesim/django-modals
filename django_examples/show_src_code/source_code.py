import inspect
from django.utils.html import escape
from django.template import loader


def code_block(file, line_no, code):
    return f'''<div class="bg-secondary text-light">{file}<span class="pl-4">Line: <b>{line_no}</b></span></div>
               <pre><code class="python-html">{code}</code></pre>'''


def template_source(template_name, code_ptr=None):
    source = loader.get_template(template_name).template.source
    if code_ptr:
        code_location = source.find('>', source.find(f'<data value="{code_ptr}"')) + 1
        code_end = source.find('</data>', code_location)
        lines = source[:code_location].count('\n') + 1
    else:
        lines = 0
        code_location = 0
        code_end = len(source)
    return code_block(template_name, lines, escape(source[code_location: code_end]))


def html_code(python_object):
    return code_block(inspect.getsourcefile(python_object), inspect.getsourcelines(python_object)[1],
                      escape(inspect.getsource(python_object)))
