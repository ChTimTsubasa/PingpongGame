from django.conf.urls import url

from pingponggame import views as pviews

from django.contrib.auth import views as aviews

urlpatterns = [
	url(r'^registration$', pviews.registration, name="registration"),
	url(r'^login$', aviews.login, {'template_name':'Login.html'}, name="login"),
	url(r'^logout$', aviews.logout_then_login, name="logout"),
	url(r'^main', pviews.main, name="main"),
	url(r'^gameRoom$', pviews.gameRoom, name="gameRoom"),
]