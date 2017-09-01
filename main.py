#!/usr/bin/python3
# coding=utf-8

from pytg.sender import Sender
from pytg.receiver import Receiver
from pytg.utils import coroutine
from collections import deque
from time import time, sleep
from getopt import getopt
from datetime import datetime
from threading import Timer
import sys
import os
import glob
import re
import _thread
import random
import pytz
import configparser

pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname)

# username игрового бота
bot_username = 'ChatWarsBot'

# ваш username или username человека, который может отправлять запросы этому скрипту
admin_username = ''

# username бота и/или человека, которые будут отправлять приказы
order_usernames = ''

# имя замка
castle_name = None

captcha_bot = 'ChatWarsCaptchaBot'

stock_bot = 'PenguindrumStockBot'
stock2_bot = 'ChatWarsStock_bot'

trade_bot = 'ChatWarsTradeBot'

redstat_bot = 'RedStatBot'
redstat2_bot = 'CWRedCastleBot'

blueoysterbot = 'BlueOysterBot'

# путь к сокет файлу
socket_path = ''

# хост чтоб слушать telegram-cli
host = 'localhost'

# порт по которому слушать
port = 1338

# скидывание денег покупкой/продажей шлемов
donate_buying = False

# включить прокачку при левелапе
lvl_up = 'lvl_off'

# имя группы
group_name = ''

build_target = '/build_hq'

# id ресурса для трейда
resource_id_list = []

config = configparser.ConfigParser()

# user_id бота, используется для поиска конфига
bot_user_id = ''

gold_to_left = 0

#Путь, по которому создаются файлы боёв
fight_path = ''

# apikey для IFTTT
apikey = None

opts, args = getopt(sys.argv[1:], 'a:o:s:h:p:g:b:l:n:k:f:', ['admin=', 'order=', 'socket=', 'host=', 'port=',
                                                          'gold=', 'buy=', 'lvlup=', 'group_name=', 'apikey=', 'fpath='])

for opt, arg in opts:
    if opt in ('-a', '--admin'):
        admin_username = arg
    elif opt in ('-o', '--order'):
        order_usernames = arg.split(',')
    elif opt in ('-s', '--socket'):
        socket_path = arg
    elif opt in ('-h', '--host'):
        host = arg
    elif opt in ('-p', '--port'):
        port = int(arg)
    elif opt in ('-g', '--gold'):
        gold_to_left = int(arg)
    elif opt in ('-b', '--buy'):
        donate_buying = bool(arg)
    elif opt in ('-l', '--lvlup'):
        lvl_up = arg
    elif opt in ('-n', '--group_name'):
        group_name = arg
    elif opt in ('-k', '--apikey'):
        apikey = str(arg)
    elif opt in ('-f', '--fpath'):
        fight_path = str(arg)

if apikey is not None:
    import requests
        
orders = {
    'red': '🇮🇲',
    'black': '🇬🇵',
    'white': '🇨🇾',
    'yellow': '🇻🇦',
    'blue': '🇪🇺',
    'mint': '🇲🇴',
    'twilight': '🇰🇮',
    'lesnoi_fort': '🌲Лесной форт',
    'les': '🌲Лес',
    'gorni_fort': '⛰Горный форт',
    'morskoi_fort': '⚓Морской форт',
    'gora': '⛰',
    'cover': '🛡 Защита',
    'attack': '⚔ Атака',
    'cover_symbol': '🛡',
    'hero': '🏅Герой',
    'corovan': '/go',
    'peshera': '🕸Пещера',
    'quests': '🗺 Квесты',
    'castle_menu': '🏰Замок',
    'lavka': '🏚Лавка',
    'snaraga': 'Снаряжение',
    'shlem': 'Шлем',
    'sell': 'Скупка предметов',
    'lvl_def': '+1 🛡Защита',
    'lvl_atk': '+1 ⚔Атака',
    'lvl_off': 'Выключен',
    'more':'🏝Побережье',
    'pet_play': '⚽Поиграть',
    'pet_feed': '🍼Покормить',
    'pet_wash': '🛁Почистить'
}

captcha_answers = {
    # блядь, кольцов, ну и хуйню же ты придумал
    'watermelon_n_cherry': '🍉🍒',
    'bread_n_cheese': '🍞🧀',
    'cheese': '🧀',
    'pizza': '🍕',
    'hotdog': '🌭',
    'eggplant_n_carrot': '🍆🥕',
    'dog': '🐕',
    'horse': '🐎',
    'goat': '🐐',
    'cat': '🐈',
    'pig': '🐖',
    'squirrel': '🐿'
}

builds = {
    'stash': '/build_stash',
    'sentries': '/build_sentries',
    'monument': '/build_monument',
    'warriors': '/build_warriors',
    'teaparty': '/build_teaparty',
    'hq': '/build_hq',
    'gladiators': '/build_gladiators',
    'wall': '/build_wall',
    'ambar': '/build_ambar',
    'repair_stash': '/repair_stash',
    'repair_sentries': '/repair_sentries',
    'repair_monument': '/repair_monument',
    'repair_warriors': '/repair_warriors',
    'repair_teaparty': '/repair_teaparty',
    'repair_hq': '/repair_hq',
    'repair_gladiators': '/repair_gladiators',
    'repair_wall': '/repair_wall',
    'repair_ambar': '/repair_ambar'
}

flags = {
    '🇪🇺': 'blue',
    '🇮🇲': 'red',
    '🇬🇵': 'black',
    '🇻🇦': 'yellow',
    '🇨🇾': 'white',
    '🇰🇮': 'twilight',
    '🇲🇴': 'mint',
}

pet_states = {
    '😁': 'perfect',
    '😃': 'good',
    '😐': 'med',
    '😢': 'bad'
}

pet_char_states = {
    'отлично!': 5,
    'хорошо': 4,
    'удовлетворительно': 3,
    'плохо': 2,
    'очень плохо': 1
}

