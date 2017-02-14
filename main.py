# coding=utf-8
from pytg.sender import Sender
from pytg.receiver import Receiver
from pytg.utils import coroutine
from collections import deque
from time import time, sleep
from getopt import getopt
import sys
import datetime
import re
import _thread
import random

# username игрового бота
bot_username = 'ChatWarsBot'

# ваш username или username человека, который может отправлять запросы этому скрипту
admin_username = ''

# username бота и/или человека, которые будут отправлять приказы
order_usernames = ''

# имя замка
castle_name = 'blue'

# путь к сокет файлу
socket_path = ''

# хост чтоб слушать telegram-cli
host = 'localhost'

# порт по которому сшулать
port = 1338

opts, args = getopt(sys.argv[1:], 'a:o:c:s:h:p', ['admin=', 'order=', 'castle=', 'socket=', 'host=', 'port='])

for opt, arg in opts:
    if opt in ('-a', '--admin'):
        admin_username = arg
    elif opt in ('-o', '--order'):
        order_usernames = arg.split(',')
    elif opt in ('-c', '--castle'):
        castle_name = arg
    elif opt in ('-s', '--socket'):
        socket_path = arg
    elif opt in ('-h', '--host'):
        host = arg
    elif opt in ('-p', '--port'):
        port = int(arg)

orders = {
    'red': '🇮🇲',
    'black': '🇬🇵',
    'white': '🇨🇾',
    'yellow': '🇻🇦',
    'blue': '🇪🇺',
    'lesnoi_fort': '🌲Лесной форт',
    'les': '🌲',
    'gorni_fort': '⛰Горный форт',
    'gora': '⛰',
    'cover': '🛡 Защита',
    'attack': '⚔ Атака',
    'cover_symbol': '🛡',
    'hero': '🏅Герой',
    'corovan': '/go',
}

arena_cover = ['🛡головы', '🛡корпуса', '🛡ног']
arena_attack = ['🗡в голову', '🗡по корпусу', '🗡по ногам']
# поменять blue на red, black, white, yellow в зависимости от вашего замка
castle = orders[castle_name]
# текущий приказ на атаку/защиту, по умолчанию всегда защита, трогать не нужно
current_order = {'time': 0, 'order': castle}

sender = Sender(sock=socket_path) if socket_path else Sender(host=host,port=port)
action_list = deque([])
log_list = deque([], maxlen=30)
lt_arena = 0
get_info_diff = 360
hero_message_id = ''

bot_enabled = True
arena_enabled = True
les_enabled = True
corovan_enabled = True
order_enabled = True
auto_def_enabled = True


@coroutine
def work_with_message(receiver):
    while True:
        msg = (yield)
        try:
            if msg['event'] == 'message' and msg['unread'] and 'text' in msg and msg['peer'] is not None:
                parse_text(msg['text'], msg['sender']['username'], msg['id'])
        except Exception as err:
            log('Ошибка coroutine: {0}'.format(err))


def queue_worker():
    global get_info_diff
    lt_info = 0
    while True:
        try:
            #if time() - last_command_time > time_between_commands:
            #last_command_time = time()
            if time() - lt_info > get_info_diff:
                lt_info = time()
                get_info_diff = random.randint(600, 1200)
                send_msg(bot_username, orders['hero'])
                continue

            if len(action_list):
                log('Отправляем ' + action_list[0])
                send_msg(bot_username, action_list.popleft())
            sleep_time = random.randint(2, 8)
            sleep(sleep_time)
        except Exception as err:
            log('Ошибка очереди: {0}'.format(err))


