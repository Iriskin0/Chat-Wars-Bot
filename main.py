# coding=utf-8
from pytg.sender import Sender
from pytg.receiver import Receiver
from pytg.utils import coroutine
from collections import deque
from time import time
import datetime
import re
import _thread
import random

orders = {
    'red': "🇮🇲",
    'black': "🇬🇵",
    'white': "🇨🇾",
    'yellow': "🇻🇦",
    'blue': '🇪🇺',
    'lesnoi_fort': "🌲Лесной форт",
    'les': "🌲",
    'gorni_fort': "⛰Горный форт",
    'gora': "⛰",
    'cover': "🛡 Защита",
    'attack': '⚔ Атака',
    'cover_symbol': "🛡",
    'hero': "🏅Герой"
}

arena_cover = ['🛡головы', '🛡корпуса', '🛡ног']
arena_attack = ['🗡в голову', '🗡по корпусу', '🗡по ногам']
# username игрового бота, менять не нужно
bot_username = "ChatWarsBot"
# username бота или человека, который будет отправлять приказы, ставить необязательно
order_username = "BlueOysterBot"
# ваш username, который может отправлять запросы этому скрипту, ставить необязательно
admin_username = "iriskin0"
# поменять blue на red, black, white, yellow в зависимости от вашего замка
castle = orders['blue']
# текущий приказ на атаку/защиту, по умолчанию всегда защита, трогать не нужно
current_order = {'time': 0, 'order': castle}

sender = Sender(host="localhost", port=1338)
action_list = deque([])
log_list = deque([], maxlen=30)
lt_arena = 0
get_info_diff = 360
hero_message_id = ''


@coroutine
def work_with_message(receiver):
    while True:
        msg = (yield)
        try:
            if msg['event'] == 'message' and msg['unread'] and 'text' in msg and msg['peer'] is not None:
                parse_text(msg['text'], msg['sender']['username'], msg['id'])

        except Exception as err:
            log("Ошибка coroutine: {0}".format(err))


def queue_worker(time_between_commands):
    global get_info_diff
    last_command_time = time()
    lt_info = 0
    while True:
        try:
            if time() - last_command_time > time_between_commands:
                last_command_time = time()
                if time() - lt_info > get_info_diff:
                    lt_info = time()
                    get_info_diff = random.randint(300, 550)
                    sender.send_msg('@' + bot_username, orders['hero'])
                    continue

                if len(action_list):
                    log("Отправляем " + action_list[0])
                    sender.send_msg('@' + bot_username, action_list.popleft())
        except Exception as err:
            log("Ошибка очереди: {0}".format(err))


def parse_text(text, username, message_id):
    global lt_arena
    if username == bot_username:
        log("Получили сообщение от бота. Проверяем условия")
        if text.find("Битва пяти замков через") != -1:
            global hero_message_id
            hero_message_id = message_id
            m = re.search('Битва пяти замков через(?: ([0-9]+)ч){0,1}(?: ([0-9]+)){0,1}', text)
            if not m.group(1):
                if m.group(2) and int(m.group(2)) < 25:
                    log("До битвы меньше 25 минут!")
                    # прекращаем все действия
                    state = re.search('Состояние:\\n(.*)$', text)
                    if time() - current_order['time'] > 3600:
                        update_order(castle)
                    if current_order['order'] not in action_list:
                        if current_order['order'] == castle and (state.group(1).find(orders['cover_symbol']) == -1 or state.group(1).find(castle) == -1):
                            log("Защита замка")
                            action_list.append(orders['cover'])
                            action_list.append(castle)
                        elif current_order['order'] == orders['lesnoi_fort'] and state.group(1).find(orders['les']) == -1:
                            log("Лесной форт")
                            action_list.append(current_order['order'])
                        elif current_order['order'] == orders['gorni_fort'] and state.group(1).find(orders['gora']) == -1:
                            log("Горный форт")
                            action_list.append(current_order['order'])
                        elif state.group(1).find(current_order['order']) == -1:
                            log("Приказ " + current_order['order'])
                            action_list.append(orders['attack'])
                            action_list.append(current_order['order'])
                    return
            log("Времени достаточно")
            # теперь узнаем, сколько у нас выносливости и золота
            m = re.search('Золото: ([0-9]+)\\n.*Выносливость: ([0-9]+) из', text)
            gold = int(m.group(1))
            endurance = int(m.group(2))
            log("Золото: {0}, выносливость: {1}".format(gold, endurance))
            if gold > 5 and "🔎Поиск соперника" not in action_list and time() - lt_arena > 3600:
                action_list.append("🔎Поиск соперника")
            if endurance > 0 and "🌲Лес" not in action_list:
                action_list.append("🌲Лес")

        elif text.find(" /go") != -1:
            sender.send_msg('@' + bot_username, '/go')

        elif text.find("выбери точку атаки и точку защиты") != -1:
            lt_arena = time()
            attack_chosen = arena_attack[random.randint(0, 2)]
            cover_chosen = arena_cover[random.randint(0, 2)]
            log("Атака: {0}, Защита: {1}".format(attack_chosen, cover_chosen))
            action_list.append(attack_chosen)
            action_list.append(cover_chosen)

    else:
        if username == order_username:
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

        if username == admin_username:
            if text == "#help":
                sender.send_msg('@' + admin_username, "#getlog\n#ping\n#lt_arena\n#order\n#time\n#get_info_diff\n#push_order\n#get_hero")
            if text == "#getlog":
                sender.send_msg('@' + admin_username, "\n".join(log_list))
                log_list.clear()
            if text == "#ping":
                sender.send_msg('@' + admin_username, "#pong")
            if text == "#lt_arena":
                sender.send_msg('@' + admin_username, str(lt_arena))
            if text == "#order":
                text_date = datetime.datetime.fromtimestamp(current_order['time']).strftime('%Y-%m-%d %H:%M:%S')
                sender.send_msg('@' + admin_username, current_order['order'] + " " + text_date)
            if text == "#time":
                text_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sender.send_msg('@' + admin_username, text_date)
            if text == "#get_info_diff":
                sender.send_msg('@' + admin_username, str(get_info_diff))
            if text == "#get_hero":
                if hero_message_id == '':
                    sender.send_msg('@' + admin_username, "Информации о герое пока не было")
                else:
                    sender.fwd('@' + admin_username, hero_message_id)
            if text.startswith("#push_order"):
                command = text.split(' ')[1]
                if command in orders:
                    update_order(orders[command])
                    sender.send_msg('@' + admin_username, "Команда " + command + " применена")
                else:
                    sender.send_msg('@' + admin_username, "Команда " + command + " не распознана")


def update_order(order):
    current_order['order'] = order
    current_order['time'] = time()
    action_list.append(orders['hero'])


def log(text):
    message = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ' ' + text
    print(message)
    log_list.append(message)


if __name__ == '__main__':
    receiver = Receiver(port=1338)
    receiver.start()  # start the Connector.
    _thread.start_new_thread(queue_worker, (3, ))
    receiver.message(work_with_message(receiver))
    receiver.stop()
