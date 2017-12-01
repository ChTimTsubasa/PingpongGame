from django.test import TestCase
from pingponggame.models import Player

from django.contrib.auth.models import User

from pingponggame.caching import GameCache

from django.core.cache import cache
import datetime

# Create your tests here.

class PlayerTestCase(TestCase):
    def test_create(self):
        newuser = User.objects.create_user(
            username='temp',
            password='123',
            first_name='test',
            last_name='test',
        )
        newplayer = Player(user=newuser)
        newplayer.nickname='cool'
        newplayer.save()
        self.assertEqual(newplayer.score, 0)
        self.assertEqual(newplayer.currentGame, None)

    
        
