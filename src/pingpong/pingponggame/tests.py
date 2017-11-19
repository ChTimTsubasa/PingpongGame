from django.test import TestCase
from pingponggame.models import Pad

from pingponggame.caching import GameCache

from django.core.cache import cache
import datetime

# Create your tests here.

class PadTestCase(TestCase):
    message = {}
    def setUp(self):
        self.message['TYPE'] = "PAD"
        self.message['x'] = 0.1
        self.message['y'] = 0.2
        
    def test_pad_contruct(self):
        t1 = datetime.datetime.now()
        pad = Pad(self.message)
        t2 = datetime.datetime.now()

        self.assertEqual(pad.position_X, self.message['x'])
        self.assertEqual(pad.position_Y, self.message['y'])

    def test_pad_toMessage(self):
        pad = Pad(self.message)
        new_m = pad.message()
        self.assertEqual(self.message['x'], new_m['x'])
        self.assertEqual(self.message['y'], new_m['y'])


class CacheTest(TestCase):
    user1 = 1
    user2 = 2
    game = 3

    def test_store_group(self):
        GameCache.store_group(self.user1)
        group = cache.get("USER_" + str(self.user1))
        self.assertEqual("USER_" + str(self.user1), group)

    def test_init_game(self):
        GameCache.store_group(self.user1)
        GameCache.store_group(self.user2)
        GameCache.init_game(self.user1, self.user2, self.game)
