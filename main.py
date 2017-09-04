#!/usr/bin/python3
# coding=utf-8
import telethon
import traceback
import threading
import random
import json
import re
import pytz
import os
from collections import deque

from telethon import TelegramClient
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.utils import get_input_peer
from telethon.errors import SessionPasswordNeededError
from telethon.utils import get_display_name
from telethon.tl.types import UpdateShortChatMessage, UpdateShortMessage, InputPeerEmpty
from telethon.tl.types.update_new_message import UpdateNewMessage
from telethon.tl.types.update_edit_channel_message import UpdateEditChannelMessage
from telethon.tl.types.update_chat_user_typing import UpdateChatUserTyping
from telethon.tl.types.update_user_status import UpdateUserStatus
from telethon.tl.types.update_read_history_inbox import UpdateReadHistoryInbox
from telethon.tl.types.update_channel_pinned_message import UpdateChannelPinnedMessage
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.messages import GetChatsRequest
from telethon.tl.functions.messages import GetHistoryRequest, GetDialogsRequest
from telethon.tl.functions.messages import ReceivedMessagesRequest
from telethon.tl.functions.messages import ForwardMessageRequest
from telethon.tl.functions.messages import get_messages
from telethon.tl.functions.messages import GetInlineBotResultsRequest, SendInlineBotResultRequest, GetDialogsRequest, GetBotCallbackAnswerRequest
from telethon.tl.functions.contacts import SearchRequest, ResolveUsernameRequest
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from telethon.tl.functions.account  import UpdateNotifySettingsRequest, CheckUsernameRequest, UpdateUsernameRequest

from collections import deque
from time import time, sleep
from getopt import getopt
from datetime import datetime
from threading import Timer, Thread
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
# from telethon.tl.types import InputUser, InputPeerUser, InputPeerChannel, InputPeerSelf, InputPeerEmpty
from telethon.tl.types import *
import sys
import os
import re
import _thread
import random
import pytz
import configparser
import requests
import names

pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname)

TOTALLY_IGNORED_MESSAGE_TYPES = [
    telethon.tl.types.update_chat_user_typing.UpdateChatUserTyping,
    telethon.tl.types.update_user_typing.UpdateUserTyping,
    telethon.tl.types.update_user_status.UpdateUserStatus,
    telethon.tl.types.update_read_history_inbox.UpdateReadHistoryInbox,
    telethon.tl.types.update_read_history_outbox.UpdateReadHistoryOutbox,
    telethon.tl.types.update_read_channel_inbox.UpdateReadChannelInbox,
    telethon.tl.types.update_read_channel_outbox.UpdateReadChannelOutbox,
    telethon.tl.types.update_delete_channel_messages.UpdateDeleteChannelMessages,
    telethon.tl.types.update_draft_message.UpdateDraftMessage,
]

api_id = 67656
api_hash = 'd6b2cb5d21032b39b53d9a51c2021934'

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
trade_bot_telethon = None

redstat_bot = 'RedStatBot'
redstat2_bot = 'CWRedCastleBot'

blueoysterbot = 'BlueOysterBot'

# номер для логина
phone = None

# скидывание денег покупкой/продажей шлемов
donate_buying = False

# включить прокачку при левелапе
lvl_up = 'lvl_off'

# имя группы
group_name = None

build_target = '/build_hq'

# id ресурса для трейда
resource_id_list = []

# config = configparser.ConfigParser()

# user_id бота, используется для поиска конфига
bot_user_id = ''

gold_to_left = 0

# apikey для IFTTT
apikey = None

# пароль для двухшаговой авторизации
telethon_pw = ''

# зайдет в маркет, если нет диалога
join_market = False

# путь к конфигу
config_path = ''

# регистрировать номер
reg_number = False
reg_apikey = None
reg_service = None
reg_generate_name = False

# стандартный конфиг
config = {
    'bot_enabled': True,
    'les_enabled': True,
    'peshera_enabled': False,
    'arena_enabled': True,
    'coast_enabled': False,
    'corovan_enabled': True,
    'order_enabled': True,
    'auto_def_enabled': True,
    'donate_enabled': False,
    'quest_fight_enabled': True,
    'pet_enabled': False,
    'lvl_up': 'lvl_atk',
    'build_enabled': False,
    'build_target': '/build_hq',
    'autodonate_enabled': True
}

opts, args = getopt(sys.argv[1:], 'ja:o:p:g:bl:n:k:w:r:', ['join', 'admin=', 'order=', 'phone=',
                                                             'gold=', 'buy', 'lvlup=', 'group_name=', 'apikey=', '2sp=', 'reg=', 'reg-service=', 'gen-name'])
# todo:повторную проверку аргументов после загрузки конфига из файла (перезаписывать значения)
for opt, arg in opts:
    if opt in ('-a', '--admin'):
        admin_username = arg
    elif opt in ('-o', '--order'):
        order_usernames = arg.split(',')
    elif opt in ('-p', '--phone'):
        phone = re.sub('[()-+ ]', '', arg)
    elif opt in ('-g', '--gold'):
        gold_to_left = int(arg)
    elif opt in ('-b', '--buy'):
        donate_buying = True
    elif opt in ('-l', '--lvlup'):
        config['lvl_up'] = arg
    elif opt in ('-n', '--group_name'):
        group_name = arg
    elif opt in ('-k', '--apikey'):
        apikey = str(arg)
    elif opt in ('-w', '--2sp'):
        telethon_pw = str(arg)
    elif opt in ('-j', '--join'):
        join_market = True
    elif opt in ('-r'):
        reg_number = True
        reg_apikey = str(arg)
    elif opt in ('--reg-service'):
        reg_service = arg
    elif opt in ('--gen-name'):
        reg_generate_name = True

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
    'sea_fort': '⚓Морской форт',
    'coast': '🏝Побережье',
    'gorni_fort': '⛰Горный форт',
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
    'more': '🏝Побережье',
    'pet_play': '⚽Поиграть',
    'pet_feed': '🍼Покормить',
    'pet_wash': '🛁Почистить',
    'back': '⬅️Назад',
    'arena': '📯Арена',
    'arena_search': '🔎Поиск соперника',
    'arena_stop': '✖️Отменить поиск'
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
# текущий приказ на атаку/защиту, по умолчанию всегда защита, трогать не нужно
current_order = {'time': 0, 'order': orders['blue']}

def authorize(client, phone_num):
    client.send_code_request(phone_num)
    client_user = None
    while client_user is None:
        code = input('Enter the code you just received: ')
        try:
            client_user = client.sign_in(phone_num, code)
            # Two-step verification may be enabled
        except SessionPasswordNeededError:
            pw = input('Two step verification password: ')
            client_user = client.sign_in(password=pw)


