from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [

    # url(r'^$', Home.as_view(), name='home'),

    url(r'^api/', include('apps.api.urls', namespace='api')),

    #url(r'^admin/', admin.site.urls),

    #url(r'^signal/', include('apps.signal.urls', namespace='signal')) # REST API for signal
]