# Блядь, ну нахуя так репорты собирать то, а?
oyster_report_castles = {
    'red': '🇮🇲Красный замок',
    'black': '🇬🇵Черный замок',
    'white': '🇨🇾Белый замок',
    'yellow': '🇻🇦Желтый замок',
    'blue': '🇪🇺Синий замок',
    'mint': '🇲🇴Мятный замок',
    'twilight': '🇰🇮Сумрачный замок',
}

arena_cover = ['🛡головы', '🛡корпуса', '🛡ног']
arena_attack = ['🗡в голову', '🗡по корпусу', '🗡по ногам']
# ничо не менять, все подхватится само
castle = orders['blue']
# текущий приказ на атаку/защиту, по умолчанию всегда защита, трогать не нужно
current_order = {'time': 0, 'order': castle}
# задаем получателя ответов бота: админ или группа
if group_name =='':
    pref = '@'
    msg_receiver = admin_username
else:
    pref = ''
    msg_receiver = group_name

sender = Sender(sock=socket_path) if socket_path else Sender(host=host,port=port)
action_list = deque([])
log_list = deque([], maxlen=30)
lt_arena = 0
get_info_diff = 360
hero_message_id = 0
report_message_id = 0
last_captcha_id = 0
last_pet_play = 0

bot_enabled = True
arena_enabled = True
les_enabled = True
peshera_enabled = False
more_enabled = False
corovan_enabled = True
order_enabled = True
auto_def_enabled = True
donate_enabled = False
quest_fight_enabled = True
build_enabled = False
firststock_enabled = True
secondstock_enabled = False
twinkstock_enabled = False
trade_active = False
report = False
arenafight = re.search('Поединков сегодня (\d+) из (\d+)', 'Поединков сегодня 0 из 0')
victory = 0
gold = 0
endurance = 0
level = 0
class_available = False

arena_change_enabled = False
arena_item_id = 0
non_arena_item_id = 0

arena_running = False
arena_delay = False
arena_delay_day = -1
tz = pytz.timezone('Europe/Moscow')

@coroutine
def work_with_message(receiver):
    global bot_user_id
    while True:
        msg = (yield)
        try:
            if msg['event'] == 'message' and 'text' in msg and msg['peer'] is not None:
                if bot_user_id == '' and msg['sender']['username'] == bot_username:
                    bot_user_id = msg['receiver']['peer_id']
                    log('user_id найден: {0}'.format(bot_user_id))
                    config.read(fullpath + '/bot_cfg/' + str(bot_user_id) + '.cfg')
                    if config.has_section(str(bot_user_id)):
                        log('Конфиг найден')
                        read_config()
                        log('Конфиг загружен')
                    else:
                        log('Конфиг не найден')
                        write_config()
                        log('Новый конфиг создан')
                # Проверяем наличие юзернейма, чтобы не вываливался Exception
                if 'username' in msg['sender']:
                    parse_text(msg['text'], msg['sender']['username'], msg['id'])
        except Exception as err:
            if apikey is not None:
                ifttt("bot_error", "coroutine", err)
            log('Ошибка coroutine: {0}'.format(err))

            
def queue_worker():
    global get_info_diff
    global lt_info
    global arena_delay
    global arena_delay_day
    global tz
    lt_info = 0
    # Бот не пишет незнакомым юзерам, пока не поищет их
    print(sender.contacts_search(bot_username))
    print(sender.contacts_search(captcha_bot))
    print(sender.contacts_search(stock_bot))
    print(sender.contacts_search(stock2_bot))
    print(sender.contacts_search(trade_bot))
    print(sender.contacts_search(redstat_bot))
    print(sender.contacts_search(redstat2_bot))
    print(sender.contacts_search(blueoysterbot))
    sleep(3)
    while True:
        try:
            if time() - lt_info > get_info_diff:
                if arena_delay and arena_delay_day != datetime.now(tz).day:
                    arena_delay = False
                lt_info = time()
                curhour = datetime.now(tz).hour
                if 9 <= curhour <= 23:
                    get_info_diff = random.randint(420, 900)
                else:
                    get_info_diff = random.randint(600, 900)
                if bot_enabled:
                    send_msg('@', bot_username, orders['hero'])
                continue
            if fight_path != '' and castle_name is not None:
                os.chdir(fight_path)
                for file_name in glob.glob(castle_name+"*"):
                    if file_name[-4:] != port:
                        f = open(file_name,'r')
                        action_list.append(f.readline())
                        f.close
                        os.remove(file_name)
            if len(action_list):
                log('Отправляем ' + action_list[0])
                send_msg('@', bot_username, action_list.popleft())
            sleep_time = random.randint(2, 5)
            sleep(sleep_time)
        except Exception as err:
            if apikey is not None:
                ifttt("bot_error", "очереди", err)
            log('Ошибка очереди: {0}'.format(err))