class Reg(object):
    def __init__(self, service):
        self.service = service

    def send_request(self, method, params=None):
        if self.service == 'sms-reg':
            if not params:
                params = {}
            if not getattr(params, 'apikey', None):
                params['apikey'] = reg_apikey
            r = requests.get('http://api.sms-reg.com/{0}.php'.format(method), params=params)
            return r.json()

    def get_balance(self):
        balance_request = self.send_request('getBalance')

        if balance_request['response'] != "1":
            raise Exception('Ошибка при получении баланса: ' + balance_request['error_msg'])

        return float(balance_request['balance'])

    def get_tzid(self):
        get_num_request = self.send_request('getNum', {'service': 'telegram'})

        if get_num_request['response'] != "1":
            raise Exception('Ошибка при получении номера: '+get_num_request['error_msg'])

        return int(get_num_request['tzid'])

    def wait_num(self, tzid):
        number = None

        while number is None:
            state_request = self.send_request('getState', {'tzid': tzid})
            if state_request['response'] == "WARNING_NO_NUMS":
                raise Exception('Нет свободных номеров, попробуй еще раз через 5 минут')
            elif state_request['response'] == "TZ_INPOOL":
                print('Жду номера')
                sleep(10)
            elif state_request['response'] == "TZ_NUM_PREPARE":
                number = state_request['number']
                print('Получен номер: {0}'.format(number))
            else:
                print('Другой ответ: {0}'.format(state_request['response']))
        return number

    def set_ready(self, tzid):
        set_ready_request = self.send_request('setReady', {'tzid': tzid})
        if set_ready_request['response'] != "1":
            raise Exception('Ошибка при отправке готовности: '+set_ready_request['error_msg'])

    def wait_code(self, tzid):
        code = None

        while code is None:
            state_request = self.send_request('getState', {'tzid': tzid})
            if state_request['response'] == "TZ_NUM_WAIT":
                print('Жду код')
                sleep(10)
            elif state_request['response'] == "TZ_NUM_ANSWER":
                code = state_request['number']
                print('Получен код: {0}'.format(code))
            else:
                print('Другой ответ: {0}'.format(state_request['response']))
        return code

    def set_ok(self, tzid):
        set_ok_request = self.send_request('setOperationOk', {'tzid': tzid})
        if set_ok_request['response'] != "1":
            raise Exception('Ошибка при завершении операции: '+set_ok_request['error_msg'])


def get_buttons(message):
    if not getattr(message, 'reply_markup', None):
        return []
    result = []
    rows = getattr(message.reply_markup, 'rows', [])
    for row in rows:
        buttons = getattr(row, 'buttons', [])
        for btn in buttons:
            if hasattr(btn, 'text'):
                result.append(btn.text)
    return result


