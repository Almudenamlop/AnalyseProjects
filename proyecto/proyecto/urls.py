from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'proyecto.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^people/$', 'web.views.people'),			#$no recibe args
	url(r'^(?P<nombre>.+)/(?P<ident>.+)$', 'web.views.person'),
	url(r'^principal/', 'web.views.principal'),
	url(r'^$', 'web.views.principal'),

)