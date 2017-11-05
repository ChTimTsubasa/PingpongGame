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
	context['user'] = request.user
	return render(request, 'UserMainPage.html', context)


@transaction.atomic
@login_required	
def create_room(request):
	context = {}
	player = Player.objects.get(user=request.user)
	
	# if not player.current_game:
	# 	print ("here")
	# 	game = player.create_new_game()
	# else:
	# 	print("ha")
	# 	game = player.current_game
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

	if request.method == 'GET':
		joined_game = current_player.join_game_random()

		#To do-----if room is full, try to find an empty room for the user

		# if Game.join_as_opponent(joined_game, current_player) == 0:
		# 	errors.append('You can not join the room, its currently full')
		# 	context['errors'] = errors
		# 	return render(request, 'UserMainPage.html', context)

		#For test, define winner
		joined_game[0].winner = current_player
		joined_game[0].save()
		context['game'] = joined_game[0].id

	if request.method == 'POST':
		join_form =  JoinRoomForm(request.POST)
		if not join_form.is_valid():
			return render(request, 'UserMainPage.html', context)

		room_id = request.POST['room_id']
		# game = get_object_or_404(Game, id=room_id)

		game = current_player.join_game_by_id(room_id)

		if Game.join_as_opponent(game, current_player) == 0:
			errors.append('You can not join the room, its currently full')
			context['errors'] = errors
			return render(request, 'UserMainPage.html', context)

		#For test, define winner
		game.winner = current_player
		game.save()
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
	context['games'] = games
	context['current_user'] = current_user

	return render(request, 'ScoreBoard.html', context)
