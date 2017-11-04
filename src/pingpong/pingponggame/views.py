from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, Http404
from django.http import HttpResponse

#Import model for application
from pingponggame.models import *
#Import Django forms
from pingponggame.forms import *

# Registration Page
@transaction.atomic
def registration(request):
	context = {}

	#If get request, just display web page
	if request.method != 'POST':
		context['user_form'] = UserForm()
		context['password_form'] = PasswordForm()
		context['player_form'] = PlayerForm()
		return render(request, 'Registration.html', context)

	user_form = UserForm(request.POST)
	password_form = PasswordForm(request.POST)
	
	context['user_form'] = user_form
	context['password_form'] = password_form
	context['player_form'] = PlayerForm()

	if not user_form.is_valid() or \
		not password_form.is_valid():
		print (request.POST)
		return render(request, 'Registration.html', context)

	newuser = User.objects.create_user(username=request.POST['username'],
									   password=request.POST['password'],
									   first_name=request.POST['first_name'],
									   last_name=request.POST['last_name'])
	
	newplayer = Player(user = newuser)
	player_form = PlayerForm(request.POST, instance=newplayer)
	newplayer = player_form.save()
	newplayer.save()

	return redirect(reverse('main'))


# Render the usermainpage
@transaction.atomic
@login_required	
def main(request):
	context = {}
	context['form'] = JoinRoomForm()
	return render(request, 'UserMainPage.html', context)


@transaction.atomic
@login_required	
def create_room(request):
	context = {}
	player = Player.objects.get(user=request.user)
	
	if not player.current_game:
		print ("here")
		game = player.create_new_game()
	else:
		print("ha")
		game = player.current_game

	context["game"] = game.id
	context["player"] = player.id

	return render(request, 'GameRoom.html', context)

@transaction.atomic
@login_required	
def get_players_info(request, game_id):
	context = {}
	game = get_object_or_404(Game, id=game_id)
	
	context['creator'] = game.creator
	context['opponent'] = game.opponent

	return render(request, 'Player.json', context, content_type='application/json')


# Render the gameroom
@transaction.atomic
@login_required
def join_room(request):
	context = {}
	if request.method == 'GET':
		pass

	if request.method == 'POST':
		pass

	return render(request, 'GameRoom.html', {})


# Render the ScoreBoard
@transaction.atomic
@login_required	
def scoreboard(request):
	context = {}

	current_user = request.user
	games = Game.objects.all()
	player = get_object_or_404(Player, user=current_user)
	context['games'] = games
	context['current_user'] = current_user

	return render(request, 'ScoreBoard.html', context)