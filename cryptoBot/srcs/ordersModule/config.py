import configparser
import os

class config: 
    config = configparser.ConfigParser()
    config.read('cryptoBot/srcs/ordersModule/config.ini')
    API_KEY = config.get('KEYS', 'api_key')
    API_SECRET = config.get('KEYS', 'secret_key')
    API_URL=config.get('URLS', 'api_url')
    possible_orders = ["BUY", "SELL"]
    possible_symbols = ["BTC", "ETH", "BETH", "USDT"]