from channels import Group

def ws_connect(message):
    print('connecting')
    Group('users').add(message.reply_channel)


def ws_disconnect(message):
    Group('users').discard(message.reply_channel)