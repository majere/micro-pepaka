import configparser
import ssl
import time
import json
import psycopg2
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
    def start_handler(response):
        print('------------------------------------')
        message = json.loads(response)
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


class DB:
    def check_tables():
        db_cursor = connection.cursor()
        db_cursor.execute('CREATE TABLE IF NOT EXISTS admins (id SERIAL NOT NULL, "user_id" bigint NOT NULL, "role" varchar NOT NULL);')
        connection.commit()
        print(config['default']['owner_id'])
        db_cursor.execute('SELECT role FROM admins WHERE user_id = %s AND role = %s;', (int(config['default']['owner_id']), 'owner'))
        answer = db_cursor.fetchall()
        print(answer)

        if answer:
            print('answer true')
        else:
            print('answer false')
            db_cursor.execute('INSERT INTO admins ("user_id", role) VALUES (%s, %s);', (config['default']['owner_id'], 'owner'))
            connection.commit()


class PepakaCore:
    def core(message):
        print('core')
        print(message)


    def service(message):
        print('service')
        print(message)


# create connection to DB
connection = psycopg2.connect(dbname=config['default']['db_name'], user=config['default']['db_user'], password=config['default']['db_password'], host=config['default']['db_ip'])
DB.check_tables()
# start web-server
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(config['default']['ssl_fullchain'], config['default']['ssl_privkey'])
webhook = Webhook()
web.run_app(webhook.app, host=config['default']['webhook_listen'], port=config['default']['webhook_port'], ssl_context=ssl_context)
