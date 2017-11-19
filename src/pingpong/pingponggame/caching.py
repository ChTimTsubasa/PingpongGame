from pingponggame.models import Pad, Ball
from django.core.cache import cache


BALL_SUF = '_BALL'
PAD_SUF = '_PAD'
OPPO_SUF = '_OPPO'

def init_game(user1, user2):
    cache.set(user1 + OPPO_SUF, user2)
    cache.set(user2 + OPPO_SUF, user1)

def delete_user_record(user_id):
    cache.delete(user_id + OPPO_SUF)
    cache.delete(user_id + PAD_SUF)
    cache.delete(user_id + BALL_SUF)

def delete_game(user1, user2):
    delete_user_record(user1)
    delete_user_record(user2)

def update_pad(user_id, message):
    # TODO do some authentication
    pad = Pad(message)
    cache.set(user_id + PAD_SUF, pad)
    return pad

def update_ball(user_id, message):
    ball = Ball(message)
    cache.set(user_id + BALL_SUF, ball)
    return ball