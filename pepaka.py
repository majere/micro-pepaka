import configparser
import ssl
from aiohttp import web

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
    async def start(request):

        response = await request.text()
        print('------------------------------------')
        print(response)
        return web.Response()

    app = web.Application()
    app.add_routes([web.post('/', start), web.post('/{name}', start)])


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(config['default']['ssl_fullchain'], config['default']['ssl_privkey'])
webhook = Webhook()
web.run_app(webhook.app, host=config['default']['webhook_listen'], port=config['default']['webhook_port'], ssl_context=ssl_context)
