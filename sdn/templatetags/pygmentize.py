# Enables syntax highlighting with pygment
import re
from django import template 
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
 
register = template.Library()
 
@register.filter(name='pygmentize') 
def pygmentize(value):
    code = highlight(value, PythonLexer(), HtmlFormatter())
    return mark_safe(code)

@register.filter(name='pygmentize_css') 
def pygmentize_css(value):
    css = '<style type="text/css">code{padding:0; border:0;}' + HtmlFormatter().get_style_defs('code.python') + '</style>'
    return mark_safe(css)
