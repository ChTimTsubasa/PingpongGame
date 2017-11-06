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
	player = get_object_or_404(Player, user=request.user)
	context['form'] = JoinRoomForm()
	context['user'] = request.user
	context['player'] = player
	return render(request, 'UserMainPage.html', context)

@transaction.atomic
@login_required	
def create_room(request):
	context = {}
	player = Player.objects.get(user=request.user)

	game = player.create_new_game()

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
	errors = []
	current_user = request.user
	current_player = get_object_or_404(Player, user=current_user)
	context['player'] = current_player.id
	print (Game.objects.filter(opponent=None, completed=None))
	if request.method == 'GET':
		joined_game = current_player.join_game_random()
		if not joined_game:
			errors.append('There is no room available now')
			context['errors'] = errors
			context['form'] = JoinRoomForm()
			return render(request, 'UserMainPage.html', context)

		context['game'] = joined_game.id

	if request.method == 'POST':
		join_form =  JoinRoomForm(request.POST)
		if not join_form.is_valid():
			context['form'] = join_form
			return render(request, 'UserMainPage.html', context)

		room_id = request.POST['room_id']
		
		game = current_player.join_game_by_id(room_id)
		context['game'] = game.id

	return render(request, 'GameRoom.html', context)


# Render the ScoreBoard
@transaction.atomic
@login_required	
def scoreboard(request):
	context = {}

	current_user = request.user
	games = Game.objects.all()
	player = get_object_or_404(Player, user=current_user)
	context['latest_game'] = -1
	context['current_user'] = current_user

	return render(request, 'ScoreBoard.html', context)

@transaction.atomic
@login_required
def get_latest_game(request, game_id):
	context = {}
	games = Game.get_newer_game(game_id)
	print(games)
	if not games.last():
		context['latest_game'] = game_id
	else:
		context['latest_game'] = games.last().id

	context['games'] = games

	return render(request, 'Games.json', context, content_type='application/json')