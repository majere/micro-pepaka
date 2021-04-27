import configparser
import datetime
import ssl
import time
import json
import requests
import random
import string
import re
from aiohttp import web
from threading import Thread
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL


class Config:
    t_url = None
    bot_api_token = None
    ssl_fullchain = None
    ssl_privkey = None
    webhook_listen = None
    webhook_port = None
    db_ip = None
    db_port = None
    db_name = None
    db_user = None
    db_password = None
    owner_id = None
    url = None

    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read('config.ini')
        self.t_url = conf['default']['t_url']
        self.bot_api_token = conf['default']['bot_api_token']
        self.ssl_fullchain = conf['default']['ssl_fullchain']
        self.ssl_privkey = conf['default']['ssl_privkey']
        self.webhook_listen = conf['default']['webhook_listen']
        self.webhook_port = conf['default']['webhook_port']
        self.db_ip = conf['default']['db_ip']
        self.db_port = conf['default']['db_port']
        self.db_name = conf['default']['db_name']
        self.db_user = conf['default']['db_user']
        self.db_password = conf['default']['db_password']
        self.owner_id = int(conf['default']['owner_id'])


cfg = Config()


class Webhook:
    async def start(self):
        response = await self.text()
        th = Thread(target=Handler.start_handler, args=(response,))
        th.start()
        return web.Response()

    app = web.Application()
    app.add_routes([web.post('/', start), web.post('/{name}', start)])


class Handler:
    def start_handler(self):
        print('------------------------------------')
        message = json.loads(self)
        if message.get('message'):
            message = message['message']
            PepakaCore.core(message)
        elif message.get('edited_message'):
            message = message['edited_message']
            PepakaCore.core(message)
        elif message.get('pepaka'):
            PepakaCore.service(message)
        else:
            print('Wrong data')
            print(message)


class RandomGenerator:
    def genString(length):
        password_characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(password_characters) for i in range(length))
        return password


class Message:
    message_id = None
    user_id = None
    user_firstname = None
    user_lastname = None
    user_fullname = None
    chat_id = None
    text = None
    caption = None
    command = None
    sticker_set_name = None
    sticker_id = None
    reply_id = None
    reply_user_id = None
    reply_user_fullname = None
    reply_text = None
    file_id = None
    file_path = None
    bot_owner = None

    def __init__(self, data):
        self.bot_owner = cfg.owner_id
        print(data)
        self.message_id = data['message_id']
        print('message_id =', self.message_id)
        self.user_id = data['from']['id']
        print('user_id =', self.user_id)
        self.chat_id = data['chat']['id']
        print('chat_id =', self.chat_id)
        self.user_firstname = data['from']['first_name']
        print('first_name =', self.user_firstname)
        try:
            self.user_fullname = self.user_firstname + ' ' + data['from']['last_name']
        except KeyError:
            self.user_fullname = self.user_firstname
        if data.get('text'):
            self.text = data['text']
            self.command = self.text.lower()
            print('text =', self.text)
        if data.get('caption'):
            self.caption = data['caption']
            self.command = self.caption.lower()
            print('caption =', self.caption)
        if data.get('photo'):
            count = len(data['photo'])
            self.file_id = data['photo'][count - 1]['file_id']
            print('file_id =', self.file_id)
        if data.get('sticker'):
            self.sticker_set_name = data['sticker']['set_name']
            self.sticker_id = data['sticker']['file_id']
            print(self.sticker_set_name)
        if data.get('reply_to_message'):
            self.reply_id = data['reply_to_message']['message_id']
            print('reply_id =', self.reply_id)
            self.reply_user_id = data['reply_to_message']['from']['id']
            print('reply_user_id =', self.reply_user_id)
            try:
                self.reply_user_fullname = data['reply_to_message']['from']['first_name'] + ' ' + data['reply_to_message']['from']['last_name']
            except KeyError:
                self.reply_user_fullname = data['reply_to_message']['from']['first_name']
        if data.get('animation'):
            self.file_id = data['animation']['file_id']
            print('file_id =', self.file_id)
        if data.get('video'):
            self.file_id = data['video']['file_id']


