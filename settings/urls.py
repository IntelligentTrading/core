from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [

    url(r'^api/v3/', include('apps.TA.urls', namespace='redis_api')),
    url(r'^api/', include('apps.api.urls', namespace='api')),

    # url(r'^admin/', admin.site.urls),

]
