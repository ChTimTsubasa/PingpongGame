from django.db import models
from django.db.models import Max

from django.contrib.auth.models import User

from django.template.loader import render_to_string


from channels import Group

import datetime

# Player model
class Player(models.Model):
	# user field for authentication
	user = models.OneToOneField(User)
	
	# nickname of the user
	nickname = models.CharField(default = '', max_length=100, blank = True)
	
	# score of the user in the current game. When there is a current game
	score = models.IntegerField(default=0)

	# if the user has clicked ready in the game
	ready = models.BooleanField(default=False)

	# current game that the player is playing
	currentGame = models.ForeignKey(
		'CurrentGame',
		models.SET_NULL,	# on delete
		blank=True,
		null=True,
	)

	def __unicode__(self):
		return 'Player #{0}'.format(self.pk)

	def join_game(self, game):
		if self.currentGame:
			# TODO more appropriate error should be thrown
			raise AttributeError('you are already in a game')
		self.currentGame = game
		self.ready = False
		self.save()

	def leave_game(self, game):
		if self.currentGame != game:
			# TODO more appropriate error should be thrown
			raise AttributeError('you are not in this game')
		self.currentGame = None
		self.ready = False
		self.save()
	
	def set_ready(self, ready_state):
		self.ready = ready_state
		self.save()

	def add_score(self):
		self.score = self.score + 1
		self.save()

	@property
	def html(self):
		return render_to_string("Player.html", {"player":self}).replace("\n", "")

# TODO add the source of reference
# Game Model
class CurrentGame(models.Model):
	JOIN_STATE = 0
	READYING_STATE = 1
	GAMING_STATE = 2

	GAME_STATE = (
		(JOIN_STATE, 'Join'),
		(READYING_STATE, 'Ready'),
		(GAMING_STATE, 'Gaming'),
	)
	# game state
	state = models.IntegerField(choices=GAME_STATE, default=JOIN_STATE)

	max_player_num = models.IntegerField(default=2)

	# The score that if some one get reach, the game ends
	max_score = models.IntegerField(default=3)

	#Dates
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return 'Game #{0}'.format(self.pk)

	@staticmethod
	def get_game_random():
		games = CurrentGame.objects.filter(state=CurrentGame.JOIN_STATE)
		for game in games:
			if game.player_set.count() < game.max_player_num:
				return game
		return None

	@staticmethod
	def get_game_by_id(id):
		try:
			game = CurrentGame.objects.filter(state=CurrentGame.JOIN_STATE).get(pk=id)
		except CurrentGame.DoesNotExist:
			return None

		if game.player_set.count() < game.max_player_num:
			return game
		
		return None

	# The room is full of players
	def full(self):
		return self.player_set.count() == self.max_player_num

	# All players in the room is ready
	def all_ready(self):
		return self.player_set.filter(ready=True).count() == self.max_player_num

	# Find opponent
	# this is just for two players game
	def find_opponent(self, player):
		return self.player_set.exclude(id=player.id).first()

class GameRecord(models.Model):
	#Dates
	created = models.DateTimeField(blank=True)
	ended = models.DateTimeField(auto_now=True)

	# Participants of this game
	participants = models.ManyToManyField(
		Player,
		through='Participant'
	)

	@staticmethod
	def record(game):
		gr = GameRecord.objects.create(
			created=game.created,
		)
		for player in game.player_set.all():
			participant = Participant(player=player, gameRecord=gr, score=player.score)
			participant.save()
		
		# game.player_set.update(score=0, ready=False)
		# game.delete()

		gr.save()
		return gr
	
	def winner(self):
		winner = Participant.objects.filter(gameRecord=self).order_by('-score')[0]
		return winner

	@property
	def html(self):
		return render_to_string("Game.html", {"game":self}).replace("\n", "")

class Participant(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	gameRecord = models.ForeignKey(GameRecord, on_delete=models.CASCADE)
	
	# The score of the user
	score = models.IntegerField(default=0)

class Pad():
	position_X = 0.0
	position_Y = 0.0
	time_stamp = 0
	def __init__(self, message):
		self.position_X = message['x']
		self.position_Y = message['y']
		self.time_stamp = message['ts']

	def update(self, message):
		self.position_X = message['x']
		self.position_Y = message['y']
		self.time_stamp = message['ts']

	def message(self):
		content = {
			'TYPE': 'PAD',
			'x': self.position_X,
			'y': self.position_Y,
			'ts': self.time_stamp,
		}
		return content

class Ball(models.Model):
	def __init__(self, message):
		self.position_X = message['p_x']
		self.position_Y = message['p_y']
		self.velocity_X = message['v_x']
		self.velocity_Y = message['v_y']
	
	def message(self):
		content = {
			'TYPE': 'BALL',
			'p_x': self.position_X,
			'p_y': self.position_Y,
			'v_x': self.velocity_X, 
			'v_y': self.velocity_Y,
		}
		return content