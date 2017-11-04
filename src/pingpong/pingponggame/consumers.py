import json
import redis
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

redis_conn = redis.Redis("localhost", 6379)

@channel_session_user_from_http
# Connected to websocket.connect
def ws_add(message):
    # Accept the connection
    message.reply_channel.send({"accept": True})
    # Add to the chat group
    Group("chat").add(message.reply_channel)

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