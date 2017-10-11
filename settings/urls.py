from django.conf.urls import include, url
from django.contrib import admin

from apps.service.views.service import Home
from apps.user.views import auth as user_auth_views

urlpatterns = [

    # url(r'^$', Home.as_view(), name='home'),

    url(r'^admin/', admin.site.urls),
]
