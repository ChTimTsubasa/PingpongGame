from django.test import TestCase
from pingponggame.models import Pad

from pingponggame.caching import GameCache

from django.core.cache import cache

# Create your tests here.

class PadTestCase(TestCase):
    message = {}
    def setUp(self):
        self.message['TYPE'] = "GAME"
        self.message['pad_v'] = [0.1, 0.2]
        self.message['pad_p'] = [0.2, 0.3]

    def test_pad_contruct(self):
        pad = Pad(self.message)

        self.assertEqual(pad.position_X, self.message['pad_p'][0])
        self.assertEqual(pad.position_Y, self.message['pad_p'][1])
        self.assertEqual(pad.velocity_X, self.message['pad_v'][0])
        self.assertEqual(pad.velocity_Y, self.message['pad_v'][1])

    def test_pad_toMessage(self):
        pad = Pad(self.message)
        new_m = pad.message()
        self.assertEqual(self.message['pad_v'], new_m['pad_v'])
        self.assertEqual(self.message['pad_p'], new_m['pad_p'])


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
