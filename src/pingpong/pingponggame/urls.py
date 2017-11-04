from django.conf.urls import url

from pingponggame import views as pviews

from django.contrib.auth import views as aviews

urlpatterns = [
	url(r'^registration$', pviews.registration, name="registration"),
	url(r'^login$', aviews.login, {'template_name':'Login.html'}, name="login"),
	url(r'^logout$', aviews.logout_then_login, name="logout"),
	url(r'^main', pviews.main, name="main"),
	url(r'^scoreboard$', pviews.scoreboard, name="scoreboard"),
	url(r'^createRoom$', pviews.create_room, name="createRoom"),
	url(r'^joinRoom$', pviews.join_room, name="joinRoom"),
]