from django.db import models
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

	# current game that the player is playing
	currentGame = models.ForeignKey(
		'CurrentGame',
		models.SET_NULL,	# on delete
		blank=True,
		null=True,
	)

	@property
	def html(self):
		return render_to_string("Player.html", {"player":self}).replace("\n", "")

# TODO add the source of reference
# Game Model
class CurrentGame(models.Model):
	JOIN_STATE = 0
	READY_STATE = 1
	GAMING_STATE = 2
	PAUSE_STATE = 3

	GAME_STATE = (
		(JOIN_STATE, 'Join'),
		(READY_STATE, 'Ready'),
		(GAMING_STATE, 'Gaming'),
		(PAUSE_STATE, 'Pause'),
	)
	# game state
	state = models.IntegerField(choices=GAME_STATE, default=JOIN_STATE)

	max_player_num = models.IntegerField(default=2)

	max_score = models.IntegerField(default=3)

	#Dates
	completed = models.DateTimeField(null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return 'Game #{0}'.format(self.pk)

	@staticmethod
	def get_game_random():
		games = Game.objects.filter(state=JOIN_STATE)
		for game in games:
			if game.player_set.count() < game.max_player_num:
				return game
		return None

	@staticmethod
	def get_game_by_id(id):
		try:
			game = Game.objects.filter(state=JOIN_STATE).get(pk=id)
		except Game.DoesNotExist:
			return None

		if game.player_set.count() < game.max_player_num:
			return game
		
		return None


class GameRecord(models.Model):
	# Winner of this game
	winner = models.ForeignKey(
		Player,
		on_delete=models.DO_NOTHING,
		related_name='win_game'
	)

	# Participants of this game
	participants = models.ManyToManyField(
		Player,
		through='Participant'
	)

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