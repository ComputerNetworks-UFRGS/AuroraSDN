from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Social auth urls
    url('', include('social.apps.django_app.urls', namespace='social')),
    # Aurora urls
    url(r'^$', 'sdn.views.basic.pages.index', name='home'),
    url(r'^not_implemented/$', 'sdn.views.basic.pages.not_implemented',
        name='not_implemented'),

    # SDN urls
    url(r'^sdn/', include('sdn.urls')),

    # Django Admin
    url(r'^admin/', include(admin.site.urls)),

    # User login/logout
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'sdn/pages-login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'sdn/pages-logout.html'}),
    url(r'^accounts/login-error/$', 'sdn.views.basic.pages.login_error',
        name='login_error'),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        # Debug toolbar urls
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
