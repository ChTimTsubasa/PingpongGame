from pingponggame.models import Pad, Ball
from django.core.cache import cache


BALL_SUF = '_BALL'
PAD_SUF = '_PAD'
GAME_SUF = '_GAME'
OPPO_SUF = '_OPPO'
CHANNEL_PRE = 'USER_'

class GameCache():

    @staticmethod
    def init_game(user1, user2, game_id):
        # GameCache.delete_game(user1, user2)
        cache.set(str(user1) + OPPO_SUF, user2)
        cache.set(str(user2) + OPPO_SUF, user1)
        cache.set(str(user1) + GAME_SUF, game_id)
        cache.set(str(user2) + GAME_SUF, game_id)

    @staticmethod
    def store_group(user_id):
        group = CHANNEL_PRE + str(user_id)
        cache.set(CHANNEL_PRE + str(user_id), group)
        return group
    
    @staticmethod
    def delete_user_record(user_id):
        cache.delete(str(user_id) + OPPO_SUF)
        cache.delete(str(user_id) + PAD_SUF)
        cache.delete(str(user_id) + BALL_SUF)
        cache.delete(str(user_id) + GAME_SUF)

    @staticmethod
    def delete_game(user1, user2):
        delete_user_record(str(user1))
        delete_user_record(str(user2))

    @staticmethod
    def get_game(user_id):
        return cache.get(str(user_id) + GAME_SUF)

    @staticmethod
    def update_pad(user_id, message):
        pad = cache.get(str(user_id) + PAD_SUF)
        if pad:
            # Update only when the new message has larger time stamp
            if pad.time_stamp < message['ts']:
                pad.update(message) 
                cache.set(str(user_id) + PAD_SUF, pad)
        else :
            pad = Pad(message)
            cache.set(str(user_id) + PAD_SUF, pad)

    @staticmethod
    def update_ball(game_id, message):
        ball = Ball(message)
        cache.set(str(game_id) + BALL_SUF, ball)
        return ball

    @staticmethod
    def get_oppo_pad(user_id):
        oppo_user_id = cache.get(str(user_id) + OPPO_SUF)
        return cache.get(str(oppo_user_id) + PAD_SUF)

    @staticmethod
    def get_oppo_group(user_id):
        oppo_user_id = cache.get(str(user_id) + OPPO_SUF)
        return cache.get(CHANNEL_PRE + str(oppo_user_id))

