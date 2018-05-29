from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [

    # url(r'^$', Home.as_view(), name='home'),

    url(r'^api/', include('apps.api.urls', namespace='api')),
    url(r'^dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # url(r'^admin/', admin.site.urls),

]
