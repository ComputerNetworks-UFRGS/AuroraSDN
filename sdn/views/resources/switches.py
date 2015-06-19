import logging
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from sdn.helpers import session_flash
from sdn.models.switch import Switch

# Configure logging for the module name
logger = logging.getLogger(__name__)
active_menu = "Resources"

@login_required
def index(request):
    t = loader.get_template('switches.html')
    switch_list = Switch.objects.all()
    view_vars = {
        'active_menu': active_menu,
        'title': "Switches List"
    }
    c = Context({
        'switch_list': switch_list,
        'view_vars': view_vars,
        'request': request,
        'flash': session_flash.get_flash(request)
    })
    return HttpResponse(t.render(c))