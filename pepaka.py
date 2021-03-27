import configparser
import ssl
import time
import json
import requests
import random
import string
from aiohttp import web
from threading import Thread
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime
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
    sticker = None
    reply_id = None
    reply_user_id = None
    reply_user_fullname = None
    reply_text = None
    file_id = None
    file_path = None

    def __init__(self, data):
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
            self.file_id = data['photo'][0]['file_id']
            print('file_id =', self.file_id)
        if data.get('sticker'):
            self.sticker = data['sticker']
            print(self.sticker)
        if data.get('reply_to_message'):
            self.reply_id = data['reply_to_message']['message_id']
            print('reply_id =', self.reply_id)
            self.reply_user_id = data['reply_to_message']['from']['id']
            print('reply_user_id =', self.reply_user_id)
            try:
                self.reply_user_fullname = data['reply_to_message']['from']['first_name'] + ' ' + data['reply_to_message']['from']['last_name']
            except KeyError:
                self.reply_user_fullname = data['reply_to_message']['from']['first_name']


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

    def getFile(self, id):
        url = self.url + '/getFile'
        data = {'file_id': id}
        r = requests.post(url, data=data)
        print('getFile = ', r.text)
        return r


class PepakaCore:
    def core(message):
        print('core')
        m = Message(message)
        is_command = True
        if m.command:
            if m.command == '!адм' and is_command:
                is_command = False
            if m.command == '!del':
                db.del_user(m, cfg)
            if m.command.startswith('!add'):
                db.add_user(m, cfg)
            if m.command.startswith('!мем') and m.file_id:
                mem = Meme()
                mem.check_meme(m)



    def service(message):
        print('service')
        print(message)


class Meme:
    def __init__(self):
        pass

    def check_meme(self, m):
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
                print('REPLACED')
            else:
                print('NORIGHTS')
        else:
            mtd.sendChatAction(m.chat_id, 'typing')
            text = 'Неправильная комнада. !мем !суперкоманда'
            mtd.sendMessage(m.chat_id, text)


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

    def check_user_role(self, m):
        s = self.session()
        q = s.query(Admins).filter(Admins.user_id == m.user_id)
        if q.count() == 1:
            for elem in q:
                return elem.role
        elif q.count() > 1:
            print('Слишком много записей с таким user_id')
            return False
        else:
            print('Такого user_id нет в бд')
            return False

    def check_owner(self, conf):
        self.base.metadata.create_all(self.engine)
        print('START CHECK OWNER')
        s = self.session()
        q = s.query(Admins).filter(Admins.user_id == conf.owner_id)
        if q.count() == 1:
            print('owner ok')
        elif q.count() > 1:
            print('too many owners')
        else:
            print('No owner. Create owner')
            t = Admins(user_id=conf.owner_id, role='owner', token=RandomGenerator.genString(64))
            s.add(t)
            s.commit()

    def add_user(self, m, conf):
        print('START ADD USER TO ADMINS')
        if conf.owner_id == m.user_id and m.reply_user_id:
            mtd = Methods()
            s = self.session()
            q = s.query(Admins).filter(Admins.user_id == m.reply_user_id)
            if q.count() == 0:
                t = Admins(user_id=m.reply_user_id, role='admin', token=RandomGenerator.genString(64))
                s.add(t)
                s.commit()
                mtd.sendChatAction(m.chat_id, 'typing')
                text = F'<b>{m.reply_user_fullname}</b> принят в Котячий дворец'
                mtd.sendMessage(m.chat_id, text)
            else:
                mtd.sendChatAction(m.chat_id, 'typing')
                text = F'<b>{m.reply_user_fullname}</b> уже во дворце'
                mtd.sendMessage(m.chat_id, text)
        else:
            print('no rights to add admin')

    def del_user(self, m, conf):
        print('START DELETE USER')
        mtd = Methods()
        if m.reply_user_fullname:
            if conf.owner_id == m.user_id and m.reply_user_id and m.reply_user_id != conf.owner_id:
                s = self.session()
                s.query(Admins).filter(Admins.user_id == m.reply_user_id).delete()
                s.commit()
                text = F'<b>{m.user_fullname}</b> с позором выгнал из котячей крепости <b>{m.reply_user_fullname}</b>'
                mtd.sendChatAction(m.chat_id, 'typing')
                mtd.sendMessage(m.chat_id, text)
            else:
                text = F'У <b>{m.user_fullname}</b> нет прав для удаления <b>{m.reply_user_fullname}</b>'
                mtd.sendChatAction(m.chat_id, 'typing')
                mtd.sendMessage(m.chat_id, text)
        else:
            text = 'Пустота вечна. Её нельзя удалить'
            mtd.sendChatAction(m.chat_id, 'typing')
            mtd.sendMessage(m.chat_id, text)

    def add_meme(self, m):
        s = self.session()
        query = s.query(Memes).filter(Memes.chat_id == m.chat_id, Memes.command == m.command)
        if query.count() == 0:
            t = Memes(owner=m.user_id, chat_id=m.chat_id, command=m.command, file=m.file_path)
            s.add(t)
            s.commit()
            return 'created'
        else:
            if query[0].owner == m.user_id:
                print('replace meme')
                query.delete()
                t = Memes(owner=m.user_id, chat_id=m.chat_id, command=m.command, file=m.file_path)
                s.add(t)
                s.commit()
                return 'replaced'
            else:
                print('No rights to replace meme')
                return 'norights'



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
    chat_id = Column('chat_id', Integer)
    command = Column('command', String)
    file = Column('file', String)


db.check_owner(cfg)
# start web-server
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(cfg.ssl_fullchain, cfg.ssl_privkey)
webhook = Webhook()
web.run_app(webhook.app, host=cfg.webhook_listen, port=cfg.webhook_port, ssl_context=ssl_context)
