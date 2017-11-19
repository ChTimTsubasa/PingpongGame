import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.generic.websockets import JsonWebsocketConsumer
from .models import Player, Game

from django.db import transaction

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
        # When current player does not exist or do not have a current game
        if player and player.current_game:
            game = player.current_game
            return ["game_%s" % game.id]

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
        print(message.reply_channel)
        #available_players means how many players connect to the current game room
        game = player.current_game
        game.player_ready()
        print(game.available_players)
        
        if game.available_players == 2:
            response = {'TYPE': 'STATE', 'state': 'start'}
            self.group_send('game_%s' % game.id, response)


        # Accept the connection; this is done by default if you don't override
        # the connect function.
        self.message.reply_channel.send({"accept": True})

    def receive(self, content, **kwargs):
        """
        Called when a message is received with decoded JSON content
        """
        # Simple echo
        print(self.message.user)
        print(content)
        response = self.game_handle(content)
        print(response)
        self.send(response)

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

            response = {'TYPE': 'STATE', 'STATE': 'stop'}
        elif c_type == 'GAME':
            response = {'': 'game'}
        
        return response
