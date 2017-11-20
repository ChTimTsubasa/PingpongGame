import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.generic.websockets import JsonWebsocketConsumer
from .models import Player, Game

from django.db import transaction

from .caching import GameCache

import datetime

class GameServer(JsonWebsocketConsumer):
    http_user_and_session = True

    # Set to True if you want it, else leave it out
    strict_ordering = False

    @transaction.atomic
    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        print(self.message.user)
        player = Player.objects.get(user=self.message.user)
        # When current player does exist and has a current game
        if player and player.current_game:
            game = player.current_game
            group = GameCache.store_group(player.user.id)
            return ["game_%s" % game.id, group]

    @transaction.atomic
    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        print("connect")

        player = Player.objects.get(user=message.user)
        # When current player does not exist or do not have a current game
        if not player or not player.current_game:
            message.reply_channel.send({"accept": False})
            return
        
        #available_players means how many players connect to the current game room
        game = player.current_game
        game.player_ready()
        # Accept the connection; 
        message.reply_channel.send({"accept": True})
        
        if game.available_players == 2:
            game.available_players = 0
            game.state = Game.READY_STATE
            response = {'TYPE': 'STATE', 'STATE': 'ready'}
            # Initialize the game
            user1 = game.creator.user.id
            user2 = game.opponent.user.id
            GameCache.init_game(user1, user2, game.id)
            self.group_send('game_%s' % game.id, response)


    def receive(self, content, **kwargs):
        """
        Called when a message is received with decoded JSON content
        """
        if content['TYPE'] == 'STATE':
            self.state_handle(content)
        else:
            self.game_handle(content)
    
    def state_handle(self, content):
        player = Player.objects.get(user=self.message.user)
        game = player.current_game
        if content['STATE'] == 'start':
            game.player_ready()
            if game.available_players == 2:
                game.state = Game.GAMING_STATE
                game.save()
                response = {'TYPE': 'STATE', 'STATE': 'start'}
                user1 = game.creator.user.id
                user2 = game.creator.user.id
                # user 1 should be positive
                response[str(user1)] = 1
                # user 2 should be negative
                response[str(user2)] = -1
                self.group_send('game_%s' % game.id, response)
        
        # There may be race issue here
        elif content['STATE'] == 'score':
            game.add_oppo_player_score(player)
            if game.creator_score == 3 or game.opponent_score == 3:
                game.state = Game.END_STATE
                winner = game.determine_winner()
                response = {'TYPE': 'STATE', 'STATE': 'end', 'WINER': winer.user.id}
                self.group_send('game_%s' % game.id, response)
                GameCache.delete_game(
                                game.creator.user.id
                                game.opponent.user.id
                            )

            else:
                game.state = Game.PAUSE_STATE
                game.available_players = 0            
                game.save()
                response = {'TYPE': 'STATE', 'STATE': 'pause'}
                self.group_send('game_%s' % game.id, response)

    def game_handle(self, content):
        c_type = content['TYPE']
        response = {}

        if c_type == 'PAD':
            user_id = self.message.user.id
            GameCache.update_pad(user_id, content)
            oppo_pad = GameCache.get_oppo_pad(user_id)
            if oppo_pad:
                self.send(oppo_pad.message())

        elif c_type == 'BALL':
            user_id = self.message.user.id
            game_id = GameCache.get_game(user_id)
            oppo_group = GameCache.get_oppo_group(user_id)
            ball = GameCache.update_ball(game_id, content)
            self.group_send(oppo_group, ball.message())


    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        player = Player.objects.get(user=message.user)
        game = player.current_game
        # this game is over
        game.player_gone()
        player.leave_game()
        print (game.available_players)
        Group("game_%s" % game.id).discard(message.reply_channel)
        