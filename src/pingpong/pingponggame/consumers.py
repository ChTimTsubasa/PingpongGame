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
        
        message.reply_channel.send({"accept": True})
        #available_players means how many players connect to the current game room
        game = player.current_game
        game.player_ready()
        print(game.available_players)

        # Accept the connection; 
        self.message.reply_channel.send({"accept": True})

        if game.available_players == 2:
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
        self.game_handle(content)
        
    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        print("some one leaves")
        player = Player.objects.get(user=message.user)
        game = player.current_game
        # this game is over
        if game.winner:
            print("game is already over~")
            return
        game.player_gone()
        player.leave_game()
        print (game.available_players)
        Group("game_%s" % game.id).discard(message.reply_channel)
        Group("game_%s" % game.id).send({
                "text": json.dumps({
                    "TYPE": "STATE",
                    "STATE": "stop",
                }),
            })

        pass

    def game_handle(self, content):
        c_type = content['TYPE']
        response = {}

        if c_type == 'STATE':
            if content['STATE'] == 'start':
                response = {'TYPE': 'STATE', 'STATE': 'start'}
                self.send(response)

        elif c_type == 'PAD':
            user_id = self.message.user.id
            game_id = GameCache.get_game(user_id)
            GameCache.update_pad(user_id, content)
            oppo_pad = GameCache.get_oppo_pad(user_id)
            if oppo_pad:
                self.send(oppo_pad.message())

        elif c_type == 'BALL':
            user_id = self.message.user.id
            game_id = GameCache.get_game(user_id)

