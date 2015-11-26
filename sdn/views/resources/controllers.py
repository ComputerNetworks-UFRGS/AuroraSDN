import logging
from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from sdn.helpers import session_flash
from sdn.models.controller import Controller, CONTROLLER_CHOICE
from django import forms
from django.shortcuts import render_to_response, redirect
from django.http import Http404
from sdn.models.floodlight import Floodlight
import time

# Configure logging for the module name
logger = logging.getLogger(__name__)
active_menu = "Resources"


@login_required
def index(request):
    t = loader.get_template('controllers.html')
    controller_list = Controller.objects.all()
    view_vars = {
        'active_menu': active_menu,
        'title': "Controllers List",
        'actions': [{'name': "New Controller",
        'url': "/AuroraSDN/sdn/resources/controllers/new/"}]
    }
    c = Context({
        'controller_list': controller_list,
        'view_vars': view_vars,
        'request': request,
        'flash': session_flash.get_flash(request)
    })
    return HttpResponse(t.render(c))


# noinspection PyBroadException
@login_required
def sync(request, controller_id):
    try:
        controller = Controller.objects.get(pk=controller_id)
    except Controller.DoesNotExist:
        raise Http404
    # Deleting existing switches in db
    # Switch.objects.all().delete()
    # Host.objects.all().delete()
    if hasattr(controller, 'floodlight'):
        try:
            controller.floodlight.sync()
            session_flash.set_flash(request, "Controller %s was successfully sync!" %
            str(controller))
            logger.debug("Controller %s was successfully sync!" % str(controller))
        except:
            session_flash.set_flash(request, "Controller %s was not sync!" %
            str(controller), 'danger')
    else:
        session_flash.set_flash(request, "Controller %s was not sync!" %
        str(controller), 'danger')
        logger.debug("Controller %s was not sync!" % str(controller))
    return redirect('sdn-controllers-index')

#Form for new Switch creation
class ControllerForm(forms.Form):
    action = "/AuroraSDN/sdn/resources/controllers/new/"
    # Ip address
    ip_address = forms.CharField(max_length=50, label='IP Address')

    # REST API Port
    listen_port = forms.CharField(max_length=10, label='REST API listen port')

    # Name
    name = forms.CharField(max_length=50, label='Name')

    # Description
    description = forms.CharField(max_length=100, label='Description')

    # Controller type
    controller_type = forms.ChoiceField(choices=CONTROLLER_CHOICE, label='Controller type')


@login_required
def new(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ControllerForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            if form.cleaned_data['controller_type'] == 'f':
                c = Floodlight()
            else:
                c = Controller()
            c.ip_address = form.cleaned_data['ip_address']
            c.listen_port = form.cleaned_data["listen_port"]
            c.name = form.cleaned_data['name']
            c.description = form.cleaned_data['description']
            c.controller_type = form.cleaned_data['controller_type']
            c.last_synchronization_time = int(time.time())
            c.save()

            session_flash.set_flash(request,
            "New Controller successfully created")
            return redirect('sdn-controllers-index')  # Redirect after POST
    else:
        form = ControllerForm()  # An unbound form

    view_vars = {
        'active_menu': active_menu,
        'title': "New Controller",
        'actions': [
            {'name': "Back to List", 'url': "/AuroraSDN/sdn/resources/controllers/"},
        ]
    }
    c = RequestContext(request, {
        'form': form,
        'view_vars': view_vars,
        'request': request,
        'flash': session_flash.get_flash(request)
    })
    return render_to_response('sdn/base-form.html', c)


@login_required
def delete(request, controller_id):
    try:
        controller = Controller.objects.get(pk=controller_id)
    except Controller.DoesNotExist:
        raise Http404

    controller.delete()
    session_flash.set_flash(request, "Controller %s was successfully deleted!" %
    str(controller))
    logger.debug("Controller %s was successfully deleted!" % str(controller))

    return redirect('sdn-controllers-index')
