from django.conf.urls import url

from pingponggame import views as pviews

from django.contrib.auth.views import login, logout_then_login

urlpatterns = [
	url(r'^registration$', pviews.registration, name="registration"),
	
]