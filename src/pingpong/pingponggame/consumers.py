import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from django.core.cache import cache
from .models import Player, Game

@channel_session_user_from_http
# Connected to websocket.connect
def ws_add(message):
    player = Player.objects.get(user=message.user)

    # When current player does not exist or do not have a current game
    if not player or not player.current_game:
        message.reply_channel.send({"accept": False})
        return
    
    message.reply_channel.send({"accept": True})
    
    game = player.current_game
    
    Group("game_%s" % game.id).add(message.reply_channel)

    if not cache.get(game.id):
        cache.set(game.id, game)
    else:
        game = cache.get(game.id)
    
    print(cache.get(game.id))
    # Two people are available
    message = {'room':str(game.id)}
    print (message)

@channel_session_user
# Connected to websocket.receive
def ws_message(message):
    Group("chat").send({
        "text": "[user] %s" % message.content['text'],
    })

@channel_session_user
# Connected to websocket.disconnect
def ws_disconnect(message):
    print("some one leaves")
    Group("chat").discard(message.reply_channel)

