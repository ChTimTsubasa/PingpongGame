import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.generic.websockets import JsonWebsocketConsumer
from .models import Player, CurrentGame, GameRecord

from django.db import transaction

from django.core.cache import cache
from .caching import GameCache

import datetime

class GameServer(JsonWebsocketConsumer):
    http_user_and_session = True

    # Set to True if you want it, else leave it out
    strict_ordering = False

    # groups = None

    @transaction.atomic
    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        groups = []
        player = Player.objects.get(user=self.message.user)
        # When current player does exist and has a current game
        if player and player.currentGame:
            groups.append("p_%s" % player.user.id)
        if player.currentGame:
            game = player.currentGame
            groups.append("g_%s" % game.id)

        return groups

    @transaction.atomic
    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        player = Player.objects.get(user=message.user)
        # When current player does not exist or do not have a current game
        if not player or \
            not player.currentGame or \
            player.currentGame.state != CurrentGame.JOIN_STATE:
            message.reply_channel.send({"accept": False})
            return
        
        #available_players means how many players connect to the current game room
        game = player.currentGame
        message.reply_channel.send({"accept": True})
        if game.full():
            game.state = CurrentGame.READYING_STATE
            game.save()
            # 1 is ALL_IN
            ALL_IN_response = {'TYPE': 'EVENT', 'EVENT': 1}    
            # Tell all clients that they are all in
            self.group_send('g_%s' % game.id, ALL_IN_response)

    def receive(self, content, **kwargs):
        """
        Called when a message is received with decoded JSON content
        """
        if content['TYPE'] == 'STATE':
            self.state_handle(content)
        else:
            self.game_handle(content)
    
    @transaction.atomic
    def state_handle(self, content):
        player = Player.objects.get(user=self.message.user)
        game = player.currentGame
        if game.state == CurrentGame.READYING_STATE:
            if content['STATE'] == 'ready':
                player.set_ready(content['VAL'])
                if game.all_ready():
                    game.state = CurrentGame.GAMING_STATE
                    game.save()

                    GameCache.init_game(game)
                    response = {'TYPE': 'EVENT', 'EVENT': 3} # 3 is START

                    # Send the start command to all players and indicating
                    # their ball starting position
                    # Note that this is only for two players
                    dir = 1
                    user_list = GameCache.get_users(game)
                    for user in user_list:
                        response['DIR'] = dir
                        self.group_send("p_%s" % user.id, response)
                        dir = -dir

        elif game.state == CurrentGame.GAMING_STATE:
            if content['STATE'] == 'lose_score':
                opponent = game.find_opponent(player)
                opponent.add_score()
                game.player_set.update(ready=False)
                if opponent.score == game.max_score:
                    # One people win
                    response = {'TYPE': 'EVENT', 'EVENT': 5, 'WINNER': opponent.user.username}
                    self.group_send('g_%s' % game.id, response)
                    
                    # log the current game to game record
                    gr = GameRecord.record(game)
                    game.player_set.update(ready=False, score=0)
                    game.delete()

                else:
                    game.state = CurrentGame.READYING_STATE
                    game.save()
                    response = {'TYPE': 'EVENT', 'EVENT': 4, 'SCORER': opponent.user.username} # score message

                    # broadcast the score to all users
                    self.group_send('g_%s' % game.id, response)

                GameCache.delete_game(game)

    def game_handle(self, content):
        c_type = content['TYPE']
        response = {}

        # assert the game state in gaming
        if not cache.get(self.message.user):
            return

        opponents = GameCache.get_opponents(self.message.user)
        for opponent in opponents:
            self.group_send('p_%s' % opponent.id, content)

        
    @transaction.atomic
    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """

        player = Player.objects.get(user=message.user)
        
        # the game has ended gracefully
        if not player.currentGame:
            return

        game = player.currentGame
        
        player.leave_game(game)
        if game.player_set.count() == 0:
            game.delete()
            return

        ONE_OUT_response = {'TYPE': 'EVENT', 'EVENT': 2}
        self.group_send('g_%s' % game.id, ONE_OUT_response)
        
        game.state = CurrentGame.JOIN_STATE
        game.player_set.update(score=0, ready=False)
        game.save()