def read_config():
    global config
    global bot_user_id
    global bot_enabled
    global arena_enabled
    global les_enabled
    global peshera_enabled
    global more_enabled
    global corovan_enabled
    global auto_def_enabled
    global donate_enabled
    global donate_buying
    global lvl_up
    global quest_fight_enabled
    global build_enabled
    global build_target
    global arena_change_enabled
    global arena_item_id
    global non_arena_item_id
    global firststock_enabled
    global secondstock_enabled
    section=str(bot_user_id)
    bot_enabled          = config.getboolean(section, 'bot_enabled')          if config.has_option(section, 'bot_enabled')          else bot_enabled
    arena_enabled        = config.getboolean(section, 'arena_enabled')        if config.has_option(section, 'arena_enabled')        else arena_enabled
    les_enabled          = config.getboolean(section, 'les_enabled')          if config.has_option(section, 'les_enabled')          else les_enabled
    peshera_enabled      = config.getboolean(section, 'peshera_enabled')      if config.has_option(section, 'peshera_enabled')      else peshera_enabled
    more_enabled         = config.getboolean(section, 'more_enabled')         if config.has_option(section, 'more_enabled')         else more_enabled
    corovan_enabled      = config.getboolean(section, 'corovan_enabled')      if config.has_option(section, 'corovan_enabled')      else corovan_enabled
    auto_def_enabled     = config.getboolean(section, 'auto_def_enabled')     if config.has_option(section, 'auto_def_enabled')     else auto_def_enabled
    donate_enabled       = config.getboolean(section, 'donate_enabled')       if config.has_option(section, 'donate_enabled')       else donate_enabled
    donate_buying        = config.getboolean(section, 'donate_buying')        if config.has_option(section, 'donate_buying')        else donate_buying
    lvl_up               = config.get       (section, 'lvl_up')               if config.has_option(section, 'lvl_up')               else lvl_up
    quest_fight_enabled  = config.getboolean(section, 'quest_fight_enabled')  if config.has_option(section, 'quest_fight_enabled')  else quest_fight_enabled
    build_enabled        = config.getboolean(section, 'build_enabled')        if config.has_option(section, 'build_enabled')        else build_enabled
    build_target         = config.get       (section, 'build_target')         if config.has_option(section, 'build_target')         else build_target
    arena_change_enabled = config.getboolean(section, 'arena_change_enabled') if config.has_option(section, 'arena_change_enabled') else arena_change_enabled
    arena_item_id        = config.get       (section, 'arena_item_id')        if config.has_option(section, 'arena_item_id')        else arena_item_id
    non_arena_item_id    = config.get       (section, 'non_arena_item_id')    if config.has_option(section, 'non_arena_item_id')    else non_arena_item_id
    firststock_enabled   = config.getboolean(section, 'firststock_enabled')   if config.has_option(section, 'firststock_enabled')   else firststock_enabled
    secondstock_enabled  = config.getboolean(section, 'secondstock_enabled')  if config.has_option(section, 'secondstock_enabled')  else secondstock_enabled

def write_config():
    global config
    global bot_user_id
    global bot_enabled
    global arena_enabled
    global les_enabled
    global peshera_enabled
    global more_enabled
    global corovan_enabled
    global auto_def_enabled
    global donate_enabled
    global donate_buying
    global lvl_up
    global quest_fight_enabled
    global build_enabled
    global build_target
    global arena_change_enabled
    global firststock_enabled
    global secondstock_enabled
    section=str(bot_user_id)
    if config.has_section(section):
        config.remove_section(section)
    config.add_section(section)
    config.set(section, 'bot_enabled', str(bot_enabled))
    config.set(section, 'arena_enabled', str(arena_enabled))
    config.set(section, 'arena_change_enabled', str(arena_change_enabled))
    config.set(section, 'arena_item_id', str(arena_item_id))
    config.set(section, 'non_arena_item_id', str(non_arena_item_id))
    config.set(section, 'les_enabled', str(les_enabled))
    config.set(section, 'peshera_enabled', str(peshera_enabled))
    config.set(section, 'more_enabled', str(more_enabled))
    config.set(section, 'corovan_enabled', str(corovan_enabled))
    config.set(section, 'auto_def_enabled', str(auto_def_enabled))
    config.set(section, 'donate_enabled', str(donate_enabled))
    config.set(section, 'donate_buying', str(donate_buying))
    config.set(section, 'lvl_up', str(lvl_up))
    config.set(section, 'quest_fight_enabled', str(quest_fight_enabled))
    config.set(section, 'build_enabled', str(build_enabled))
    config.set(section, 'build_target', str(build_target))
    config.set(section, 'firststock_enabled', str(firststock_enabled))
    config.set(section, 'secondstock_enabled', str(secondstock_enabled))
    with open(fullpath + '/bot_cfg/' + str(bot_user_id) + '.cfg','w+') as configfile:
        config.write(configfile)

