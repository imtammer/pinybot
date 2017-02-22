import sys
import logging
import time

import pinybot

log = logging.getLogger(__name__)


def main():
    if pinybot.pinylib.CONFIG.AUTO_INFO:
        if len(pinybot.pinylib.CONFIG.ROOM_NAME) is not 0:
            # Handle automatic login with the information already provided.
            bot = pinybot.TinychatBot(roomname=pinybot.pinylib.CONFIG.ROOM_NAME, nick=pinybot.pinylib.CONFIG.NICK_NAME,
                                      account=pinybot.pinylib.CONFIG.ACCOUNT, password=pinybot.pinylib.CONFIG.PASSWORD)
            is_logged_in = bot.login()
            if is_logged_in:
                bot.console_write(pinybot.pinylib.COLOR['bright_green'], 'Logged in as: %s' % bot.account)
        else:
            # Print out the error message and exit.
            print ('AUTOMATIC CONNECTION INFORMATION: The room name variable must be at least set for the automatic '
                   'login to work.')
            sys.exit(1)
    else:
        room_name = raw_input('Enter room name: ').strip()
        if pinybot.pinylib.CONFIG.ACCOUNT and pinybot.pinylib.CONFIG.PASSWORD:
            bot = pinybot.TinychatBot(roomname=room_name, account=pinybot.pinylib.CONFIG.ACCOUNT,
                                      password=pinybot.pinylib.CONFIG.PASSWORD)
        else:
            bot = pinybot.TinychatBot(roomname=room_name)
        bot.nickname = raw_input('Enter nickname (optional): ').strip()

        do_login = raw_input('Login? [enter=No] ')
        if do_login:
            if not bot.account:
                bot.account = raw_input('Account: ').strip()
            if not bot.password:
                bot.password = raw_input('Password: ')

            is_logged_in = bot.login()
            while not is_logged_in:
                bot.account = raw_input('Account: ').strip()
                bot.password = raw_input('Password: ')
                if bot.account == '/' or bot.password == '/':
                    main()
                    break
                elif bot.account == '//' or bot.password == '//':
                    do_login = False
                    break
                else:
                    is_logged_in = bot.login()
            if is_logged_in:
                bot.console_write(pinybot.pinylib.COLOR['bright_green'], 'Logged in as: %s' % bot.account)
        if not do_login:
            bot.account = ''
            bot.password = None

    status = bot.get_rtmp_parameters()
    while True:
        if status == 1:
            bot.console_write(pinybot.pinylib.COLOR['bright_red'], 'Password protected. Enter room password')
            bot.room_pass = raw_input()
            if bot.room_pass == '/':
                main()
                break
            else:
                status = bot.get_rtmp_parameters()
        elif status == 2:
            bot.console_write(pinybot.pinylib.COLOR['bright_red'], 'The room has been closed.')
            main()
            break
        elif status == 4:
            bot.console_write(pinybot.pinylib.COLOR['bright_red'], 'The response returned nothing.')
            main()
            break
        else:
            bot.console_write(pinybot.pinylib.COLOR['bright_green'], 'Connect parameters set. Connecting...')
            break

    t = pinybot.threading.Thread(target=bot.connect)
    t.daemon = True
    t.start()

    while not bot.is_connected:
        time.sleep(2)
    if not pinybot.pinylib.CONFIG.ON_SERVER:
        while bot.is_connected:
            chat_msg = raw_input()
            if chat_msg.startswith('/'):
                msg_parts = chat_msg.split(' ')
                cmd = msg_parts[0].lower().strip()
                if cmd == '/q':
                    bot.disconnect()
                    if bot.is_greenroom_connected:
                        bot.disconnect(greenroom=True)
                elif cmd == '/a':
                    if len(bot.users.signed_in) is 0:
                        print ('No signed in users in the room.')
                    else:
                        for user in bot.users.signed_in:
                            print ('%s:%s' % (user.nick, user.account))
                elif cmd == '/u':
                    for user in bot.users.all:
                        print ('%s: %s' % (user, bot.users.all[user].user_level))
                elif cmd == '/m':
                    if len(bot.users.mods) is 0:
                        print ('No moderators in the room.')
                    else:
                        for mod in bot.users.mods:
                            print (mod.nick)
                elif cmd == '/l':
                    if len(bot.users.lurkers) is 0:
                        print ('No lurkers in the room.')
                    else:
                        for lurker in bot.users.lurkers:
                            print (lurker.nick)
                elif cmd == '/n':
                    if len(bot.users.norms) is 0:
                        print ('No normal users in the room.')
                    else:
                        for norm in bot.users.norms:
                            print (norm.nick)
                elif cmd == '/b':
                    if len(msg_parts) is 2:
                        _user = bot.users.search(msg_parts[1])
                        if _user is not None:
                            if _user.user_level <= 1:
                                print ('Cannot ban room owner or client.')
                            else:
                                bot.send_ban_msg(_user.nick, _user.id)
                        else:
                            print ('No user named: %s' % msg_parts[1])
                elif cmd == '/k':
                    if len(msg_parts) is 2:
                        _user = bot.users.search(msg_parts[1])
                        if _user is not None:
                            if _user.user_level <= 1:
                                print ('Cannot kick room owner or client.')
                            else:
                                bot.send_ban_msg(_user.nick, _user.id)
                                bot.send_forgive_msg(_user.id)
                        else:
                            print ('No user named: %s' % msg_parts[1])

            else:
                bot.send_chat_msg(chat_msg)
    else:
        while bot.is_connected:
            continue

if __name__ == '__main__':
    if pinybot.pinylib.CONFIG.DEBUG_TO_FILE:
        formater = '%(asctime)s : %(levelname)s : %(filename)s : %(lineno)d : %(funcName)s() : %(name)s : %(message)s'
        logging.basicConfig(filename=pinybot.pinylib.CONFIG.B_DEBUG_FILE_NAME, level=pinybot.pinylib.CONFIG.DEBUG_LEVEL,
                            format=formater)
        log.info('Starting tinybot version: %s using pinylib version: %s' %
                 (pinybot.__version__, pinybot.pinylib.__version__))
    else:
        log.addHandler(logging.NullHandler())
    main()
