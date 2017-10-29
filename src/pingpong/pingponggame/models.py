from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User


# Player model
class Player(models.Model):
	user = models.OneToOneField(User)
	current_game = models.IntegerField(default=0, blank = True)
	nickname = models.CharField(default = '', max_length=100, blank = True)
	# image = models.ImageField()
	bio = models.CharField(default = '', max_length=200, blank = True)
	


#Game model
class Game(models.Model):
	time = models.DateTimeField(auto_now=True, null=True)
	participants = models.ManyToManyField(Player, related_name = 'participants')
	winner = models.ForeignKey(Player, null=True, related_name = 'winner')
	
