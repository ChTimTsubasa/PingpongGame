from django.conf.urls import url

from pingponggame import views as pviews

from django.contrib.auth.views import login, logout_then_login

urlpatterns = [
	url(r'^registration$', pviews.registration, name="registration"),
	url(r'^login$', login, {'template_name':'Login.html'}, name="login"),
	url(r'^logout$', logout_then_login, name="logout"),
	url(r'^main', pviews.usermainpage, name="main"),
	url(r'^gameRoom$', pviews.gameRoom, name="gameRoom"),
]