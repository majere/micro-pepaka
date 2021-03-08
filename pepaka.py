import configparser

print('It`s me, Pepaka III')

config = configparser.ConfigParser()

try:
    config.read('config.ini')
    print(config['default']['bot_api_token'])

except LookupError:
    print('config.ini error')


