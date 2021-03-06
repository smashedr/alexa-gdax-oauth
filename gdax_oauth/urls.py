from django.contrib import admin
from django.conf.urls import url, include

from login import views as home

urlpatterns = [
    url(r'^$', home.do_connect, name='home'),
    url(r'connect/', home.do_connect, name='connect'),
    url(r'authenticate/', home.do_login, name='authenticate'),
    url(r'token/', home.get_token, name='token'),
    url(r'success/', home.has_success, name='success'),
    url(r'error/', home.has_error, name='error'),
    url(r'privacy/', home.privacy_policy, name='privacy'),
    url(r'^api/', include('api.urls')),
    url(r'^admin/', admin.site.urls, name="django_admin"),
]
