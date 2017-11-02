from django.db import models
from django.contrib.auth.models import User

# Player model
class Player(models.Model):
	user = models.OneToOneField(User, null=True)
	current_game = models.ForeignKey(Game, null=True)
	nickname = models.CharField(default = '', max_length=100, blank = True)
	# image = models.ImageField()
	bio = models.CharField(default = '', max_length=200, blank = True)

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
	winner = models.ForeignKey(Player, null=True, blank=True)
	creator = models.ForeignKey(Player)
	opponent = models.ForeignKey(Player, null=True, blank=True)

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
			return Game.objects.get(pk=id)
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


	class GameSquare(models.Model):
		STATUS_TYPES = (
			('Free', 'Free'),
			('Selected', 'Selected'),
			('Surrounding', 'Surrounding')
		)
		game = models.ForeignKey(Game)
		owner = models.ForeignKey(User, null=True, blank=True)
		status = models.CharField(choices=STATUS_TYPES,
									max_length=25,
									default='Free')
		row = models.IntegerField()
		col = models.IntegerField()

		# dates
		created = models.DateTimeField(auto_now_add=True)
		modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return '{0} - ({1}, {2})'.format(self.game, self.col, self.row)

	@staticmethod
	def get_by_id(id):
		try:
			return GameSquare.objects.get(pk=id)
		except GameSquare.DoesNotExist:
			# TODO: Handle exception for gamesquare
			return None

	def get_surrounding(self):
		"""
		Returns this square's surrounding neighbors that are still Free
		"""
		# TODO:
		# http://stackoverflow.com/questions/2373306/pythonic-and-efficient-way-of-finding-adjacent-cells-in-grid
		ajecency_matrix = [(i, j) for i in (-1, 0, 1)
							for j in (-1, 0, 1) if not (i == j == 0)]
		results = []
		for dx, dy in ajecency_matrix:
			# boundaries check
			if 0 <= (self.col + dy) < self.game.cols and 0 <= self.row + dx < self.game.rows:
				# yield grid[x_coord + dx, y_coord + dy]
				results.append((self.col + dy, self.row + dx))
		return results

