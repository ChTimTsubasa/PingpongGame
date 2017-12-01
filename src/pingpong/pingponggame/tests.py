from django.test import TestCase
from pingponggame.models import Player, CurrentGame

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
        newplayer = Player.objects.create(nickname='cool', user=newuser)
        self.assertEqual(newplayer.score, 0)
        self.assertEqual(newplayer.currentGame, None)


class CurrentGameTestCase(TestCase):
    def setUp(self):
        # create 3 players
        for i in range(1, 3):
            newuser = User.objects.create_user(
                username=i,
                password='123',
                first_name='test',
                last_name='test',
            )
            Player.objects.create(nickname=i, user=newuser)

    def test_create(self):
        new_c_game = CurrentGame.objects.create()
        self.assertEqual(new_c_game.state, CurrentGame.JOIN_STATE)
        self.assertEqual(new_c_game.max_player_num ,2)
        self.assertEqual(new_c_game.max_score,3)
    
    def test_search_game(self):
        new_c_game = CurrentGame.objects.create()
        g = CurrentGame.get_game_random()
        self.assertEqual(g, new_c_game)

        # we have two players that donot join any game
        self.assertEqual(Player.objects.count(), 2)
        # TODO assert these two users has no game
        
        i = 0
        for player in Player.objects.all():
            player.join_game(g)
            if i == 0:
                g = CurrentGame.get_game_random()
                self.assertEqual(g, new_c_game)
            i = i + 1
        # Two players has join the game, should not find any more
        self.assertEqual(CurrentGame.get_game_random(), None)
        
        for player in Player.objects.all():
            player.leave_game(g)
            g = CurrentGame.get_game_random()
            self.assertEqual(g, new_c_game)

class GameParticipantTestCase(TestCase):

    def test_join_game(self):
        newuser = User.objects.create_user(
            username='temp',
            password='123',
            first_name='test',
            last_name='test',
        )
        player = Player.objects.create(nickname='cool', user=newuser)
        game = CurrentGame.objects.create()
        player.join_game(game)
        self.assertEqual(player.currentGame, game)
        self.assertEqual(game.player_set.count(), 1)
        with self.assertRaisesRegexp(
            AttributeError, "you are already in a game"
            ):
            self.assertRaises(AttributeError, player.join_game(game))
        self.assertEqual(game.player_set.count(), 1)

    # TODO test leave game
