from django.contrib import admin
from django.conf.urls import url

from login import views as home

urlpatterns = [
    url(r'^$', home.home, name='home'),
    url(r'authenticate/', home.do_login, name='authenticate'),
    url(r'success/', home.success, name='success'),
    url(r'^admin/', admin.site.urls, name="django_admin"),
]
