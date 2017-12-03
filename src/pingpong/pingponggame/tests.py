from django.test import TestCase
from pingponggame.models import *

from django.contrib.auth.models import User

from pingponggame.caching import GameCache

from django.core.cache import cache
import datetime

# Create your tests here.

from django.db import transaction
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
        self.assertEqual(newplayer.ready, False)

    def test_ready(self):
        newuser = User.objects.create_user(
            username='temp',
            password='123',
            first_name='test',
            last_name='test',
        )
        newplayer = Player.objects.create(nickname='cool', user=newuser)
        newplayer.set_ready(True)
        self.assertTrue(newplayer.ready)
        newplayer.set_ready(False)
        self.assertFalse(newplayer.ready)

    def test_get_users(self):
        for i in range(1, 3):
            newuser = User.objects.create_user(
                username=i,
                password='123',
                first_name='test',
                last_name='test',
            )
            Player.objects.create(nickname=i, user=newuser)
        
        players = Player.objects.all()

class CurrentGameTestCase(TestCase):
    def setUp(self):
        # create 2 players
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
    
    def test_random_game(self):
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

    def test_id_game(self):
        new_c_game = CurrentGame.objects.create()
        ID = new_c_game.id
        g = CurrentGame.get_game_by_id(ID)
        self.assertEqual(g, new_c_game)
        i = 0
        for player in Player.objects.all():
            player.join_game(g)
            if i == 0:
                g = CurrentGame.get_game_by_id(ID)
                self.assertEqual(g, new_c_game)
            i = i + 1

        # Two players has join the game, should not find any more
        self.assertEqual(CurrentGame.get_game_by_id(ID), None)
        
        for player in Player.objects.all():
            player.leave_game(g)
            g = CurrentGame.get_game_by_id(ID)

    def test_full(self):
        new_c_game = CurrentGame.objects.create()
        self.assertFalse(new_c_game.full())

        for player in Player.objects.all():
            player.join_game(new_c_game)
        
        self.assertTrue(new_c_game.full())

        players = Player.objects.all()

        players[0].leave_game(new_c_game)
        self.assertFalse(new_c_game.full())

        self.assertEqual(new_c_game.player_set.count(), 1)

        # Updated player tuple would be the first one
        players[0].leave_game(new_c_game)
        self.assertFalse(new_c_game.full())

    @transaction.atomic
    def test_ready(self):
        new_c_game = CurrentGame.objects.create()
        self.assertFalse(new_c_game.all_ready())
        for player in Player.objects.all():
            player.join_game(new_c_game)
            player.set_ready(True)

        self.assertTrue(new_c_game.all_ready())

        for player in Player.objects.all():
            player.leave_game(new_c_game)

        self.assertFalse(new_c_game.all_ready())

        for player in Player.objects.all():
            player.join_game(new_c_game)
            self.assertFalse(player.ready)
            player.add_score()
            self.assertEqual(player.score, 1)

        new_c_game.player_set.update(score=0, ready=False)
        for player in Player.objects.all():
            self.assertFalse(player.ready)
            self.assertEqual(player.score, 0)

    @transaction.atomic
    def test_find_opponent(self):
        game = CurrentGame.objects.create()
        for player in Player.objects.all():
            player.join_game(game)
            player.set_ready(True)

        players = Player.objects.all()
        self.assertEqual(players[0], game.find_opponent(players[1]))
        self.assertEqual(players[1], game.find_opponent(players[0]))

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
    
class GameRecordTest(TestCase):
    def setUp(self):
        game = CurrentGame.objects.create()
        # create 2 players
        for i in range(1, 3):
            newuser = User.objects.create_user(
                username=i,
                password='123',
                first_name='test',
                last_name='test',
            )
            p = Player.objects.create(nickname=i, user=newuser)
            p.join_game(game)

        game.player_set.update(ready=True)

        game.player_set.first().add_score()

    def test_record(self):
        game = CurrentGame.objects.first()
        gr = GameRecord.record(game)

        self.assertEqual(gr.winner().score, 1)
        self.assertEqual(CurrentGame.objects.count(), 0)