class Methods:
    url = None

    def __init__(self):
        self.url = cfg.t_url + '/bot' + cfg.bot_api_token
        print(self.url)

    def sendChatAction(self, chat_id, action):
        url = self.url + '/sendChatAction'
        data = {'chat_id': chat_id, 'action': action}
        r = requests.post(url, data=data)
        print('send chat action status:', r)
        time.sleep(random.random())

    def sendMessage(self, chat_id, text):
        url = self.url + '/sendMessage'
        data = {'chat_id': chat_id, 'parse_mode': 'HTML', 'text': text}
        r = requests.post(url, data=data)
        print('send message status:', r)
        print(r.text)

    def sendReply(self, chat_id, message_id, text):
        url = self.url + '/sendMessage'
        data = {'chat_id': chat_id, 'parse_mode': 'HTML', 'reply_to_message_id': message_id, 'text': text}
        r = requests.post(url, data=data)
        print('send reply status:', r)

    def deleteMessage(self, chat_id, message_id):
        url = self.url + '/deleteMessage'
        data = {'chat_id': chat_id, 'message_id': message_id}
        r = requests.post(url, data=data)
        print('delete message status:', r)

    def getFile(self, file_id):
        url = self.url + '/getFile'
        data = {'file_id': file_id}
        r = requests.post(url, data=data)
        print('getFile = ', r.text)
        return r

    def sendPhoto(self, chat_id, photo):
        url = self.url + '/sendPhoto'
        data = {'chat_id': chat_id}
        files = {'photo': photo}
        r = requests.post(url, data=data, files=files)
        print('sendPhoto =', r.text)

    def getStickerSet(self, set_name):
        url = self.url + '/getStickerSet'
        data = {'name': set_name}
        r = requests.post(url, data=data)
        return r

    def sendSticker(self, chat_id, sticker):
        url = self.url + '/sendSticker'
        data = {'chat_id': chat_id, 'sticker': sticker}
        r = requests.post(url, data=data)
        print(r.text)

    def sendAnimation(self, chat_id, animation):
        url = self.url + '/sendAnimation'
        data = {'chat_id': chat_id}
        files = {'animation': animation}
        r = requests.post(url, data=data, files=files)
        print(r.text)

    def sendVideo(self, chat_id, video):
        url = self.url + '/sendVideo'
        data = {'chat_id': chat_id}
        files = {'video': video}
        r = requests.post(url, data=data, files=files)
        print(r.text)


class Actions:
    dict_actions = {}
    # is_command = False
    action = None

    def __init__(self, m):
        self.dict_actions = {'!del': db.del_user,
                             '!add': db.add_user,
                             '!мем': Meme().save_meme,
                             '!дата': InfinitySummer,
                             '!мну': Mnu}
        self.action = m.command.split(' ')
        self.action = self.action[0]

    def check_general_actions(self, m):
        if self.action in self.dict_actions:
            self.dict_actions[self.action](m)
            return True
        else:
            return False

    def check_db_actions(self, m):
        if db.get_meme(m):
            mem = Meme()
            mem.send_meme(m)
            return True
        else:
            print('meme not found')
            return False


class PepakaCore:
    def core(message):
        print('core')
        m = Message(message)
        if m.command:
            a = Actions(m)
            if m.command[0] == '!':
                if not a.check_general_actions(m):
                    if m.command.startswith('!d'):
                        Dice(m)
                    else:
                        a.check_db_actions(m)
            else:
                db.write_msg(m)
        if m.sticker_set_name:
            s = Sticker(m)
            s.check_sticker()
        if m.command and m.command.startswith('пепяк') and 'или' in m.command:
            ToBeOrNoToBe(m)
        if m.command and 'утр' in m.command and 'котан' in m.command:
            GoodMorning(m)


    def service(message):
        print('service')
        print(message)


