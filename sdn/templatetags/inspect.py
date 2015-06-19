from django import template
from django.template.defaultfilters import linebreaksbr
from django.utils.html import escape
try:
    from django.utils.safestring import mark_safe
except ImportError: # v0.96 and 0.97-pre-autoescaping compat
    def mark_safe(x): return x
from pprint import pformat

def rawdump(x):
    if hasattr(x, '__dict__'):
        d = {
            'str': str(x),
            'unicode': unicode(x),
            'repr': repr(x),
        }
        d.update(x.__dict__)

        # List methods
        for m in dir(x):
            try:
                # Avoid error in protected attributes
                if callable(getattr(x, m)):
                    d.update({m: str(getattr(x, m))})
            except:
                pass

        # Update returned object
        x = d

    output = pformat(x) + '\n'
    return output

def dump(x):
    return mark_safe(linebreaksbr(escape(rawdump(x))))

register = template.Library()
register.filter('rawdump', rawdump)
register.filter('dump', dump)
