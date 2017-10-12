from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [

    # url(r'^$', Home.as_view(), name='home'),

    url(r'^admin/', admin.site.urls),
]
