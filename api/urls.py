from django.conf.urls import url

from api import views as api

urlpatterns = [
    url(r'^$', api.home, name='home'),
    url(r'accounts/', api.accounts, name='accounts'),
]
