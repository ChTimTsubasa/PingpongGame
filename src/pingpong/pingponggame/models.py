from django.db import models
from django.contrib.auth.models import User

# Player model
class Player(models.Model):
	user = models.OneToOneField(User)
	current_game = models.ForeignKey('Game', null=True)
	nickname = models.CharField(default = '', max_length=100, blank = True)
	image = models.ImageField(blank = True)

	def create_new_game(self):
		new_game = Game.create_new(self)
		self.current_game = new_game
		self.save()
		return new_game

	def join_game_by_id(self, game_id):
		game = Game.get_by_id(game_id)
		return self.join_game(game)

	def join_game_random(self):
		game = Game.get_available_games()
		return self.join_game(game)

	def join_game(self, game):
		if not game:
			return None
		self.current_game = game
		self.save()
		return game

	def leave_game(self):
		if not self.current_game:
			return
		self.current_game.emit_player(self)
		

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

	def __unicode__(self):
		return 'Game #{0}'.format(self.pk)

	@staticmethod
	def get_available_games():
		return Game.objects.filter(opponent=None, completed=None)

	@staticmethod
	def get_by_id(id):
		try:
			return Game.get_available_games.get(pk=id)
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

	def emit_player(self, player):
		if self.opponent == player:
			self.opponent = null
			self.save()
		if self.creator == player:
			self.creator = self.opponent
			self.opponent = null
			self.save()

	def mark_complete(self, winner):
		"""
		Sets a game to completed status and records the winner
		"""
		self.winner = winner
		self.completed = datetime.now()
		self.save()
