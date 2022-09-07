import logging.config
import yaml
import logging

logging.getLogger('telethon.network.mtprotosender').setLevel('CRITICAL')
logging.getLogger('telethon.extensions.messagepacker').setLevel('CRITICAL')
logging.getLogger('telethon.crypto.libssl').setLevel('CRITICAL')
logging.getLogger('telethon.crypto.aes').setLevel('CRITICAL')
logger = logging.getLogger('__main__')
# log/config.yml - host
# C:\python\bots\BotForRey\log\config.yml - desktop
with open(r'log/config.yml', 'r') as obj:
    logging.config.dictConfig(yaml.safe_load(obj))
