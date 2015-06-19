# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('sdn.views',

    # Switches
    url(r'^resources/switches/$', 'resources.switches.index', name='sdn-switches-index'),

    # Hosts
    url(r'^resources/hosts/$', 'resources.hosts.index', name='sdn-hosts-index'),

    # Controller
    url(r'^resources/controllers/$', 'resources.controllers.index', name='sdn-controllers-index'),
    url(r'^resources/controllers/new/$', 'resources.controllers.new'),
    url(r'^resources/controllers/(?P<controller_id>\d+)/delete/$', 'resources.controllers.delete'),
    url(r'^resources/controllers/(?P<controller_id>\d+)/sync/$', 'resources.controllers.sync', name='resources.controllers.sync'),

    # Data Plane
    url(r'^visualizations/data_plane/$', 'visualizations.data_plane.index', name='sdn-visualizations-data_plane-index'),
    url(r'^visualizations/data_plane/(?P<controller_id>\d+)/data/$', 'visualizations.data_plane.getDataPlane', name='sdn-visualization-data_plane-data'),
    url(r'^visualizations/data_plane/controller/(?P<controller_id>\d+)/view/$', 'visualizations.data_plane.selectController', name='sdn-visualizations-data_plane-select-controller'),
    url(r'^visualizations/data_plane/controller/(?P<controller_id>\d+)/configure/$', 'visualizations.data_plane.configureController', name='sdn-visualizations-data_plane-configure-controller'),

)