class GoodMorning:
    def __init__(self, m):
        print('Good Morning')
        if random.randint(0, 1) == 0:
            mtd = Methods()
            mtd.sendChatAction(m.chat_id, 'typing')
            mtd.sendMessage(m.chat_id, 'Мырк')



class Dice:
    def __init__(self, m):
        mtd = Methods()
        try:
            num = int(m.command[2:])
            if num > 0:
                mtd.deleteMessage(m.chat_id, int(m.message_id))
                rnd = random.randint(1, num)
                print('random number is ' + str(rnd))
                mtd.sendChatAction(m.chat_id, 'typing')
                mtd.sendMessage(m.chat_id, '<b>' + m.user_fullname + '</b> выбросил <b>' + str(rnd) + ' из ' + m.command[2:] + '</b>.')

                if rnd == 1:
                    mtd.sendChatAction(m.chat_id, 'typing')
                    mtd.sendMessage(m.chat_id, 'Ха-ха! Етить ты маубедитель!')

            else:
                mtd.sendChatAction(m.chat_id, 'typing')
                mtd.sendMessage(m.chat_id, 'Кажется я проглотил твой кубик, <b>' + m.user_fullname + '</b>.')

        except:
            mtd.sendChatAction(m.chat_id, 'typing')
            mtd.sendMessage(m.chat_id, '<b>' + m.user_fullname + '</b> зашвырнул кубик за грань реальности.')


class Meme:
    @staticmethod
    def save_meme(m):
        c = m.command.split(' ')
        mtd = Methods()
        if len(c) == 2 and c[1].startswith('!'):
            print('mem ok')
            m.command = c[1]
            f = Files()
            f.download(m)
            result = db.add_meme(m)
            if result == 'created':
                mtd.sendChatAction(m.chat_id, 'typing')
                mtd.sendMessage(m.chat_id, F'Схоронил мемасик {m.command}')
            elif result == 'replaced':
                mtd.sendChatAction(m.chat_id, 'typing')
                mtd.sendMessage(m.chat_id, F'Заменил мемасик {m.command}')
            else:
                mtd.sendChatAction(m.chat_id, 'typing')
                mtd.sendMessage(m.chat_id, F'Нет прав на мемасик {m.command}')
        else:
            mtd.sendChatAction(m.chat_id, 'typing')
            text = 'Неправильная комнада. !мем !имямема'
            mtd.sendMessage(m.chat_id, text)

    @staticmethod
    def send_meme(m):
        print(m.file_path)
        file = open(m.file_path, 'rb')
        mtd = Methods()
        if m.file_path.startswith('photo'):
            mtd.sendPhoto(m.chat_id, file)
        elif m.file_path.startswith('animation'):
            mtd.sendAnimation(m.chat_id, file)
        elif m.file_path.startswith('video'):
            mtd.sendVideo(m.chat_id, file)


class Files:
    file_id = None
    url = None

    def __init__(self):
        self.url = cfg.t_url + '/file/bot' + cfg.bot_api_token

    def download(self, m):
        mtd = Methods()
        data = mtd.getFile(m.file_id)
        jdata = json.loads(data.text)
        if jdata['ok']:
            print('DOWNLOAD')
            print(jdata)
            m.file_path = jdata['result']['file_path']
            url_file = self.url + '/' + jdata['result']['file_path']
            file = jdata['result']['file_path']
            f = open(file, "wb")
            r = requests.get(url_file)
            f.write(r.content)
            f.close()
        else:
            text = 'getFile failed'
            mtd.sendMessage(m.chat_id, text)