def parse_text(text, username, message_id):
    global lt_arena
    global hero_message_id
    global bot_enabled
    global arena_enabled
    global les_enabled
    global corovan_enabled
    global order_enabled
    global auto_def_enabled
    if bot_enabled and username == bot_username:
        log('Получили сообщение от бота. Проверяем условия')

        if corovan_enabled and text.find(' /go') != -1:
            action_list.append(orders['corovan'])

        if orders['corovan'] in action_list and time() - current_order['time'] < 3600:
            update_order(current_order['order'])

        elif text.find('Битва пяти замков через') != -1:
            hero_message_id = message_id
            m = re.search('Битва пяти замков через(?: ([0-9]+)ч){0,1}(?: ([0-9]+)){0,1}', text)
            if not m.group(1):
                if m.group(2) and int(m.group(2)) <= 59:
                    # send_msg(admin_username, 'До битвы ' + m.group(2) + ' минут(ы)!')
                    # прекращаем все действия
                    state = re.search('Состояние:\\n(.*)$', text)
                    if auto_def_enabled and time() - current_order['time'] > 3600:
                        update_order(castle)
                    return
            log('Времени достаточно')
            # теперь узнаем, сколько у нас выносливости и золота
            # m = re.search('Золото: (-*[0-9]+)\\n.*Выносливость: ([0-9]+) из', text)
            gold = int(re.search('Золото: (-*[0-9]+)\\n', text).group(1))
            endurance = int(re.search('Выносливость: ([0-9]+)', text).group(1))
            log('Золото: {0}, выносливость: {1}'.format(gold, endurance))
            if les_enabled and endurance > 0 and '🌲Лес' not in action_list:
                action_list.append('🌲Лес')
            elif arena_enabled and gold >= 5 and '🔎Поиск соперника' not in action_list and time() - lt_arena > 3600:
                action_list.append('🔎Поиск соперника')

        elif arena_enabled and text.find('выбери точку атаки и точку защиты') != -1:
            lt_arena = time()
            attack_chosen = arena_attack[random.randint(0, 2)]
            cover_chosen = arena_cover[random.randint(0, 2)]
            log('Атака: {0}, Защита: {1}'.format(attack_chosen, cover_chosen))
            action_list.append(attack_chosen)
            action_list.append(cover_chosen)

    else:
        if bot_enabled and order_enabled and username in order_usernames:
            if text.find(orders['red']) != -1:
                update_order(orders['red'])
            elif text.find(orders['black']) != -1:
                update_order(orders['black'])
            elif text.find(orders['white']) != -1:
                update_order(orders['white'])
            elif text.find(orders['yellow']) != -1:
                update_order(orders['yellow'])
            elif text.find(orders['blue']) != -1:
                update_order(orders['blue'])
            elif text.find('🌲') != -1:
                update_order(orders['lesnoi_fort'])
            elif text.find('⛰') != -1:
                update_order(orders['gorni_fort'])
            elif text.find('🛡') != -1:
                update_order(castle)

            # send_msg(admin_username, 'Получили команду ' + current_order['order'] + ' от ' + username)

        if username == admin_username:
            if text == '#help':
                send_msg(admin_username, '\n'.join([
                    '#enable_bot - Включить бота',
                    '#disable_bot - Выключить бота',
                    '#enable_arena - Включить арену',
                    '#disable_arena - Выключить арену',
                    '#enable_les - Включить лес',
                    '#disable_les - Выключить лес',
                    '#enable_corovan - Включить корован',
                    '#disable_corovan - Выключить корован',
                    '#enable_order - Включить приказы',
                    '#disable_order - Выключить приказы',
                    '#enable_auto_def - Включить авто деф',
                    '#disable_auto_def - Выключить авто деф',
                    '#status - Получить статус',
                    '#hero - Получить информацию о герое',
                    '#push_order - Добавить приказ ({0})'.format(','.join(orders)),
                    '#order - Дебаг, последняя команда защиты/атаки замка',
                    '#log - Дебаг, последние 30 сообщений из лога',
                    '#time - Дебаг, текущее время',
                    '#lt_arena - Дебаг, последняя битва на арене',
                    '#get_info_diff - Дебаг, последняя разница между запросами информации о герое',
                    '#ping - Дебаг, проверить жив ли бот',
                ]))

            # Вкл/выкл бота
            if text == '#enable_bot':
                bot_enabled = True
                send_msg(admin_username, 'Бот успешно включен')
            if text == '#disable_bot':
                bot_enabled = False
                send_msg(admin_username, 'Бот успешно выключен')

            # Вкл/выкл арены
            if text == '#enable_arena':
                arena_enabled = True
                send_msg(admin_username, 'Арена успешно включена')
            if text == '#disable_arena':
                arena_enabled = False
                send_msg(admin_username, 'Арена успешно выключена')

            # Вкл/выкл леса
            if text == '#enable_les':
                les_enabled = True
                send_msg(admin_username, 'Лес успешно включен')
            if text == '#disable_les':
                les_enabled = False
                send_msg(admin_username, 'Лес успешно выключен')

            # Вкл/выкл корована
            if text == '#enable_corovan':
                corovan_enabled = True
                send_msg(admin_username, 'Корованы успешно включены')
            if text == '#disable_corovan':
                corovan_enabled = False
                send_msg(admin_username, 'Корованы успешно выключены')

            # Вкл/выкл команд
            if text == '#enable_order':
                order_enabled = True
                send_msg(admin_username, 'Приказы успешно включены')
            if text == '#disable_order':
                order_enabled = False
                send_msg(admin_username, 'Приказы успешно выключены')

            # Вкл/выкл авто деф
            if text == '#enable_auto_def':
                auto_def_enabled = True
                send_msg(admin_username, 'Авто деф успешно включен')
            if text == '#disable_auto_def':
                auto_def_enabled = False
                send_msg(admin_username, 'Авто деф успешно выключен')

            # Получить статус
            if text == '#status':
                send_msg(admin_username, '\n'.join([
                    'Бот включен: {0}',
                    'Арена включена: {1}',
                    'Лес включен: {2}',
                    'Корованы включены: {3}',
                    'Приказы включены: {4}',
                    'Авто деф включен: {5}',
                ]).format(bot_enabled, arena_enabled, les_enabled, corovan_enabled, order_enabled, auto_def_enabled))

            # Информация о герое
            if text == '#hero':
                fwd(admin_username, hero_message_id)

            # Получить лог
            if text == '#log':
                send_msg(admin_username, '\n'.join(log_list))
                log_list.clear()

            if text == '#lt_arena':
                send_msg(admin_username, str(lt_arena))

            if text == '#order':
                text_date = datetime.datetime.fromtimestamp(current_order['time']).strftime('%Y-%m-%d %H:%M:%S')
                send_msg(admin_username, current_order['order'] + ' ' + text_date)

            if text == '#time':
                text_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                send_msg(admin_username, text_date)

            if text == '#ping':
                send_msg(admin_username, '#pong')

            if text == '#get_info_diff':
                send_msg(admin_username, str(get_info_diff))

            if text.startswith('#push_order'):
                command = text.split(' ')[1]
                if command in orders:
                    update_order(orders[command])
                    send_msg(admin_username, 'Команда ' + command + ' применена')
                else:
                    send_msg(admin_username, 'Команда ' + command + ' не распознана')


def send_msg(to, message):
    sender.send_msg('@' + to, message)


def fwd(to, message_id):
    sender.fwd('@' + to, message_id)


def update_order(order):
    current_order['order'] = order
    current_order['time'] = time()
    if order == castle:
        action_list.append(orders['cover'])
    else:
        action_list.append(orders['attack'])
    action_list.append(order)


def log(text):
    message = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ' ' + text
    print(message)
    log_list.append(message)


if __name__ == '__main__':
    receiver = Receiver(sock=socket_path) if socket_path else Receiver(port=port)
    receiver.start()  # start the Connector.
    _thread.start_new_thread(queue_worker, ())
    receiver.message(work_with_message(receiver))
    receiver.stop()