class ChatWarsAutomator(object):
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.action_list = deque([])
        self.log_list = deque([], maxlen=30)
        self.intent = 'INIT'
        self.latest_buttons = []
        self.tz = pytz.timezone('Europe/Moscow')
        self.message_queue = []
        self.message_queue_lock = threading.Lock()
        self.last_message_received = datetime.now()
        self.arena_running = False
        self.get_info_diff = random.randint(420, 900)
        self.castle_name = None
        self.castle = None
        self.lt_info = 0
        self.lt_arena = 0
        self.hero_message = None
        self.current_order = {'time': 0, 'order': orders['blue']}
        self.arena_delay = False
        self.arena_delay_day = -1
        self.endurance = 0
        self.endurancetop = 0
        self.gold = 0
        self.petstatus = 'нет'
        self.time_to_war = 0
        self.report = False  # получение репорта после боя
        self.arenafight = re.search('Поединков сегодня ([0-9]+) из ([0-9]+)', 'Поединков сегодня 0 из 0')
        self.victory = 0  # количество побед на арене
        self.level = 0  # уровень героя
        self.petcount = 0  # счетчик попыток кормления пета
        self.twinkstock_enabled = False
        self.tradeadd = False
        self.botid = 0
        self.pet_state = 'no_pet'
        self.last_pet_play = 0
        self.class_available = False
        self.res_id_list = []
        self.CHATWARS_PROPS   = self.find_props('ChatWarsBot')
        self.CAPTCHA_PROPS    = self.find_props('ChatWarsCaptchaBot')
        self.TRADEBOT_PROPS   = self.find_props('ChatWarsTradeBot')
        self.STOCKBOT_PROPS   = self.find_props('PenguindrumStockBot')
        self.REDSTAT_PROPS    = self.find_props('RedStatBot')
        self.REDSTAT2_PROPS   = self.find_props('CWRedCastleBot')
        self.BLUEOYSTER_PROPS = self.find_props('BlueOysterBot')
        self.MARKET_PROPS     = self.find_props('ChatWarsMarket')
        self.ADMIN_PROPS      = self.find_props(admin_username)
        self.GROUP_PROPS      = self.find_group_id(group_name)
        self.ALL_PROPS = [self.CHATWARS_PROPS, self.ADMIN_PROPS, self.CAPTCHA_PROPS, self.STOCKBOT_PROPS,
                          self.TRADEBOT_PROPS, self.REDSTAT_PROPS, self.REDSTAT2_PROPS, self.BLUEOYSTER_PROPS]
        self.ADMIN_ID    = self.find_props_id(admin_username)
        self.CHATWARS_ID = self.find_props_id('ChatWarsBot')
        self.TRADEBOT_ID = self.find_props_id('ChatWarsTradeBot')
        self.STOCKBOT_ID = self.find_props_id('PenguindrumStockBot')
        self.chatwars_dialog  = self.find_dialog_user('ChatWarsBot')
        self.captcha_dialog   = self.find_dialog_user('ChatWarsCaptchaBot')
        self.redstat_dialog   = self.find_dialog_user('RedStatBot')
        self.redstat2_dialog  = self.find_dialog_user('CWRedCastleBot')
        self.blueyster_dialog = self.find_dialog_user('BlueOysterBot')
        self.tradebot_dialog  = self.find_dialog_user('ChatWarsTradeBot')
        self.stockbot_dialog  = self.find_dialog_user('PenguindrumStockBot')
        self.market_dialog    = self.find_dialog_chat('ChatWarsMarket')
        self.market_chat      = self.get_market_input_peer()
        if group_name is not None:
            self.admin_dialog = self.find_dialog(self.GROUP_PROPS)
        else:
            self.admin_dialog = self.find_dialog_user(admin_username)

        if join_market:
            if self.market_dialog.left:
                # не в чате
                self.client.invoke(JoinChannelRequest(self.market_dialog))
                self.market_dialog = self.find_dialog_chat('ChatWarsMarket')
            market_full = self.client.invoke(GetFullChannelRequest(self.market_dialog)).full_chat
            if market_full.notify_settings.mute_until != 0:
                # замьючен
                market_notify_peer = InputNotifyPeer(self.market_chat)
                self.client.invoke(UpdateNotifySettingsRequest(market_notify_peer, InputPeerNotifySettings(0, 'default')))

    def find_dialog_user(self, username: str):
        return self.client.invoke(ResolveUsernameRequest(username)).users[0]

    def find_dialog(self, props: object) -> object:
        ATTEMPTS = 3
        for i in range(ATTEMPTS):  # get_dialogs is unstable method
            try:
                dialogs = self.client.get_dialogs(limit=100)
                for entity in dialogs[1]:
                    if all(hasattr(entity, k) and getattr(entity, k) == v for k, v in props.items()):
                        return entity
                print('Cannot find dialog with props: %s. :c' % props)
                return None
            except Exception as e:
                if i + 1 != ATTEMPTS:
                    print('get_dialogs fucked up!. Error: "' + str(e) + '". Next attempt...')
                    sleep(2)
                else:
                    print('get_dialogs failed', ATTEMPTS, 'times. Fucking up :(')
                    raise e

    def find_dialog_chat(self, username: str) -> object:
        return self.client.invoke(ResolveUsernameRequest(username)).chats[0]

    def get_market_input_peer(self):
        market_chat = self.client.invoke(ResolveUsernameRequest('ChatWarsMarket')).chats[0]
        return InputPeerChannel(market_chat.id, market_chat.access_hash)

    def find_props(self, name):
        # возвращает props по имени
        r = self.client.invoke(ResolveUsernameRequest(name))
        is_user = getattr(r.peer, 'user_id', None)
        return {'id': r.peer.user_id if is_user else r.peer.channel_id}

    def find_props_id(self, name):
        # возвращает id props по имени
        r = self.client.invoke(ResolveUsernameRequest(name))
        return r.peer.user_id

    def find_group_id(self, groupname):
        # возвращает id группы по имени
        dialog_count = 100
        dialogs, entities = self.client.get_dialogs(dialog_count)
        for i, entity in enumerate(entities):
            i += 1  # 1-based index
            # print('{}. {}. id: {}'.format(i, get_display_name(entity), entity.id))
            if get_display_name(entity) == groupname:
                return {'id': entity.id}

    def loop(self):
        # инициализация и получение начальной инфы о герое
        total, messages, _ = self.client.get_message_history(self.chatwars_dialog, limit=100)
        arena_init = False
        hero_init = False
        selfid_init = False
        for m in messages:
            m.origin_id = m.from_id
            if not selfid_init and m.out:
                self.botid = m.from_id
                self.log('botid получен: '+str(self.botid))
                selfid_init = True
            if 'Добро пожаловать на арену!' in m.message and not arena_init:
                self.log('Инфа о последней арене получена')
                self.arena_parser(m)
                arena_init = True
                continue
            if ('Битва семи замков через' in m.message or 'Межсезонье' in m.message) and not hero_init:
                self.log('Инфа о герое получена')
                self.hero_parser(m)
                hero_init = True
                continue
        # зацикливаем и ждем обновления сообщений
        self.client.add_update_handler(self.update_handler)
        def _loop():
            while True:
                try:

                    if time() - self.lt_info > self.get_info_diff:
                        if self.arena_delay and self.arena_delay_day != datetime.now(self.tz).day:
                            self.arena_delay = False
                        self.lt_info = time()
                        curhour = datetime.now(self.tz).hour
                        if 9 <= curhour <= 23:
                            self.get_info_diff = random.randint(420, 900)
                        else:
                            self.get_info_diff = random.randint(600, 900)
                        if self.config['bot_enabled']:
                            self.action_list.append(orders['hero'])

                    if len(self.action_list) > 0:
                        sleep(random.randint(1, 4))
                        self.log('Отправляем ' + self.action_list[0])
                        self._send_to_chatwars(self.action_list.popleft())
                    sleep(1)
                except Exception as err:
                    self.log('Ошибка очереди: {0}'.format(err))
        Thread(target=_loop).run()

    def command_from_admin(self, message):
        text = message.message
        self.log('Получили сообщение от администратора бота: '+text)
        if text == '#help':
            self._send_to_admin('\n'.join([
                '#enable_bot - Включить бота',
                '#disable_bot - Выключить бота',
                '#enable_arena - Включить арену',
                '#disable_arena - Выключить арену',
                '#enable_les - Включить лес',
                '#disable_les - Выключить лес',
                '#enable_coast - Включить побережье',
                '#disable_coast - Выключить побережье',
                '#enable_peshera - Включить пещеры',
                '#disable_peshera - Выключить пещеры',
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
                "#lvl_atk - качать атаку",
                "#lvl_def - качать защиту",
                "#lvl_off - ничего не качать",
                '#status - Получить статус',
                '#hero - Получить информацию о герое',
                '#push_order - Добавить приказ ({0})'.format(', '.join(orders)),
                #'#order - Дебаг, последняя команда защиты/атаки замка',
                '#log - Дебаг, последние 30 сообщений из лога',
                '#time - Дебаг, текущее время',
                '#lt_arena - Дебаг, последняя битва на арене',
                '#get_info_diff - Дебаг, последняя разница между запросами информации о герое',
                '#ping - Дебаг, проверить жив ли бот',
                '#enable_build - Включить постройки',
                '#disable_build - Выключить постройки'
                '#build_target - указать цель постройки ({0})'.format(', '.join(builds)),
                '#stock - Обновить стоки',
                '#info - немного оперативной информации'
            ]))

        # Вкл/выкл бота
        elif text == '#enable_bot':
            self.config['bot_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Бот успешно включен')
            self.log('Бот успешно включен')
        elif text == '#disable_bot':
            self.config['bot_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Бот успешно выключен')
            self.log('Бот успешно выключен')

        # Вкл/выкл арены
        elif text == '#enable_arena':
            self.config['arena_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Арена успешно включена')
            self.log('Арена успешно включена')
        elif text == '#disable_arena':
            self.config['arena_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Арена успешно выключена')
            self.log('Арена успешно выключена')

        # Вкл/выкл леса
        elif text == '#enable_les':
            self.config['les_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Лес успешно включен')
            self.log('Лес успешно включен')
        elif text == '#disable_les':
            self.config['les_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Лес успешно выключен')
            self.log('Лес успешно выключен')

        # Вкл/выкл побережья
        elif text == '#enable_coast':
            self.config['coast_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Побережье успешно включено')
            self.log('Побережье успешно включено')
        elif text == '#disable_coast':
            self.config['coast_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Побережье успешно выключено')
            self.log('Побережье успешно выключено')

        # Вкл/выкл пещеры
        elif text == '#enable_peshera':
            self.config['peshera_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Пещеры успешно включены')
            self.log('Пещеры успешно включены')
        elif text == '#disable_peshera':
            self.config['peshera_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Пещеры успешно выключены')
            self.log('Пещеры успешно выключены')

        # Вкл/выкл корован
        elif text == '#enable_corovan':
            self.config['corovan_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Отлов корованов успешно включен')
            self.log('Отлов корованов успешно включен')
        elif text == '#disable_corovan':
            self.config['corovan_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Отлов корованов успешно выключен')
            self.log('Отлов корованов успешно выключен')

        # Вкл/выкл Автодеф
        elif text == '#enable_auto_def':
            self.config['auto_def_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Автодеф успешно включен')
            self.log('Автодеф успешно включен')
        elif text == '#disable_auto_def':
            self.config['auto_def_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Автодеф успешно выключен')
            self.log('Автодеф успешно выключен')

        # Вкл/выкл Автодонат
        elif text == '#enable_autodonate':
            self.config['autodonate_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Автодонат успешно включен')
            self.log('Автодонат успешно включен')
        elif text == '#disable_autodonate':
            self.config['autodonate_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Автодонат успешно выключен')
            self.log('Автодонат успешно выключен')

        # Вкл/выкл команд
        elif text == '#enable_order':
            self.config['order_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Приказы успешно включены')
            self.log('Приказы успешно включены')
        elif text == '#disable_order':
            self.config['order_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Приказы успешно выключены')
            self.log('Приказы успешно выключены')

        # Вкл/выкл постройки
        elif text == '#enable_build':
            self.config['build_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Постройки успешно включены')
            self.log('Постройки успешно включены')
        elif text == '#disable_build':
            self.config['build_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Постройки успешно выключены')
            self.log('Постройки успешно выключены')

        # Вкл/выкл лесных боев
        elif text == '#enable_quest_fight':
            self.config['quest_fight_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Битва включена')
            self.log('Битва включена')
        elif text == '#disable_quest_fight':
            self.config['quest_fight_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Битва выключена')
            self.log('Битва выключена')

        # Вкл/выкл питомца
        elif text == '#enable_pet':
            self.config['pet_enabled'] = True
            save_config(self.config)
            self._send_to_admin('Контроль за питомцем успешно включен')
            self.log('Контроль за питомцем успешно включен')
        elif text == '#disable_pet':
            self.config['pet_enabled'] = False
            save_config(self.config)
            self._send_to_admin('Контроль за питомцем успешно выключен')
            self.log('Контроль за питомцем успешно выключен')

        # что качать при левелапе
        elif text == '#lvl_atk':
            self.config['lvl_up'] = 'lvl_atk'
            save_config(self.config)
            self._send_to_admin('Качаем атаку')
            self.log('Качаем атаку')
        elif text == '#lvl_def':
            self.config['lvl_up'] = 'lvl_def'
            save_config(self.config)
            self._send_to_admin('Качаем защиту')
            self.log('Качаем защиту')
        elif text == '#lvl_off':
            self.config['lvl_up'] = 'lvl_off'
            save_config(self.config)
            self._send_to_admin('Ничего не качаем')
            self.log('Ничего не качаем')

        # Информация о герое
        elif text == '#hero':
            if self.hero_message is None:
                self._send_to_admin('Информация о герое пока еще недоступна')
            else:
                self._forward_msg(self.hero_message, self.admin_dialog)

        # Получить лог
        elif text == '#log':
            self._send_to_admin('\n'.join(self.log_list))
            self.log_list.clear()
            self.log('Лог запрошен и очищен')

        # Получить статус
        elif text == "#status":
            self._send_to_admin('\n'.join([
                '🤖Бот включен: {0}',
                '📯Арена включена: {1}',
                '🔎Сейчас на арене: {2}',
                '🌲Лес включен: {3}',
                '🏝Побережье включено: {4}',
                '🕸Пещеры включены: {5}',
                '🐫Корованы включены: {6}',
                '🇪🇺Приказы включены: {7}',
                '🛡Авто деф включен: {8}',
                '💰Донат включен: {9}',
                '😁Питомец включен: {10}',
                '🌟Левелап: {11}',
                '🏘Постройка включена: {12}',
                '🚧Цель постройки: {13}',
                '⚔️Бои в квестах включены: {14}',
            ]).format(self.config['bot_enabled'], self.config['arena_enabled'], self.arena_running,
                      self.config['les_enabled'], self.config['coast_enabled'], self.config['peshera_enabled'],
                      self.config['corovan_enabled'], self.config['order_enabled'], self.config['auto_def_enabled'],
                      self.config['donate_enabled'], self.config['pet_enabled'], self.config['lvl_up'],
                      self.config['build_enabled'], self.config['build_target'], self.config['quest_fight_enabled']))

        # отправка info
        elif text == '#info':
            infotext = '🕯' if self.class_available else ''
            infotext += '{0}{1}|💰{2}|🔋{3}/{4}'.format(self.castle, self.level, self.gold, self.endurance, self.endurancetop)
            if self.arenafight.group(2) != '0':
                infotext += '|📯{0}/{1}|🎖{2}'.format(self.arenafight.group(1), self.arenafight.group(2), self.victory)
            self._send_to_admin(infotext)

        elif text == '#detail':
            if self.hero_message is None:
                self._send_to_admin('Информация о герое пока еще недоступна')
            else:
                heroText = self.hero_message.message
                template = '{0}{1} {2}, 🏅{3}, ⚔️{4} 🛡{5}\n🔥{6}/{7} 🔋{8}/{9} 💰{10}\n🎽{11}'
                heroName = re.search('.{2}(.*), (\w+) \w+ замка', heroText).group(1)
                heroClass = re.search('.{2}(.*), (\w+) \w+ замка', heroText).group(2)
                heroAtk = re.search('⚔Атака: (\d+) 🛡Защита: (\d+)', heroText).group(1)
                heroDef = re.search('⚔Атака: (\d+) 🛡Защита: (\d+)', heroText).group(2)
                heroExpNow = re.search('🔥Опыт: (\d+)/(\d+)', heroText).group(1)
                heroExpNext = re.search('🔥Опыт: (\d+)/(\d+)', heroText).group(2)
                heroEquip = re.sub('\+', '', re.search('🎽Экипировка (.+)', heroText).group(1))
                # heroState = re.search('Состояние:\n(.+)', heroText).group(1)
                self._send_to_admin(template.format(self.castle, heroClass, heroName, self.level, heroAtk, heroDef, heroExpNow, heroExpNext, self.endurance, self.endurancetop, self.gold, heroEquip))

        elif text == '#ping':
            self.log('pinging...')
            self._send_to_admin('#pong')

        elif text == '#lt_arena':
            self._send_to_admin(str(self.lt_arena))

        elif text == '#time':
            text_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._send_to_admin(text_date)

        elif text.startswith('#push_order'):
            command = text.split(' ')[1]
            if command in orders:
                self.update_order(orders[command])
                self._send_to_admin('Команда ' + command + ' применена')
            else:
                self._send_to_admin('Команда ' + command + ' не распознана')

        elif text.startswith('#build_target'):
            command = text.split(' ')[1]
            if command in builds:
                self.config['build_target'] = builds[command]
                self._send_to_admin('Постройка ' + builds[command] + ' установлена')
                save_config(self.config)
            else:
                self._send_to_admin('Постройка ' + command + ' не распознана')

        elif text.startswith('#add'):
            if self.level >= 15:
                self.res_id_list = text.split(' ')[1].split(',')
                self.trade_add()
            else:
                self._send_to_admin('Я еще не дорос, у меня только ' + str(self.level) + ' уровень')

        elif text == '#done':
            self._send_to_dialog('/done', self.tradebot_dialog)
            self._send_to_admin('Предложение готово!')

        # отправка стока
        elif text == '#stock':
            self.twinkstock_enabled = True
            self._send_to_dialog('/start', self.tradebot_dialog)

        if self.config['bot_enabled'] and self.config['order_enabled']:
            if text.find(orders['red']) != -1:
                self.update_order(orders['red'])
            elif text.find(orders['black']) != -1:
                self.update_order(orders['black'])
            elif text.find(orders['white']) != -1:
                self.update_order(orders['white'])
            elif text.find(orders['yellow']) != -1:
                self.update_order(orders['yellow'])
            elif text.find(orders['blue']) != -1:
                self.update_order(orders['blue'])
            elif text.find(orders['mint']) != -1:
                self.update_order(orders['mint'])
            elif text.find(orders['twilight']) != -1:
                self.update_order(orders['twilight'])
            elif text.find('🌲') != -1:
                self.update_order(orders['lesnoi_fort'])
            elif text.find('⚓') != -1:
                self.update_order(orders['sea_fort'])
            elif text.find('⛰') != -1:
                self.update_order(orders['gorni_fort'])
            elif text.find('🛡') != -1:
                self.update_order(self.castle)
                # elif self.config['quest_fight_enabled'] and text.find('/fight') != -1:
                #    c = re.search('(\/fight.*)', text).group(1)
                #    self.action_list.append(c)

    def arena_parser(self, message):
        text = message.message
        self.victory = re.search('Количество побед: ([0-9]+)', text).group(1)
        self.arenafight = re.search('Поединков сегодня ([0-9]+) из ([0-9]+)', text)
        self.log('Поединков: {0} / {1}. Побед: {2}'.format(self.arenafight.group(1), self.arenafight.group(2),
                                                           self.victory))

    def hero_parser(self, message):
        self.hero_message = message
        text = message.message
        if self.castle_name is None:
            self.castle_name = flags[re.search('(.{2}).*, .+ замка', text).group(1)]
            self.log('Замок: ' + str(self.castle_name))
            self.castle = orders[self.castle_name]
            self.bot_name = re.search('.{2}(.*), .+ замка', text).group(1)
        self.endurance = int(re.search('Выносливость: ([0-9]+)', text).group(1))
        self.endurancetop = int(re.search('Выносливость: ([0-9]+)/([0-9]+)', text).group(2))
        self.gold = int(re.search('💰(-?[0-9]+)', text).group(1))
        if re.search('Помощник:', text) is not None:
            # жевотне обнаружено
            self.pet_state = pet_states[re.search('Помощник:\n(.*) (.+) /pet', text).group(2)]
        self.state = re.search('Состояние:\n(.*)', text).group(1)
        self.level = int(re.search('🏅Уровень: ([0-9]+)', text).group(1))
        m = re.search('Битва семи замков через (?:(?:(\d+)ч)? ?(?:(\d+) минут)?|несколько секунд)', text)
        # считаем время до боя
        if not m:
            if re.search('Межсезонье', text):
                self.time_to_war = 60
            else:
                return
        elif not m.group(1) and m.group(2):
            self.time_to_war = int(m.group(2))
        elif m.group(1) and not m.group(2):
            self.time_to_war = 60*int(m.group(1))
        else:
            self.time_to_war = int(m.group(1)) * 60 + int(m.group(2))
        self.log(
            'Золото: {0}, выносливость: {1} / {2}, Пет: {3}, состояние: {4}, уровень: {5}, до боя {6} минут'.format(
                self.gold, self.endurance, self.endurancetop, self.petstatus, self.state, self.level,
                self.time_to_war))
        # принудительное выключение фич, которые ограничены по уровню
        if self.level < 5:
            self.config['arena_enabled'] = False
        if self.level < 15:
            self.config['coast_enabled'] = False
        if self.level < 8:
            self.config['peshera_enabled'] = False

    def parse_from_chatwars(self, message):
        self.log('Получили сообщение от бота. Проверяем условия')
        text = message.message

        if text.find('🌟Поздравляем! Новый уровень!') != -1 and self.config['lvl_up'] != 'lvl_off':
            self.log('получили уровень - {0}'.format(orders[self.config['lvl_up']]))
            self.action_list.append('/level_up')
            self.action_list.append(orders[self.config['lvl_up']])

        elif "На выходе из замка охрана никого не пропускает" in text:
            self.action_list.clear()
            self.config['bot_enabled'] = False
            self._forward_msg(message, self.captcha_dialog)

        # elif 'Не умничай!' in text or 'Ты долго думал, аж вспотел от напряжения' in text:
        #   self._send_to_admin("Командир, у нас проблемы с капчой! #captcha " + '|'.join(captcha_answers.keys()))
        #    bot_enabled = False
        #    if last_captcha_id != 0:
        #        fwd('@', admin_username, message_id)
        #    else:
        #        send_msg('@', admin_username, 'Капча не найдена?')

        elif 'На сегодня ты уже своё отвоевал. Приходи завтра.' in text:
            self.arena_delay = True
            self.arena_delay_day = datetime.now(self.tz).day
            self.log("Отдыхаем денек от арены")
            self.arena_running = False

        elif 'Ты вернулся со стройки:' in text:
            self.log("Получен репорт со стройки")
            if self.castle_name == 'red':
                self._forward_msg(message, self.redstat_dialog)
                self._forward_msg(message, self.redstat2_dialog)
            if self.castle_name == 'blue':
                self._forward_msg(message, self.blueyster_dialog)

        elif 'Здание отремонтировано' in text:
            self.log("Получен репорт с ремонта")
            if self.castle_name == 'red':
                self._forward_msg(message, self.redstat_dialog)
                self._forward_msg(message, self.redstat2_dialog)
            if self.castle_name == 'blue':
                self._forward_msg(message, self.blueyster_dialog)

        elif 'Твои результаты в бою:' in text:
            self.log("Получен репорт с последнего боя")
            if self.castle_name == 'red':
                self._forward_msg(message, self.redstat_dialog)

        elif 'Закупка начинается. Отслеживание заказа:' in text:
            buytrade = re.search('обойдется примерно в (\d+)💰', text).group(1)
            self.gold -= int(buytrade)
            self.log('Купили что-то на бирже на {0} золота'.format(buytrade))

        elif 'Ты пошел строить:' in text:
            self.action_list.clear()
            self.log("Ушли строить")
            self.lt_info = time()
            self.get_info_diff = random.randint(400, 500)

        elif 'Ты отправился искать приключения в пещеру' in text:
            self.action_list.clear()
            self.log("Ушли в пещеру")
            self.lt_info = time()
            self.get_info_diff = random.randint(400, 500)
            self.endurance -= 2

        elif 'Ты отправился искать приключения в лес' in text:
            self.action_list.clear()
            self.log("Ушли в лес")
            self.lt_info = time()
            self.get_info_diff = random.randint(400, 500)
            self.endurance -= 1

        elif 'Ты отправился искать приключения на  побережье' in text:
            self.action_list.clear()
            self.log("Ушли на  побережье")
            self.lt_info = time()
            self.get_info_diff = random.randint(400, 500)
            self.endurance -= 1

        if text.find('Твой замок не контролирует побережье') != -1 and self.config['coast_enabled']:
            self.log('Замок не контролирует побережье. Перенаправляю на лес')
            self.config['coast_enabled'] = False
            self.config['les_enabled'] = True

        elif 'Ищем соперника. Пока соперник не найден' in text:
            self.action_list.clear()
            self.lt_info = time()
            self.get_info_diff = random.randint(900, 1200)
            self.gold -= 5

        elif 'доволен.' in text:
            self.log('Поиграли с питомцем')
            self.last_pet_play = round(time())

        elif text.find('Запас еды:') != -1:
            play_state = pet_char_states[re.search('⚽ (.+)', text).group(1)]
            food_state = pet_char_states[re.search('🍼 (.+)', text).group(1)]
            wash_state = pet_char_states[re.search('🛁 (.+)', text).group(1)]
            food_rest = int(re.search('Запас еды: (\d+)', text).group(1))
            self.log('⚽️{0} 🍼{1} 🛁{2} Запас еды {3}'.format(play_state, food_state, wash_state, food_rest))
            if food_rest <= 2:
                self._send_to_admin('Питомцу скоро будет нечего жрать!')
            if play_state <= 4 and round(time()) - self.last_pet_play >= 3600:
                self.action_list.append(orders['pet_play'])
            if food_state <= 3 and food_rest != 0:
                self.action_list.append(orders['pet_feed'])
            if wash_state <= 4:
                self.action_list.append(orders['pet_wash'])
            Timer(random.randint(8, 12), self.action_list.append, '⬅️Назад').start()

        elif 'Добро пожаловать на арену!' in text:
            self.arena_parser(message)
            if 'Даже драконы не могут драться так часто' in text:
                self.arena_delay = True
                self.arena_delay_day = datetime.now(self.tz).day
                self.log("Отдыхаем денек от арены")
                self.arena_running = False
                self.action_list.append('⬅️Назад')
            if self.config['arena_enabled'] and not self.arena_delay and self.gold >= 5 and not self.arena_running:
                self.log('Включаем флаг - арена запущена')
                #if arena_change_enabled:
                #    action_list.append('/on_{0}'.format(arena_item_id))
                self.arena_running = True
                self.action_list.append('🔎Поиск соперника')
                self.log('Топаем на арену')

        elif 'В казне недостаточно' in text:
            self.log("Стройка не удалась, в замке нет денег")

        elif 'Ты приготовился к защите' in text:
            self.action_list.clear()

        elif self.config['corovan_enabled'] and text.find(' /go') != -1:
            self.action_list.append(orders['corovan'])

        elif self.config['arena_enabled'] and text.find('выбери точку атаки и точку защиты') != -1:
            self.arena_running = True  # на случай, если арена запущена руками
            self.lt_arena = time()
            self.lt_info = time()
            self.get_info_diff = random.randint(400, 500)
            attack_chosen = arena_attack[random.randint(0, 2)]
            cover_chosen = arena_cover[random.randint(0, 2)]
            self.log('Атака: {0}, Защита: {1}'.format(attack_chosen, cover_chosen))
            def _next():
                if random.randint(0, 1):
                    self.action_list.append(attack_chosen)
                    self.action_list.append(cover_chosen)
                else:
                    self.action_list.append(cover_chosen)
                    self.action_list.append(attack_chosen)
            Timer(random.randint(2, 6), _next).start()

        elif text.find('Победил воин') != -1 or text.find('Ничья') != -1:
            self.lt_info = time()
            self.get_info_diff = random.randint(60, 120)
            self.log('Выключаем флаг - арена закончилась')
            self.arena_running = False

        elif self.config['quest_fight_enabled'] and text.find('/fight') != -1:
            c = re.search('(/fight.*)', text).group(1)
            self.action_list.append(c)
            self._forward_msg(message, self.admin_dialog)

        elif 'Битва семи замков через' in text or 'Межсезонье' in text:
            self.hero_parser(message)
            if self.time_to_war <= 29:
                self.report = True
                if self.state == '📯На арене':
                    self.action_list.append(orders['castle_menu'])
                    self.action_list.append(orders['arena'])
                    self.action_list.append(orders['arena_stop'])
                if self.config['auto_def_enabled'] and time() - self.current_order[
                    'time'] > 1800 and 'Отдых' in self.state:
                    if self.castle_name == 'red':
                        self._forward_msg(message, self.redstat_dialog)
                    self.update_order(self.castle)
                    if self.config['donate_enabled']:
                        if self.gold > 0:
                            self.log('Донат {0} золота в казну замка'.format(self.gold))
                            self.action_list.append('/donate {0}'.format(self.gold))
                            self.gold -= self.gold
                return
            else:
                self.log('Времени достаточно')
            if self.report:
                def _next():
                    self.action_list.append('/report')
                    self.log('Запросили репорт по битве')
                    self.report = False
                Timer(random.randint(3, 6), _next).start()

            if text.find('🛌Отдых') == -1 and text.find('🛡Защита ') == -1:
                self.log('Чем-то занят, ждём')
            else:
                # Подумаем, а надо ли так часто ходить куда нибудь )
                if re.search('Помощник:',
                             text) is not None and self.pet_state == 'good' or self.pet_state == 'med' or self.pet_state == 'bad':
                    self.log('Идем проверить питомца')
                    self.action_list.append('/pet')
                    return
                if not self.config['build_enabled']:
                    self.log('на стройку нам не нужно')
                    curhour = datetime.now(self.tz).hour
                    if not self.config['arena_enabled'] or self.arena_delay or curhour > 23 or curhour < 8:
                        self.log('на арену тоже не нужно')
                        if int(self.endurancetop) - int(self.endurance) >= 4:
                            # минут за 35-45 до битвы имеет смысл выйти из спячки
                            sleeping = self.time_to_war * 60 - 60 * random.randint(35, 45)
                            self.log('выносливости мало, можно и подремать до боя {0} минут'.format(int(sleeping / 60)))
                            self.lt_info = time()
                            self.get_info_diff = sleeping
                            return
                    elif self.gold < 5 and self.endurance == 0 and self.time_to_war > 60:
                        sleeping = 60 * random.randint(30, 40)
                        self.log('выносливости нет, денег нет, можно и подремать в ожидании стамины {0} минут'.format(
                            int(sleeping / 60)))
                        self.lt_info = time()
                        self.get_info_diff = sleeping
                        return

                if text.find('🛌Отдых') != -1 and self.arena_running:
                    self.arena_running = False
                if self.config['peshera_enabled'] and self.endurance >= 2:
                    if self.config['les_enabled']:
                        self.action_list.append(orders['quests'])
                        self.action_list.append(random.choice([orders['peshera'], orders['les']]))
                    else:
                        self.action_list.append(orders['quests'])
                        self.action_list.append(orders['peshera'])

                elif self.config['les_enabled'] and not self.config['peshera_enabled'] and self.endurance >= 1 and \
                                orders['les'] not in self.action_list:
                    self.action_list.append(orders['quests'])
                    self.action_list.append(orders['les'])

                elif self.config['coast_enabled'] and not self.config['peshera_enabled'] and self.endurance >= 1 and \
                                orders['coast'] not in self.action_list:
                    self.action_list.append(orders['quests'])
                    self.action_list.append(orders['coast'])

                elif self.config['arena_enabled'] and not self.arena_delay and \
                                self.gold >= 5 and not self.arena_running:
                    curhour = datetime.now(self.tz).hour
                    if 9 <= curhour <= 23:
                        self.action_list.append(orders['castle_menu'])
                        self.action_list.append(orders['arena'])
                    else:
                        self.log('По часам не проходим на арену. Сейчас ' + str(curhour) + ' часов')
                        if self.config['build_enabled']:
                            self.log('Пойдем строить')
                            self.action_list.append(self.config['build_target'])

                elif self.config['build_enabled']:
                    self.log('Пойдем строить')
                    self.action_list.append(self.config['build_target'])

    def parsed_text(self, message):
        text = message.message
        origin_id = message.origin_id
        if origin_id == self.ADMIN_ID:
            self.command_from_admin(message)

        elif self.config['bot_enabled'] and origin_id == self.CHATWARS_ID:
            self.parse_from_chatwars(message)

        elif self.twinkstock_enabled and origin_id == self.TRADEBOT_ID:
            if text.find('Твой склад с материалами') != -1:
                self._forward_msg(message, self.stockbot_dialog)
                self.twinkstock_enabled = False
                self._send_to_admin('Сток обновлен')

    def trade_add(self):
        if not self.tradeadd:
            self._send_to_dialog('/start',self.tradebot_dialog)
            self.tradeadd = True
        if self.tradeadd and len(self.res_id_list) != 0:
            total, messages, _ = self.client.get_message_history(self.tradebot_dialog, limit=1)
            for m in messages:
                text = m.message
                self.log('добавляем ресурсы по списку..')
                # тк запросы на /add стартуют не строго по завершению предыдущего, а почти сразу, просто поставить
                # каждый на 1-2 сек таймаута неправильно - через 1-2 секунды они стартанут всей кучей. поэтому
                # каждый следующий ставим на таймаут+(1-2 сек), т.е на 1-2 сек дольше, чем все предыдущие таймауты
                # вместе взятые
                timeout = 0
                for res_id in self.res_id_list:
                    if re.search('/add_' + res_id + ' ', text):
                        def _next():
                            count = re.search('/add_' + res_id + '\D+(.*)', text).group(1)
                            self._send_to_dialog('/add_' + res_id + ' ' + str(count), self.tradebot_dialog)
                            self.log('Добавили ' + str(count) + ' шт. ресурса ' + res_id)
                            self._send_to_admin('Добавлено ' + str(count) + ' шт. ресурса ' + res_id)
                        timeout += random.randint(2, 5)
                        Timer(timeout, _next).start()
                    else:
                        self.log('На складе нет ресурса ' + res_id)
                        self._send_to_admin('На складе нет ресурса ' + res_id)
        self._send_to_dialog('/done', self.tradebot_dialog)
        self.log('Предложение готово')
        self.tradeadd = False
        Timer(2, self._send_last_trade_offer).start()


    def log(self, message):
        textlog = '{0:%Y-%m-%d+ %H:%M:%S}'.format(datetime.now()) + ' ' + message
        print(textlog)
        self.log_list.append(textlog)

    def update_order(self, order):
        self.current_order['order'] = order
        self.current_order['time'] = time()
        if order == self.castle_name:
            self.action_list.append(orders['cover'])
        else:
            self.action_list.append(orders['attack'])
        self.action_list.append(order)

    def _send_to_chatwars(self, text):
        # print('Sending to chatwars: "%s"' % text)
        Timer(random.randint(2, 5), self.client.send_message, (self.chatwars_dialog, text)).start()


    def _send_to_admin(self, text):
        # print('Sending to admin: "%s"' % text)
        self.client.send_message(self.admin_dialog, text)

    def _send_to_dialog(self, text, dialog):
        # print('Sending to admin: "%s"' % text)
        Timer(random.randint(1, 2), self.client.send_message, (dialog, text)).start()

    def _forward_msg(self, msg, dialog):
        if not dialog:
            print('Skipped forwarding msg because dialog not found')
            return
        fwd_id = telethon.helpers.generate_random_long()
        peer = telethon.utils.get_input_peer(dialog)
        msg_id = getattr(msg, 'id', None)
        if msg_id:
            # print('Forwarding', msg_id, 'to', peer, msg)
            Timer(random.randint(1, 2), self.client.invoke, ForwardMessageRequest(peer, msg_id, fwd_id)).start()
            return True
        else:
            print('Cannot forward message: msg id unavailable: ', msg)
            print('Destination dialog: ', dialog)
            return False

    def update_handler(self, tgupdate):
        self.last_message_received = datetime.now()
        if hasattr(tgupdate, 'updates'):
            updates = tgupdate.updates
        elif hasattr(tgupdate, 'update'):
            updates = [tgupdate.update]
        elif isinstance(tgupdate, telethon.tl.types.update_short_message.UpdateShortMessage):
            updates = [tgupdate]
        elif isinstance(tgupdate, telethon.tl.types.update_short_chat_message.UpdateShortChatMessage):
            updates = [tgupdate]
        else:
            # print('Skipped TGUpdate of class %s: ' % tgupdate.__class__.__name__, tgupdate, dir(tgupdate))
            return
        for upd in updates:
            if any(isinstance(upd, cls) for cls in TOTALLY_IGNORED_MESSAGE_TYPES):
                # 100% ignored to not shit into console
                continue
            if isinstance(upd, telethon.tl.types.update_new_message.UpdateNewMessage):
                message = getattr(upd, 'message', None)
                origin_id = getattr(message, 'from_id', None)
            elif isinstance(upd, telethon.tl.types.update_short_message.UpdateShortMessage):
                message = upd
                origin_id = getattr(message, 'user_id', None)
            elif isinstance(upd, telethon.tl.types.update_edit_message.UpdateEditMessage):
                message = getattr(upd, 'message', None)
                origin_id = getattr(message, 'from_id', None)
            elif isinstance(upd, telethon.tl.types.update_short_chat_message.UpdateShortChatMessage):
                message = upd
                origin_id = getattr(message, 'from_id', None)  # Also field 'chat_id' is present
            elif isinstance(upd, telethon.tl.types.update_new_channel_message.UpdateNewChannelMessage):
                message = getattr(upd, 'message', None)
                origin_id = getattr(getattr(message, 'to_id'), 'channel_id')
                if message is not None and getattr(message, 'message', None) is not None and message.message.find(self.bot_name) != -1 \
                        and origin_id == 1112398751 \
                        and getattr(message, 'via_bot_id') == 278525885:
                    self.log('Трейд')
                    if message.reply_markup is None:
                        self.log('Нет разметки кнопок')
                    else:
                        answer = self.client(GetBotCallbackAnswerRequest(
                            self.market_dialog,
                            message.id,
                            data=message.reply_markup.rows[0].buttons[0].data
                        ))
                        if answer.message == 'Обмен произведен!':
                            self.log('Приняли трейд')
                        else:
                            self.log('Ответ на нажатие - ' + str(answer))
            elif isinstance(upd, telethon.tl.types.update_edit_channel_message.UpdateEditChannelMessage):
                message = getattr(upd, 'message', None)
                origin_id = getattr(getattr(message, 'to_id'), 'channel_id')
            elif isinstance(upd, UpdateChannelPinnedMessage):
                print('Handling UpdateChannelPinnedMessage: ', upd)
                self._handle_update_pinned_message(upd)
                continue

            else:
                # print('Skipped update class:', upd.__class__.__name__, upd)
                continue
            if not message:
                # print('Skipped update without "message" field')
                continue
            if all(origin_id != prop['id'] for prop in self.ALL_PROPS) and origin_id != self.botid:
                # print('Skipped message not from chatwars bot: ', message)
                continue
            # print('New message: ', message, dir(message))
            # print('Text: ', message.message)
            # print('Buttons: ', get_buttons(message))
            message.origin_id = origin_id
            # with self.message_queue_lock:
            #    self.message_queue.append(message)
            self.parsed_text(message)

    def _handle_update_pinned_message(self, upd):
        pass

    def _send_last_trade_offer(self):
        query_results = self.client(GetInlineBotResultsRequest(
            self.tradebot_dialog,
            InputPeerSelf(),
            '',
            ''
        ))
        self.client(SendInlineBotResultRequest(
            self.admin_dialog,
            query_results.query_id,
            query_results.results[0].id
        ))
        self.log('Предложение отправлено')


