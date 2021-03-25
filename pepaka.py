import configparser
import ssl
import time
import json
#import psycopg2
import requests
import random
import string
from aiohttp import web
from threading import Thread
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
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
        self.owner_id = conf['default']['owner_id']


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
    command = None
    sticker = None
    reply_id = None
    reply_user_id = None
    reply_text = None

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
        except:
            self.user_fullname = self.user_firstname
        if data.get('text'):
            self.text = data['text']
            self.command = self.text.lower()
            print('text =', self.text)
            print('command =', self.command)
        if data.get('sticker'):
            self.sticker = data['sticker']
            print(self.sticker)
        if data.get('reply_to_message'):
            self.reply_id = data['reply_to_message']['message_id']
            print('reply_id =', self.reply_id)
            self.reply_user_id = data['reply_to_message']['from']['id']
            print('reply_user_id =', self.reply_user_id)


class Methods:
    url = None

    def __init__(self):
        self.url = cfg.t_url + cfg.bot_api_token

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


class PepakaCore:
    def core(message):
        print('core')
        m = Message(message)
        met = Methods()
        met.sendMessage(m.chat_id, m.text)
        if m.command == '!адм':
            pass
        if m.command == '!дел':
            pass
        if m.command.startswith('!add'):
            pass

        print(db.check_user(m))


    def service(message):
        print('service')
        print(message)



'''
        s = session()
        t = Admins(user_id=0000, role='bugaga', token='qqqqqqqqqqqqqqqqqqqqq')
        s.add(t)
        s.commit()
'''




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
        self.base.metadata.create_all(self.engine)

    def check_user(self, m):
        mtd = Methods()
        s = self.session()
        query = s.query(Admins).filter(Admins.user_id == m.user_id)
        if query.count() == 1:
            for elem in query:
                return elem.role
        elif query.count() > 1:
            mtd.sendMessage(m.chat_id, 'Слишком много записей с таким именем')
        else:
            mtd.sendMessage(m.chat_id, 'Такого пользователя нет в бд')
            return False


db = DB(cfg)


class Admins(db.base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer)
    role = Column('role', String)
    token = Column('token', String)





# start web-server
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(cfg.ssl_fullchain, cfg.ssl_privkey)
webhook = Webhook()
web.run_app(webhook.app, host=cfg.webhook_listen, port=cfg.webhook_port, ssl_context=ssl_context)