class InfinitySummer:
    def __init__(self, m):
        print('Summer never end')
        mtd = Methods()
        # curr_date = datetime.date(2020, 9, 22) # for tests
        curr_date = datetime.date.today()
        curr_month = curr_date.month
        if curr_month < 6:
            last_summer_day = datetime.date(curr_date.year - 1, 8, 31)
        else:
            last_summer_day = datetime.date(curr_date.year, 8, 31)

        if curr_month == 6 or curr_month == 7 or curr_month == 8:
            if curr_month == 6:
                month = ' июня '
            if curr_month == 7:
                month = ' июля '
            if curr_month == 8:
                month = ' августа '
            text = 'Сегодня ' + str(curr_date.day) + month + str(curr_date.year) + ' года'
            mtd.sendMessage(m.chat_id, text)
        else:
            true_date = (curr_date - last_summer_day).days + 31
            text = 'Сегодня ' + str(true_date) + ' августа ' + str(curr_date.year) + ' года'
            mtd.sendMessage(m.chat_id, text)


class DB:
    db_connect = None
    base = None
    session = None
    engine = None

    def __init__(self, conf):
        self.db_connect = {
            'drivername': 'postgresql',
            'host': conf.db_ip,
            'port': conf.db_port,
            'username': conf.db_user,
            'password': conf.db_password,
            'database': conf.db_name
        }
        self.base = declarative_base()
        self.engine = create_engine(URL(**self.db_connect))
        self.session = sessionmaker()
        self.session.configure(bind=self.engine)

    def create_tables(self):
        self.base.metadata.create_all(self.engine)

    def add_user(self, m):
        print('Start add user')
        mtd = Methods()
        if m.user_id == m.bot_owner:
            if m.reply_user_id:
                s = self.session()
                q = s.query(Admins).filter(Admins.user_id == m.reply_user_id)
                if q.count() == 0:
                    t = Admins(user_id=m.reply_user_id, role='admin', token=RandomGenerator.genString(64))
                    s.add(t)
                    s.commit()
                    mtd.sendChatAction(m.chat_id, 'typing')
                    text = F'<b>{m.reply_user_fullname}</b>, я тебя запомнил '
                    mtd.sendMessage(m.chat_id, text)
                else:
                    mtd.sendChatAction(m.chat_id, 'typing')
                    text = F'<b>{m.user_fullname}</b>, ты повторяешься'
                    mtd.sendMessage(m.chat_id, text)
            else:
                mtd.sendChatAction(m.chat_id, 'typing')
                text = F'Глупый <b>{m.user_fullname}</b> пытается всё заполнить пустотой'
                mtd.sendMessage(m.chat_id, text)
        else:
            mtd.sendChatAction(m.chat_id, 'typing')
            text = f'<b>{m.user_fullname}</b>, тебе не позволено'
            mtd.sendMessage(m.chat_id, text)

    def del_user(self, m):
        print('Start del user')
        mtd = Methods()
        if m.user_id == m.bot_owner:
            if m.reply_user_id:
                s = self.session()
                s.query(Admins).filter(Admins.user_id == m.reply_user_id).delete()
                s.commit()
                mtd.sendChatAction(m.chat_id, 'typing')
                text = F'<b>{m.user_fullname}</b> зачеркнул <b>{m.reply_user_fullname}</b>'
                mtd.sendMessage(m.chat_id, text)
            else:
                mtd.sendChatAction(m.chat_id, 'typing')
                text = F'Глупый <b>{m.user_fullname}</b> пытается удалить пустоту'
                mtd.sendMessage(m.chat_id, text)
        else:
            mtd.sendChatAction(m.chat_id, 'typing')
            text = f'<b>{m.user_fullname}</b>, тебе не позволено'
            mtd.sendMessage(m.chat_id, text)

    def add_meme(self, m):
        s = self.session()
        q = s.query(Memes).filter(Memes.chat_id == m.chat_id, Memes.command == m.command)
        if q.count() == 0:
            t = Memes(owner=m.user_id, chat_id=m.chat_id, command=m.command, file=m.file_path)
            s.add(t)
            s.commit()
            return 'created'
        else:
            if q[0].owner == m.user_id:
                print('replace meme')
                q.delete()
                t = Memes(owner=m.user_id, chat_id=m.chat_id, command=m.command, file=m.file_path)
                s.add(t)
                s.commit()
                return 'replaced'
            else:
                print('No rights to replace meme')
                return 'norights'

    def get_meme(self, m):
        s = self.session()
        print('GET MEME', m.command)
        q = s.query(Memes).filter(Memes.chat_id == m.chat_id, Memes.command == m.command)
        if q.count() == 1:
            m.file_path = q[0].file
            return True
        else:
            return False

    def write_msg(self, m):
        print('def write_msg')
        s = self.session()
        q = s.query(Messages).filter(Messages.text == m.text).first()
        if q:
            print('exists')
        else:
            print('not exists')
            if not m.text.startswith('!'):
                t = Messages(text=m.text)
                s.add(t)
                s.commit()


