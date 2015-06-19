import logging
from django.template.context import RequestContext
from django.shortcuts import render_to_response, redirect
from sdn.helpers import session_flash  # @UnresolvedImport
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

view_vars = {
    'active_menu': 'Dashboard',
}

@login_required
def index(request):
    view_vars.update({
        'title': 'Dashboard'
    })
    c = RequestContext(request, {
        'view_vars': view_vars,
        'request': request,
        'flash': session_flash.get_flash(request)
    })
    return render_to_response('sdn/pages-index.html', c)


def login_error(request):
    session_flash.set_flash(
        request,
        'Could not authenticate with remote provider!', 'danger'
    )
    logger.debug('Could not authenticate with remote provider!')

    return redirect('home')


def not_implemented(request):
    return HttpResponse("Not Implemented", status=501)

