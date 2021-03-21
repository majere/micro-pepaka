import configparser
import ssl
import time
import json
import psycopg2
import requests
import random
import string
from aiohttp import web
from threading import Thread

print('It`s me, Pepaka III')

config = configparser.ConfigParser()

try:
    config.read('config.ini')
    print(config['default']['bot_api_token'])
    print(config['default']['ssl_fullchain'])
    print(config['default']['ssl_privkey'])
    print(config['default']['webhook_listen'])
    print(config['default']['webhook_port'])
    print(config['default']['db_ip'])
    print(config['default']['db_name'])
    print(config['default']['db_user'])
    print(config['default']['db_password'])
    print(config['default']['owner_id'])

except LookupError:
    print('config.ini error')
    exit()


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


class DB:
    def check_tables():
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS admins (id SERIAL NOT NULL, "user_id" bigint NOT NULL, "role" varchar NOT NULL, "token" varchar NOT NULL);')
        connection.commit()
        cursor.execute('SELECT role FROM admins WHERE user_id = %s AND role = %s;', (int(config['default']['owner_id']), 'owner'))
        answer = cursor.fetchall()
        if answer:
            print('answer true')
        else:
            print('answer false')
            cursor.execute('INSERT INTO admins ("user_id", role, token) VALUES (%s, %s, %s);', (config['default']['owner_id'], 'owner', RandomGenerator.genString(64)))
            connection.commit()

    def check_user(user_id):
        cursor = connection.cursor()
        cursor.execute('SELECT role FROM admins WHERE user_id = %s;', (user_id,))
        answer = cursor.fetchall()
        print(answer)
        if answer and answer[0][0] == 'owner':
            print('it`s owner')
            return 'owner'
        elif answer and answer[0][0] == 'admin':
            print('it`s admin')
            return 'admin'
        else:
            print('it`s noname')
            return None

    def add_admin(user_id):
        cursor = connection.cursor()
        cursor.execute('INSERT INTO admins ("user_id", role, token) VALUES (%s, %s, %s);', (user_id, 'admin', RandomGenerator.genString(64)))
        connection.commit()

    def delete_admin(user_id):
        cursor = connection.cursor()
        cursor.execute('DELETE FROM admins WHERE "user_id" = %s;', (user_id,))
        connection.commit()


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
    def sendChatAction(chat_id, action):
        url = t_url + '/sendChatAction'
        data = {'chat_id': chat_id, 'action': action}
        r = requests.post(url, data=data)
        print('send chat action status:', r)
        time.sleep(random.random())

    def sendMessage(chat_id, text):
        url = t_url + '/sendMessage'
        data = {'chat_id': chat_id, 'parse_mode': 'HTML', 'text': text}
        r = requests.post(url, data=data)
        print('send message status:', r)

    def sendReply(chat_id, message_id, text):
        url = t_url + '/sendMessage'
        data = {'chat_id': chat_id, 'parse_mode': 'HTML', 'reply_to_message_id': message_id, 'text': text}
        r = requests.post(url, data=data)
        print('send reply status:', r)

    def deleteMessage(chat_id, message_id):
        url = t_url + '/deleteMessage'
        data = {'chat_id': chat_id, 'message_id': message_id}
        r = requests.post(url, data=data)
        print('delete message status:', r)


class PepakaCore:
    def core(message):
        print('core')
        m = Message(message)
        if m.command == '!адм':
            Admins.add_admin(m)
        if m.command == '!дел':
            Admins.delete_admin(m)

    def service(message):
        print('service')
        print(message)


class Admins:
    def add_admin(m):
        if DB.check_user(m.user_id) == 'owner':
            if m.reply_user_id:
                if DB.check_user(m.reply_user_id):
                    Methods.sendReply(m.chat_id, m.message_id, 'Ужо есть такой')
                else:
                    DB.add_admin(m.reply_user_id)
                    Methods.deleteMessage(m.chat_id, m.message_id)
                    text = m.user_fullname + ' теперь почётный одмин'
                    Methods.sendMessage(m.chat_id, text)
            else:
                Methods.sendReply(m.chat_id, m.message_id, 'И на кого ты рукой показываешь?')
        else:
            Methods.deleteMessage(m.chat_id, m.message_id)
            text = m.user_fullname + ' раскидывается регалиями почем зря'
            Methods.sendMessage(m.chat_id, text)

    def delete_admin(m):
        if DB.check_user(m.user_id) == 'owner':
            if m.reply_user_id:
                DB.delete_admin(m.reply_user_id)

t_url = config['default']['t_url'] + config['default']['bot_api_token']
# create connection to DB
connection = psycopg2.connect(dbname=config['default']['db_name'], user=config['default']['db_user'], password=config['default']['db_password'], host=config['default']['db_ip'])
DB.check_tables()
# start web-server
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(config['default']['ssl_fullchain'], config['default']['ssl_privkey'])
webhook = Webhook()
web.run_app(webhook.app, host=config['default']['webhook_listen'], port=config['default']['webhook_port'], ssl_context=ssl_context)
