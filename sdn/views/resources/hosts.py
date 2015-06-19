import logging
from django.http import HttpResponse
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from sdn.helpers import session_flash
from sdn.models.host import Host

# Configure logging for the module name
logger = logging.getLogger(__name__)
active_menu = "Resources"

@login_required
def index(request):
    t = loader.get_template('hosts.html')
    host_list = Host.objects.all()
    view_vars = {
        'active_menu': active_menu,
        'title': "Hosts List"
    }
    c = Context({
        'host_list': host_list,
        'view_vars': view_vars,
        'request': request,
        'flash': session_flash.get_flash(request)
    })
    return HttpResponse(t.render(c))