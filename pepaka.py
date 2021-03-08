import configparser, ssl

print('It`s me, Pepaka III')

config = configparser.ConfigParser()

try:
    config.read('config.ini')
    print(config['default']['bot_api_token'])
    print(config['default']['ssl_fullchain'])
    print(config['default']['ssl_privkey'])


except LookupError:
    print('config.ini error')
    exit()


def webhook_setup():
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(config['default']['ssl_fullchain'], config['default']['ssl_privkey'])


webhook_setup()
