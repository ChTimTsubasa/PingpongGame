from django.db import models
from django.contrib.auth.models import User

from django.template.loader import render_to_string

from channels import Group

import datetime

# Player model
class Player(models.Model):
	user = models.OneToOneField(User)
	current_game = models.ForeignKey('Game', null=True)
	nickname = models.CharField(default = '', max_length=100, blank = True)
	image = models.ImageField(upload_to = "userpictures", blank = True)
	
	@property
	def html(self):
		return render_to_string("Player.html", {"player":self}).replace("\n", "")

	def create_new_game(self):
		new_game = Game.create_new(self)
		self.current_game = new_game
		self.save()
		return new_game

	def join_game_by_id(self, game_id):
		game = Game.get_by_id(game_id)
		if not game:
			return None
		if game.opponent: #game is full already
			return "full"
		self.current_game = game
		self.current_game.add_opponent(self)
		self.save()		
		return game

	def join_game_random(self):
		game = Game.get_available_game()

		if not game:
			return None
		self.current_game = game
		self.current_game.add_opponent(self)
		self.save()
		return game

	def leave_game(self):
		if not self.current_game:
			return
		self.current_game.emit_player(self)
		self.current_game = None
		self.save()

# TODO add the source of reference
# Game Model
class Game(models.Model):
    # Players
	winner = models.ForeignKey(Player, related_name='winner', null=True, blank=True)
	creator = models.ForeignKey(Player, related_name='creator')
	opponent = models.ForeignKey(Player, related_name='opponent',null=True, blank=True)

	#Dates
	completed = models.DateTimeField(null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	#game state
	available_players = models.IntegerField(default=0)
	creator_score = models.IntegerField(default=0)
	opponent_score = models.IntegerField(default=0)

	def __unicode__(self):
		return 'Game #{0}'.format(self.pk)

	@staticmethod
	def get_newer_game(id):
		return Game.objects.filter(winner__isnull=False, id__gt=id).order_by('completed')

	@staticmethod
	def get_available_game():
		return Game.objects.filter(opponent=None, completed=None).first()

	@staticmethod
	def get_by_id(id):
		try:
			return Game.objects.filter(opponent=None, completed=None).get(pk=id)
		except Game.DoesNotExist:
			return None

	@staticmethod
	def create_new(player):
		"""
		Create a new game and game squares
		:param player: the player that created the game
		:return: a new game object
		"""
		# make the game's name from the username and the number of
		# games they've created
		new_game = Game(creator=player)
		new_game.save()

		return new_game

	def add_opponent(self, player):
		self.opponent = player
		self.save()

	def emit_player(self, player):
		if self.opponent == player:
			self.opponent = None
			self.save()
		if self.creator == player:
			if self.opponent:
				self.creator = self.opponent
				self.opponent = None
				self.save()
			else:
				self.delete()

	def mark_complete(self, winner):
		"""
		Sets a game to completed status and records the winner
		"""
		self.winner = winner
		self.completed = datetime.datetime.now()
		self.save()

	def player_ready(self):
		self.available_players = self.available_players + 1
		self.save()

	def player_gone(self):
		self.available_players = self.available_players - 1
		self.save()

	def set_player_score(self, player, score):
		if player == self.creator:
			self.creator_score = score
			self.save()
			print('c')
		elif player == self.opponent:
			self.opponent_score = score
			self.save()
			print('o')
	
	def determine_winner(self):
		print(self.creator_score)
		print(self.opponent_score)
		if self.creator_score == 0 or self.opponent_score == 0:
			return None
		if self.creator_score >= self.opponent_score:
			print("here")
			self.mark_complete(self.creator)
		else:
			print("here2")
			self.mark_complete(self.opponent)
		return self.winner

	@property
	def html(self):
		return render_to_string("Game.html", {"game":self}).replace("\n", "")

class GameObject(models.Model):
	position_X = models.FloatField()
	position_Y = models.FloatField()
	velocity_X = models.FloatField()
	velocity_Y = models.FloatField()
	inverse = models.BooleanField()

class Pad(GameObject):
	def __init__(self, message):
		self.position_X = message['pad_p'][0]
		self.position_Y = message['pad_p'][1]
		self.velocity_X = message['pad_v'][0]
		self.velocity_Y = message['pad_v'][1]

	def message(self):
		content = {
			'TYPE': 'pad',
			'pad_p': [self.position_X, self.position_Y],
			'pad_v': [self.velocity_X, self.velocity_Y],
		}
		return content

class Ball(GameObject):
	def __init__(self, message):
		self.position_X = message['ball_p'][0]
		self.position_Y = message['ball_p'][1]
		self.velocity_X = message['ball_v'][0]
		self.velocity_Y = message['ball_v'][1]
	
	def message(self):
		content = {
			'TYPE': 'ball',
			'ball_p': [self.position_X, self.position_Y],
			'ball_v': [self.velocity_X, self.velocity_Y],
		}
		return content