def save_config(CONFIG):
    with open(config_path, 'w+') as outfile:
        json.dump(CONFIG, outfile, indent=2)


def read_config():
    with open(config_path) as f:
        return json.load(f)


def main():
    global config_path
    global phone
    while True:
        if not reg_number:
            print('Connecting to telegram...')
            client = telethon.TelegramClient(phone, api_id, api_hash)
            client.connect()
            if not client.is_user_authorized():
                print('Not authorized')
                authorize(client, phone)
        else:
            print('Регистрируем номер...')
            reg_service = 'sms-reg'
            r = Reg(reg_service)
            balance = r.get_balance()

            if balance < 2:
                raise Exception('Нет денег на балансе. Осталось {0} р.'.format(balance))

            tzid = r.get_tzid()

            phone = r.wait_num(tzid)

            client = telethon.TelegramClient(phone, api_id, api_hash)
            client.connect()
            if not client.is_user_authorized():
                print('Not authorized')
                r.set_ready(tzid)
                code = r.wait_code(tzid)
                first_name = ''
                last_name = ''
                username = ''
                if reg_generate_name:
                    first_name = names.get_first_name()
                    last_name = names.get_last_name()
                    username = first_name+last_name
                else:
                    first_name = input('Введи имя (не может быть пустым): ')
                    last_name = input('Введи фамилию (может быть пустой): ')
                    username = input('Введи корректный юзернейм или оставь пустым: ')
                print('{0} {1}, @{2}'.format(first_name, last_name, username) if bool(username) else '{0} {1}, без юзернейма'.format(first_name, last_name))
                client.sign_up(phone, code, first_name, last_name)
                r.set_ok(tzid)
                username_available = client.invoke(CheckUsernameRequest(username))
                if not username_available:
                    print('Юзернейм неверен или недоступен:(')
                else:
                    set_username_result = client.invoke(UpdateUsernameRequest(username))
                    if isinstance(set_username_result, User):
                        print('Юзернейм удачно установлен')
                    else:
                        print('Что-то пошло не так: ', str(set_username_result))

        try:
            print('Connected to telegram')
            config_path = fullpath + '/bot_cfg/' + phone + '.json'
            try:
                open(config_path)
            except FileNotFoundError:
                print('Конфиг не найден')
                save_config(config)
                print('Новый конфиг создан')
            except Exception as e:
                print(str(e))
            a = ChatWarsAutomator(client, read_config())
            a.loop()
        except Exception as e:
            print('Exception during chatwars automation process: ', e)
            traceback.print_exc()
            print('Disconnecting...')
            client.disconnect()
            sleep(5)


if __name__ == '__main__':
    main()