class Sticker:
    id = None
    set_name = None
    title = None
    animated = None
    chat_id = None

    def __init__(self, m):
        print('Sticker inside!')
        self.set_name = m.sticker_set_name
        self.id = m.sticker_id

    def check_sticker(self):
        print('Check sticker')
        print(self.set_name)
        bd = DB(cfg)
        s = bd.session()
        q = s.query(Stickers).filter(Stickers.set_name == self.set_name).first()
        if not q:
            mtd = Methods()
            stickers = mtd.getStickerSet(self.set_name)
            stickers = stickers.json()
            self.animated = stickers['result']['is_animated']
            self.title = stickers['result']['title']
            stickers = stickers['result']['stickers']
            for stkr in stickers:
                print(stkr['file_id'])
                t = Stickers(set_name=self.set_name, title=self.title, sticker_id=stkr['file_id'], is_animated=self.animated)
                s.add(t)
            s.commit()
            mtd.sendSticker(-1001437386963, self.id)


class Mnu:
    def __init__(self, m):
        if m.command.startswith('/me'):
            mnu_text = m.command[4:]
        else:
            mnu_text = m.command[5:]
        mtd = Methods()
        mtd.deleteMessage(m.chat_id, m.message_id)
        mtd.sendMessage(m.chat_id, '<b>* ' + str(m.user_fullname) + '</b> ' + mnu_text)


class ToBeOrNoToBe:
    def __init__(self, m):
        def del_trash(text):
            return (re.sub('\W+','', text ))
        word_list = m.text.split()
        answer_list = []
        temp = ''
        for word in word_list:
            if 'пепяк' not in word.lower() and word.lower() != 'или':
                temp += del_trash(word) + ' '
            elif temp != '':
                answer_list.append(temp)
                temp = ''
        answer_list.append(temp)
        answer = random.choice(answer_list)
        mtd = Methods()
        mtd.sendChatAction(m.chat_id, 'typing')
        mtd.sendReply(m.chat_id, m.message_id, answer)


db = DB(cfg)


class Admins(db.base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer)
    role = Column('role', String)
    token = Column('token', String)


class Memes(db.base):
    __tablename__ = 'memes'
    id = Column(Integer, primary_key=True)
    owner = Column('owner', Integer)
    chat_id = Column('chat_id', BigInteger)
    command = Column('command', String)
    file = Column('file', String)
    func = Column('func', String)


class Messages(db.base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column('message', String)


class Stickers(db.base):
    __tablename__ = 'stickers'
    id = Column(Integer, primary_key=True)
    set_name = Column('set_name', String)
    title = Column('title', String)
    sticker_id = Column('sticker_id', String)
    is_animated = Column('is_animated', Boolean)


db.create_tables()
# start web-server
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(cfg.ssl_fullchain, cfg.ssl_privkey)
webhook = Webhook()
web.run_app(webhook.app, host=cfg.webhook_listen, port=cfg.webhook_port, ssl_context=ssl_context)