def parse_text(text, username, message_id):
    global lt_arena
    global hero_message_id
    global bot_enabled
    global arena_enabled
    global les_enabled
    global peshera_enabled
    global more_enabled
    global corovan_enabled
    global order_enabled
    global auto_def_enabled
    global donate_enabled
    global donate_buying
    global last_captcha_id
    global arena_delay
    global arena_delay_day
    global tz
    global arena_running
    global lvl_up
    global pref
    global msg_receiver
    global quest_fight_enabled
    global build_enabled
    global build_target
    global twinkstock_enabled
    global resource_id_list
    global report
    global gold
    global inv
    global endurance
    global endurancetop
    global state
    global victory
    global arenafight
    global get_info_diff
    global lt_info
    global time_to_war
    global castle_name
    global castle
    global level
    global class_available
    global last_pet_play
    global arena_change_enabled
    global arena_item_id
    global non_arena_item_id
    global trade_active
    global report_message_id
    global oyster_report_castles
    global firststock_enabled
    global secondstock_enabled

    if bot_enabled and username == bot_username:
        log('Получили сообщение от бота. Проверяем условия')

        if text.find('🌟Поздравляем! Новый уровень!') != -1 and lvl_up != 'lvl_off':
            log('получили уровень - {0}'.format(orders[lvl_up]))
            action_list.append('/level_up')
            action_list.append(orders[lvl_up])

        elif "На выходе из замка охрана никого не пропускает" in text:
            # send_msg('@', admin_username, "Командир, у нас проблемы с капчой! #captcha " + '|'.join(captcha_answers.keys()))
            # fwd('@', admin_username, message_id)
            action_list.clear()
            bot_enabled = False
            last_captcha_id = message_id
            fwd('@', captcha_bot, message_id)

        elif 'Не умничай!' in text or 'Ты долго думал, аж вспотел от напряжения' in text:
            send_msg('@', admin_username, "Командир, у нас проблемы с капчой! #captcha " + '|'.join(captcha_answers.keys()))
            bot_enabled = False
            if last_captcha_id != 0:
                fwd('@', admin_username, message_id)
            else:
                send_msg('@', admin_username, 'Капча не найдена?')

        elif 'На сегодня ты уже своё отвоевал. Приходи завтра.' in text:
            arena_delay = True
            arena_delay_day = datetime.now(tz).day
            log("Отдыхаем денек от арены")
            arena_running = False

        elif 'Ты вернулся со стройки:' in text:
            if castle_name == 'red':
                log("Построили, сообщаем легату")
                fwd('@', redstat_bot, message_id)
                fwd('@', redstat2_bot, message_id)
            if castle_name == 'blue':
                log("Построили, сообщаем ойстеру")
                fwd('@', 'BlueOysterBot', message_id)

        elif 'Здание отремонтировано:' in text:
            if castle_name == 'red':
                log("Отремонтировали, сообщаем легату")
                fwd('@', redstat_bot, message_id)
                fwd('@', redstat2_bot, message_id)
            if castle_name == 'blue':
                log("Отремонтировали, сообщаем ойстеру")
                fwd('@', 'BlueOysterBot', message_id)

        elif 'Твои результаты в бою:' in text:
            if castle_name == 'red':
                log("Повоевали, сообщаем легату")
                fwd('@', redstat_bot, message_id)
                fwd('@', redstat2_bot, message_id)

            if castle_name == 'blue':
                log("Повоевали, сообщаем ойстеру")
                fwd('@', 'BlueOysterBot', message_id)

                def send_order_type():
                    if current_order['order'] == castle:
                        send_msg('@', 'BlueOysterBot', orders['cover'])
                    else:
                        send_msg('@', 'BlueOysterBot', orders['attack'])

                def send_order():
                    send_msg('@', 'BlueOysterBot', oyster_report_castles[flags[current_order['order']]])

                t = Timer(4, send_order_type())
                t2 = Timer(8, send_order())
                t.start()
                t2.start()

            report_message_id = message_id

        elif 'Закупка начинается. Отслеживание заказа:' in text:
            buytrade = re.search('обойдется примерно в ([0-9]+)💰', text).group(1)
            gold -= int(buytrade)
            log('Купили что-то на бирже на {0} золота'.format(buytrade))

        elif 'Ты пошел строить:' in text:
            log("Ушли строить")
            lt_info = time()
            get_info_diff = random.randint(400, 500)

        elif 'Ты отправился искать приключения в пещеру' in text:
            log("Ушли в пещеру")
            lt_info = time()
            get_info_diff = random.randint(400, 500)
            endurance -= 2

        elif 'Ты отправился искать приключения в лес' in text:
            log("Ушли в лес")
            lt_info = time()
            get_info_diff = random.randint(400, 500)
            endurance -= 1

        elif 'Ищем соперника. Пока соперник не найден' in text:
            lt_info = time()
            get_info_diff = random.randint(900, 1200)
            gold -= 5

        elif 'Добро пожаловать на арену!' in text:
            victory = re.search('Количество побед: (\d+)', text).group(1)
            arenafight = re.search('Поединков сегодня (\d+) из (\d+)', text)
            log('Поединков: {0} / {1}. Побед: {2}'.format(arenafight.group(1), arenafight.group(2), victory))
            if 'Даже драконы не могут драться так часто' in text:
                arena_delay = True
                arena_delay_day = datetime.now(tz).day
                log("Отдыхаем денек от арены")
                arena_running = False
                sleep(random.randint(5, 15))
                action_list.append('⬅️Назад')
            if arena_enabled and not arena_delay and gold >= 5 and not arena_running:
                log('Включаем флаг - арена запущена')
                if arena_change_enabled:
                    action_list.append('/on_{0}'.format(arena_item_id))
                arena_running = True
                action_list.append('🔎Поиск соперника')
                log('Топаем на арену')

        elif 'В казне недостаточно' in text:
            log("Стройка не удалась, в замке нет денег")

        elif corovan_enabled and text.find(' /go') != -1:
            action_list.append(orders['corovan'])

        elif 'доволен.' in text:
            log('Поиграли с питомцем')
            last_pet_play = round(time())
            
        elif text.find('Запас еды:') != -1:
            play_state = pet_char_states[re.search('⚽ (.+)', text).group(1)]
            food_state = pet_char_states[re.search('🍼 (.+)', text).group(1)]
            wash_state = pet_char_states[re.search('🛁 (.+)', text).group(1)]
            food_rest = int(re.search('Запас еды: (\d+)', text).group(1))
            log('⚽️{0} 🍼{1} 🛁{2} Запас еды {3}'.format(play_state, food_state, wash_state, food_rest))
            if food_rest <= 2:
                ifttt('pet_food', food_rest, None)
            if play_state <= 4 and round(time())-last_pet_play >= 3600:
                action_list.append(orders['pet_play'])
            if food_state <= 3 and food_rest != 0:
                action_list.append(orders['pet_feed'])
            if wash_state <= 4:
                action_list.append(orders['pet_wash'])
        
        elif text.find('Битва семи замков через') != -1:
            if castle_name is None:
                castle_name = flags[re.search('(.{2}).*, .+ замка', text).group(1)]
                log('Замок: '+castle_name)
                castle = orders[castle_name]
            class_available = bool(re.search('Определись со специализацией', text))
            hero_message_id = message_id
            endurance = int(re.search('Выносливость: (\d+)', text).group(1))
            endurancetop = int(re.search('Выносливость: (\d+)/(\d+)', text).group(2))
            gold = int(re.search('💰(-?[0-9]+)', text).group(1))
            inv = re.search('🎒Рюкзак: ([0-9]+)/([0-9]+)', text)
            level = int(re.search('🏅Уровень: (\d+)', text).group(1))
            log('Уровень: {0}, золото: {1}, выносливость: {2} / {3}, Рюкзак: {4} / {5}'.format(level, gold, endurance, endurancetop, inv.group(1), inv.group(2)))
            pet_state = 'no_pet'
            if re.search('Помощник:', text) is not None:
                # жевотне обнаружено
                pet_state = pet_states[re.search('Помощник:\n.+\(.+\) (.+) /pet', text).group(1)]
            m = re.search('Битва семи замков через (?:(?:(\d+)ч)? ?(?:(\d+) минут)?|несколько секунд)', text)
            if not m and re.search('Межсезонье', text):
                m = re.search('Битва семи замков через (?:(?:(\d+)ч)? ?(?:(\d+) минут)?|несколько секунд)', 'Битва семи замков через 10000ч 100 минут')
            if not m.group(1):
                if m.group(2) and int(m.group(2)) <= 29:
                    report = True
                    state = re.search('Состояние:\n(.*)', text).group(1)
                    if auto_def_enabled and time() - current_order['time'] > 1800 and 'Отдых' in state:
                        if castle_name == 'red':
                            fwd('@', redstat_bot, hero_message_id)
                            log("отправляем профиль легату")
                        elif castle_name == 'blue':
                            fwd('@', blueoysterbot, hero_message_id)
                            log("отправляем профиль ойстеру")
                        if donate_enabled:
                            if int(inv.group(1)) == int(inv.group(2)):
                                log('Полный рюкзак - Донат в лавку отключен')
                                donate_buying = False
                            if gold > gold_to_left:
                                if donate_buying:
                                    log('Донат {0} золота в лавку'.format(gold - gold_to_left))
                                    action_list.append(orders['castle_menu'])
                                    action_list.append(orders['lavka'])
                                    action_list.append(orders['shlem'])
                                    while (gold - gold_to_left) >= 35:
                                        gold -= 35
                                        action_list.append('/buy_helmet2')
                                    while (gold - gold_to_left) > 0:
                                        gold -= 1
                                        action_list.append('/buy_helmet1')
                                        action_list.append('/sell_206')
                                else:
                                    log('Донат {0} золота в казну замка'.format(gold - gold_to_left))
                                    action_list.append('/donate {0}'.format(gold - gold_to_left))
                                    gold -= gold_to_left
                        update_order(castle)
                    return
                else:
                    # если битва через несколько секунд
                    report = True
                    return
            time_to_war = int(m.group(1) if m.group(1) else 0) * 60 + int(m.group(2) if m.group(2) else 0)
            log('Времени достаточно. До боя осталось {0} минут'.format(time_to_war))
            if report:
                action_list.append('/report')
                sleep(random.randint(3, 6))
                log('запросили репорт по битве')
                report = False
            if text.find('🛌Отдых') == -1 and text.find('🛡Защита ') == -1:
                log('Чем-то занят, ждём')
            else:
                # Подумаем, а надо ли так часто ходить куда нибудь )
                if not build_enabled:
                    log('на стройку нам не нужно')
                    curhour = datetime.now(tz).hour
                    if not arena_enabled or arena_delay or curhour > 23 or curhour < 8:
                        log('на арену тоже не нужно')
                        if int(endurancetop) - int(endurance) >= 5:
                            # минут за 35-45 до битвы имеет смысл выйти из спячки
                            sleeping = time_to_war * 60 - 60 * random.randint(35, 45)
                            log('выносливости мало, можно и подремать до боя {0} минут'.format(int(sleeping / 60)))
                            lt_info = time()
                            get_info_diff = sleeping
                            return
                    elif gold < 5 and endurance == 0 and time_to_war > 60:
                        sleeping = 60 * random.randint(30, 40)
                        log('выносливости нет, денег нет, можно и подремать до боя {0} минут'.format(int(sleeping / 60)))
                        lt_info = time()
                        get_info_diff = sleeping

                if text.find('🛌Отдых') != -1 and arena_running:
                    arena_running = False
                    
                if re.search('Помощник:', text) is not None and pet_state == 'med' or pet_state == 'bad': 
                    log('Идем проверить питомца')
                    action_list.append('/pet')
                
                elif peshera_enabled and endurance >= 2 and level >= 7:
                    if les_enabled:
                        action_list.append(orders['quests'])
                        action_list.append(random.choice([orders['peshera'], orders['les']]))
                    else:
                        action_list.append(orders['quests'])
                        action_list.append(orders['peshera'])

                elif les_enabled and not peshera_enabled and endurance >= 1 and orders['les'] not in action_list:
                    action_list.append(orders['quests'])
                    action_list.append(orders['les'])

                elif more_enabled and not les_enabled and not peshera_enabled and endurance >= 1 and orders['more'] not in action_list:
                    action_list.append(orders['quests'])
                    action_list.append(orders['more'])

                elif arena_enabled and not arena_delay and gold >= 5 and not arena_running and level >= 5:
                    curhour = datetime.now(tz).hour
                    if 9 <= curhour <= 23:
                        action_list.append(orders['castle_menu'])
                        action_list.append('📯Арена')
                    else:
                        log('По часам не проходим на арену. Сейчас ' + str(curhour) + ' часов')
                        if build_enabled and level >= 10:
                            log('Пойдем строить')
                            if random.randint(0, 1) == 0:
                                action_list.append(build_target)
                            else:
                                action_list.append(orders['castle_menu'])
                                action_list.append('🏘Постройки')
                                action_list.append('🚧Стройка')
                                action_list.append(build_target)

                elif build_enabled and level >= 10:
                    log('Пойдем строить')
                    if random.randint(0, 1) == 0:
                        action_list.append(build_target)
                    else:
                        action_list.append(orders['castle_menu'])
                        action_list.append('🏘Постройки')
                        action_list.append('🚧Стройка')
                        action_list.append(build_target)

        elif arena_enabled and text.find('выбери точку атаки и точку защиты') != -1:
            arena_running = True #на случай, если арена запущена руками
            lt_arena = time()
            lt_info = time()
            get_info_diff = random.randint(400, 500)
            attack_chosen = arena_attack[random.randint(0, 2)]
            cover_chosen = arena_cover[random.randint(0, 2)]
            log('Атака: {0}, Защита: {1}'.format(attack_chosen, cover_chosen))
            sleep(random.randint(2,6))
            if random.randint(0,1):
                action_list.append(attack_chosen)
                action_list.append(cover_chosen)
            else:
                action_list.append(cover_chosen)
                action_list.append(attack_chosen)

        elif text.find('Победил воин') != -1 or text.find('Ничья') != -1:
            lt_info = time()
            get_info_diff = random.randint(60, 120)
            log('Выключаем флаг - арена закончилась')
            arena_running = False
            if arena_change_enabled: 
                action_list.append('/on_{0}'.format(non_arena_item_id))

        elif quest_fight_enabled and text.find('/fight') != -1:
            if fight_path != '':
                c = re.search('(\/fight.*)', text).group(1)
                action_list.append(c)
                file_name = fight_path+castle_name+str(port)
                f = open(file_name, 'w')
                f.write(c)
                f.close()
            else:
                c = re.search('\/fight.*', text).group(0)
                action_list.append(c)
                fwd(pref, msg_receiver, message_id)

    elif username == 'ChatWarsCaptchaBot':
        if len(text) <= 4 and text in captcha_answers.values():
            sleep(3)
            action_list.append(text)
            bot_enabled = True

    elif username == 'ChatWarsTradeBot' and twinkstock_enabled and (firststock_enabled or secondstock_enabled):
        if text.find('Твой склад с материалами') != -1:
            stock_id = message_id
            if firststock_enabled:
                fwd('@', stock_bot, stock_id)
            if secondstock_enabled:
                fwd('@', stock2_bot, stock_id)
            twinkstock_enabled = False
            send_msg(pref, msg_receiver, 'Сток обновлен')

    elif username == 'ChatWarsTradeBot' and len(resource_id_list)!= 0 and trade_active == False:
        log('добавляем ресурсы по списку..')
        trade_active = True
        for res_id in resource_id_list:
            if re.search('\/add_'+res_id+' ', text):
                count = re.search('/add_'+res_id+'\D+(.*)', text).group(1)
                send_msg('@',trade_bot,'/add_'+res_id+' '+str(count))
                log('Добавили '+str(count)+' шт. ресурса '+res_id)
                send_msg(pref, msg_receiver, 'Добавлено '+str(count)+' шт. ресурса '+res_id)
                sleep_time = random.randint(2, 5)
                sleep(sleep_time)
            else:
                log('На складе нет ресурса '+res_id)
                send_msg(pref, msg_receiver, 'На складе нет ресурса '+res_id)
        resource_id_list=[]
        send_msg('@',trade_bot,'/done')
        log('Предложение готово')
        trade_active = False
        send_msg(pref, msg_receiver, 'Предложение готово ')

    else:
        if quest_fight_enabled and text.find('/fight') != -1 and level >= 15:
            c = re.search('\/fight.*', text).group(0)
            action_list.append(c)
    
        if bot_enabled and order_enabled and (username in order_usernames or username == admin_username):
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
            elif text.find(orders['mint']) != -1:
                update_order(orders['mint'])
            elif text.find(orders['twilight']) != -1:
                update_order(orders['twilight'])
            elif text.find('🌲') != -1:
                update_order(orders['lesnoi_fort'])
            elif text.find('⛰') != -1:
                update_order(orders['gorni_fort'])
            elif text.find('⚓️') != -1:
                update_order(orders['morskoi_fort'])
            elif text.find('🛡') != -1:
                update_order(castle)

        # send_msg(pref, admin_username, 'Получили команду ' + current_order['order'] + ' от ' + username)
        if username == admin_username:
            if text == '#help':
                send_msg(pref, msg_receiver, '\n'.join([
                    '#enable_bot - Включить бота',
                    '#disable_bot - Выключить бота',
                    '#enable_arena - Включить арену',
                    '#disable_arena - Выключить арену',
                    '#enable_les - Включить лес',
                    '#disable_les - Выключить лес',
                    '#enable_peshera - Включить пещеры',
                    '#disable_peshera - Выключить пещеры',
                    '#enable_more - Включить побережье',
                    '#disable_more - Выключить побережье',
                    '#enable_corovan - Включить корован',
                    '#disable_corovan - Выключить корован',
                    '#enable_order - Включить приказы',
                    '#disable_order - Выключить приказы',
                    '#enable_auto_def - Включить авто деф',
                    '#disable_auto_def - Выключить авто деф',
                    '#enable_donate - Включить донат',
                    '#disable_donate - Выключить донат',
                    '#enable_quest_fight - Включить битву во время квестов',
                    '#disable_quest_fight - Выключить битву во время квестов',
                    '#enable_buy - Включить донат в лавку вместо казны',
                    '#disable_buy - Вылючить донат в лавку вместо казны',
                    '#set_arena_change *id предмета на арене* *id предмета вне арены* - Включить переодевание перед ареной и после нее (например рапира и кирка)',
                    '#disable_arena_change - Выключить переодевание перед ареной и после нее',
                    "#lvl_atk - качать атаку",
                    "#lvl_def - качать защиту",
                    "#lvl_off - ничего не качать",
                    '#status - Получить статус',
                    '#hero - Получить информацию о герое',
                    '#push_order - Добавить приказ ({0})'.format(','.join(orders)),
                    '#order - Дебаг, последняя команда защиты/атаки замка',
                    '#log - Дебаг, последние 30 сообщений из лога',
                    '#time - Дебаг, текущее время',
                    '#lt_arena - Дебаг, последняя битва на арене',
                    '#get_info_diff - Дебаг, последняя разница между запросами информации о герое',
                    '#ping - Дебаг, проверить жив ли бот',
                    '#enable_build - Включить постройки',
                    '#disable_build - Выключить постройки',
                    '#build_target - указать цель постройки/починки ({0})'.format(','.join(builds)),
                    '#stock - Обновить стоки',
                    '#info - Немного оперативной информации',
                    '#detail - Почти вся информация о герое, только компактнее',
                    '#report - Получить репорт с прошлой битвы',
                    '#enable_first_stock - Включить отправку стока в первого стокбота(Penguindum)',
                    '#disable_first_stock - Выключить отправку стока в первого стокбота(Penguindum)',
                    '#enable_second_stock - Включить отправку стока во второго стокбота(Капибара-банкир)',
                    '#disable_second_stock - Выключить отправку стока во второго стокбота(Капибара-банкир)',
                    '#report - Получить репорт с прошлой битвы',
                    '#eval - Дебаг, выполнить запрос вручную'
                ]))

            # отправка info
            elif text == '#info':
                infotext = '🕯' if class_available else ''
                infotext += '{0}{1}, 💰{2}, 🔋{3}/{4}'.format(castle, level, gold, endurance, endurancetop)
                if arenafight.group(2) != '0':
                    infotext += ', 🤺{0}/{1}, 🌟{2}'.format(arenafight.group(1), arenafight.group(2), victory)
                send_msg(pref, msg_receiver, infotext)

            # Вкл/выкл бота
            elif text == '#enable_bot':
                bot_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Бот успешно включен')
            elif text == '#disable_bot':
                bot_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Бот успешно выключен')

            # отправка стока
            elif text == '#stock':
                if level >= 15:
                    if firststock_enabled or secondstock_enabled:
                        twinkstock_enabled = True
                        send_msg('@',trade_bot,'/start')
                    else:
                        send_msg(pref, msg_receiver, 'Ты просишь меня обновить сток. Но ты даже не включил ни одного стокбота.')
                else:
                    send_msg(pref, msg_receiver, 'Я еще не дорос, у меня только '+str(level)+' уровень')

            # Вкл/выкл арены
            elif text == '#enable_arena':
                arena_enabled = True
                write_config()
                lt_info = time()
                get_info_diff = random.randint(400, 500)
                if level >= 5:
                    send_msg(pref, msg_receiver, 'Арена успешно включена')
                    log('Арена успешно включена, скоро пойдем бить морды')
                else:
                    send_msg(pref, msg_receiver, 'Арена успешно включена, но у меня только {0} уровень'.format(level))
                    log('Арена успешно включена, скоро пойдем бить морды, но у меня только {0} уровень'.format(level))
            elif text == '#disable_arena':
                arena_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Арена успешно выключена')

            # Вкл/выкл леса
            elif text == '#enable_les':
                les_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Лес успешно включен')
            elif text == '#disable_les':
                les_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Лес успешно выключен')

            # Вкл/выкл пещеры
            elif text == '#enable_peshera':
                peshera_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Пещеры успешно включены')
            elif text == '#disable_peshera':
                peshera_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Пещеры успешно выключены')

            # Вкл/выкл побережье
            elif text == '#enable_more':
                more_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Побережье успешно включено')
            elif text == '#disable_more':
                more_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Побережье успешно выключено')

            # Вкл/выкл корована
            elif text == '#enable_corovan':
                corovan_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Корованы успешно включены')
            elif text == '#disable_corovan':
                corovan_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Корованы успешно выключены')

            # Вкл/выкл команд
            elif text == '#enable_order':
                order_enabled = True
                send_msg(pref, msg_receiver, 'Приказы успешно включены')
            elif text == '#disable_order':
                order_enabled = False
                send_msg(pref, msg_receiver, 'Приказы успешно выключены')

            # Вкл/выкл авто деф
            elif text == '#enable_auto_def':
                auto_def_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Авто деф успешно включен')
            elif text == '#disable_auto_def':
                auto_def_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Авто деф успешно выключен')

            # Вкл/выкл авто донат
            elif text == '#enable_donate':
                donate_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Донат успешно включен')
            elif text == '#disable_donate':
                donate_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Донат успешно выключен')

            # Вкл/выкл донат в лавку
            elif text == '#enable_buy':
                donate_buying = True
                write_config()
                send_msg(pref, msg_receiver, 'Донат в лавку успешно включен')
            elif text == '#disable_buy':
                donate_buying = False
                write_config()
                send_msg(pref, msg_receiver, 'Донат в лавку успешно выключен')
            
            # Вкл/выкл переодевание перед ареной и после нее
            elif text.startswith('#set_arena_change'):
                arena_change_enabled = True
                arena_item_id = text.split(' ')[1]
                non_arena_item_id = text.split(' ')[2]
                write_config()
                send_msg(pref, msg_receiver, 'Переодевание перед ареной и после нее успешно включено. На арене - {0}, вне арены - {1}'.format(arena_item_id, non_arena_item_id))
            elif text == '#disable_arena_change':
                arena_change_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Переодевание перед ареной и после нее успешно выключено')
            
            # Вкл/выкл битву по время квеста
            elif text == '#enable_quest_fight':
                quest_fight_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Битва включена')
            elif text == '#disable_quest_fight':
                quest_fight_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Битва отключена')

            # что качать при левелапе
            elif text == '#lvl_atk':
                lvl_up = 'lvl_atk'
                write_config()
                send_msg(pref, msg_receiver, 'Качаем атаку')
            elif text == '#lvl_def':
                lvl_up = 'lvl_def'
                write_config()
                send_msg(pref, msg_receiver, 'Качаем защиту')
            elif text == '#lvl_off':
                lvl_up = 'lvl_off'
                write_config()
                send_msg(pref, msg_receiver, 'Не качаем ничего')

            # Получить статус
            elif text == '#status':
                send_msg(pref, msg_receiver, '\n'.join([
                    '🤖Бот включен: {0}',
                    '📯Арена включена: {1}',
                    '🔎Сейчас на арене: {2}',
                    '🌲Лес включен: {3}',
                    '🕸Пещеры включены: {4}',
                    '🏝Побережье включено: {5}',
                    '🐫Корованы включены: {6}',
                    '🇪🇺Приказы включены: {7}',
                    '🛡Авто деф включен: {8}',
                    '💰Донат включен: {9}',
                    '🏚Донат в лавку вместо казны: {10}',
                    '🌟Левелап: {11}',
                    '🏘Постройка включена: {12}',
                    '🚧Цель постройки: {13}',
                ]).format(bot_enabled, arena_enabled, arena_running, les_enabled, peshera_enabled, more_enabled, corovan_enabled, order_enabled,
                          auto_def_enabled, donate_enabled, donate_buying,orders[lvl_up],build_enabled,build_target))

            # Информация о герое
            elif text == '#hero':
                if hero_message_id == 0:
                    send_msg(pref, msg_receiver, 'Информация о герое пока еще недоступна')
                else:
                    fwd(pref, msg_receiver, hero_message_id)
            
            # Информация о герое
            elif text == '#report':
                if report_message_id == 0:
                    send_msg(pref, msg_receiver, 'Информация о репорте пока еще недоступна')
                else:
                    fwd(pref, msg_receiver, report_message_id)
            
            elif text == '#detail':
                if hero_message_id == 0:
                    send_msg(pref, msg_receiver, 'Информация о герое пока еще недоступна')
                else:
                    heroText  = sender.message_get(hero_message_id).text
                    template  = '{0}{1} {2}, 🏅{3}, ⚔️{4} 🛡{5}\n🔥{6}/{7} 🔋{8}/{9} 💰{10}\n🎽{11}'
                    heroName  = re.search('.{2}(.*), (\w+) \w+ замка', heroText).group(1)
                    heroClass = re.search('.{2}(.*), (\w+) \w+ замка', heroText).group(2)
                    heroAtk   = re.search('⚔Атака: (\d+) 🛡Защита: (\d+)', heroText).group(1)
                    heroDef   = re.search('⚔Атака: (\d+) 🛡Защита: (\d+)', heroText).group(2)
                    heroExpNow  = re.search('🔥Опыт: (\d+)/(\d+)', heroText).group(1)
                    heroExpNext = re.search('🔥Опыт: (\d+)/(\d+)', heroText).group(2)
                    heroEquip = re.sub('\+', '', re.search('🎽Экипировка (.+)', heroText).group(1))
                    # heroState = re.search('Состояние:\n(.+)', heroText).group(1)
                    send_msg(pref, msg_receiver, template.format(castle, heroClass, heroName, level, heroAtk, heroDef, heroExpNow, heroExpNext, endurance, endurancetop, gold, heroEquip))

            # Получить лог
            elif text == '#log':
                send_msg(pref, msg_receiver, '\n'.join(log_list))
                log_list.clear()
                log('Лог запрошен и очищен')

            elif text == '#lt_arena':
                send_msg(pref, msg_receiver, str(lt_arena))

            elif text == '#order':
                text_date = datetime.fromtimestamp(current_order['time']).strftime('%Y-%m-%d %H:%M:%S')
                send_msg(pref, msg_receiver, current_order['order'] + ' ' + text_date)

            elif text == '#time':
                text_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                send_msg(pref, msg_receiver, text_date)

            elif text == '#ping':
                send_msg(pref, msg_receiver, '#pong')

            elif text == '#get_info_diff':
                send_msg(pref, msg_receiver, str(get_info_diff))

            elif text.startswith('#push_order'):
                command = text.split(' ')[1]
                if command in orders:
                    update_order(orders[command])
                    send_msg(pref, msg_receiver, 'Команда ' + command + ' применена')
                else:
                    send_msg(pref, msg_receiver, 'Команда ' + command + ' не распознана')

            elif text.startswith('#build_target'):
                command = text.split(' ')[1]
                if command in builds:
                    build_target = builds[command]
                    send_msg(pref, msg_receiver, 'Постройка ' + builds[command] + ' установлена')
                    write_config()
                else:
                    send_msg(pref, msg_receiver, 'Постройка ' + command + ' не распознана')

            elif text.startswith('#captcha'):
                command = text.split(' ')[1]
                if command in captcha_answers:
                    action_list.append(captcha_answers[command])
                    bot_enabled = True
                    send_msg('@', admin_username, 'Команда ' + command + ' применена')
                else:
                    send_msg('@', admin_username, 'Команда ' + command + ' не распознана')

            # Вкл/выкл построек
            elif text == '#enable_build':
                build_enabled = True
                write_config()
                lt_info = time()
                get_info_diff = random.randint(400, 500)
                send_msg(pref, msg_receiver, 'Постройка успешно включена')
                log('Постройка успешно включена, скоро пойдем строить')
            elif text == '#disable_build':
                build_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Постройка успешно выключена')

            elif text.startswith('#add'):
                if level >= 15:
                    resource_id_list = text.split(' ')[1].split(',')
                    send_msg('@', trade_bot, '/start')
                else:
                    send_msg(pref, msg_receiver, 'Я еще не дорос, у меня только '+str(level)+' уровень')

            # Вкл/выкл первого стокобота
            elif text == '#enable_first_stock':
                firststock_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Первый сток успешно включён')
            elif text == '#disable_first_stock':
                firststock_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Первый сток успешно выключен')

            # Вкл/выкл второго стокобота
            elif text == '#enable_second_stock':
                secondstock_enabled = True
                write_config()
                send_msg(pref, msg_receiver, 'Второй сток успешно включён')
            elif text == '#disable_second_stock':
                secondstock_enabled = False
                write_config()
                send_msg(pref, msg_receiver, 'Второй сток успешно выключен')

            elif text.startswith('#eval'):
                eval(re.search('#eval (.+)', text).group(1))


def send_msg(pref, to, message):
    sender.send_msg(pref + to, message)


def fwd(pref, to, message_id):
    sender.fwd(pref + to, message_id)


def ifttt(event, val2, val3):
    requests.get("https://maker.ifttt.com/trigger/"+event+"/with/key/"+apikey, params={'value1': str(port), 'value2': val2, 'value3': val3})


def update_order(order):
    current_order['order'] = order
    current_order['time'] = time()
    if order == castle:
        action_list.append(orders['cover'])
    else:
        action_list.append(orders['attack'])
    action_list.append(order)


def log(text):
    message = '{0:%Y-%m-%d+ %H:%M:%S}'.format(datetime.now()) + ' ' + text
    print(message)
    log_list.append(message)


if __name__ == '__main__':
    receiver = Receiver(sock=socket_path) if socket_path else Receiver(port=port)
    receiver.start()  # start the Connector.
    _thread.start_new_thread(queue_worker, ())
    receiver.message(work_with_message(receiver))
    receiver.stop()
