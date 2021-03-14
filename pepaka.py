import configparser
import ssl
import time
import json
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

except LookupError:
    print('config.ini error')
    exit()


class Webhook:
    async def start(self):
        response = await self.text()
        th = Thread(target=Handler.start_handler, args=(response, ))
        th.start()
        return web.Response()
    app = web.Application()
    app.add_routes([web.post('/', start), web.post('/{name}', start)])


class Handler:
    def start_handler(response):
        print('------------------------------------')
        message = json.loads(response)
        print(message)


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(config['default']['ssl_fullchain'], config['default']['ssl_privkey'])
webhook = Webhook()
web.run_app(webhook.app, host=config['default']['webhook_listen'], port=config['default']['webhook_port'], ssl_context=ssl_context)
