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
	errors = []
	current_player = get_object_or_404(Player, user=request.user)

	context['player'] = current_player
	if current_player.currentGame:
		errors.append('You are already in a room!!')
		context['errors'] = errors
		context['form'] = JoinRoomForm()
		return render(request, 'UserMainPage.html', context)
	
	joined_game = CurrentGame.objects.create()

	try:
		current_player.join_game(joined_game)
		context['game'] = joined_game.id
		return render(request, 'GameRoom.html', context)
	except AttributeError:
		# Should not reach here, just for safety
		errors.append('You are already in a room!!')
		context['errors'] = errors
		context['form'] = JoinRoomForm()
		return render(request, 'UserMainPage.html', context)
		

@transaction.atomic
@login_required	
def get_players_info(request, game_id):
	context = {}
	player = get_object_or_404(Player, user=request.user)
	game = player.currentGame
	if not game:
		return
	opponent = game.find_opponent(player)
	context['you'] = player
	context['opponent'] = opponent

	return render(request, 'Player.json', context, content_type='application/json')

# Render the gameroom
@transaction.atomic
@login_required
def join_room(request):
	context = {}
	errors = []
	current_user = request.user
	current_player = get_object_or_404(Player, user=current_user)
	context['player'] = current_player
	context['user'] = request.user

	if request.method == 'GET':
		joined_game = CurrentGame.get_game_random()
		if not joined_game:
			errors.append('There is no room available now')
			context['errors'] = errors
			context['form'] = JoinRoomForm()
			return render(request, 'UserMainPage.html', context)

	if request.method == 'POST':
		join_form =  JoinRoomForm(request.POST)
		if not join_form.is_valid():
			context['form'] = join_form
			return render(request, 'UserMainPage.html', context)

		room_id = request.POST['room_id']
		joined_game = CurrentGame.get_game_by_id(room_id)

	try:
		current_player.join_game(joined_game)
		context['game'] = joined_game.id
		return render(request, 'GameRoom.html', context)
	except AttributeError:
		errors.append('You are already in a room!!')
		context['errors'] = errors
		context['form'] = JoinRoomForm()
		return render(request, 'UserMainPage.html', context)

# Render the ScoreBoard
@transaction.atomic
@login_required	
def scoreboard(request):
	context = {}
	current_player = get_object_or_404(Player, user=request.user)
	context['latest_game'] = -1
	context['current_player'] = current_player

	return render(request, 'ScoreBoard.html', context)

@transaction.atomic
@login_required
def get_latest_game(request, game_id):
	context = {}
	games = GameRecord.objects.filter(id__gt = game_id)
	rows = []
	if not games.count():
		context['latest_game'] = game_id
		context['games'] = rows

		return render(request, 'Games.json', context, content_type='application/json')
	
	context['latest_game'] = games.last().id
	for game in games:
		html = render_to_string(
				"Game.html", 
				{'id': game.id,
				 'winner': game.winner().player.nickname,
				 'created': game.created,
				 'ended': game.ended,
				}
			).replace("\n", "")
		rows.append(html)

	context['games'] = rows

	return render(request, 'Games.json', context, content_type='application/json')