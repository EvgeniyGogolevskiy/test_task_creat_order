import hashlib
import time
import hmac
import requests
import json
import random

# Пример данных, которые мы получаем от фронтенда
data = {
    "volume": 300.0,  # Объем в долларах
    "number": 3,  # На сколько ордеров нужно разбить этот объем
    "amountDif": 50.0,  # Разброс в долларах, в пределах которого случайным образом выбирается объем в верхнюю и нижнюю сторону
    "side": "SELL",  # Сторона торговли (SELL или BUY)
    "priceMin": 1700.0,  # Нижний диапазон цены, в пределах которого нужно случайным образом выбрать цену
    "priceMax": 1900.0  # Верхний диапазон цены, в пределах которого нужно случайным образом выбрать цену
}

# Торгуемая пара, на которой будем проводить тесты, апи ключи, полученные с тестнета
test_data = {
    "symbol": 'ETHUSDT',
    "api_key": 'r7naGWVGWE09UKanEFymSRh7mjqlxPI7H2a6TLDKM2MUaYjbx81siwdh0iF0IRiY',
    "secret_key": 'pP0Ak9TFKEEMpGUZA0k839u7rwVASD1xoHY3kfczUlHG1HJBEMry4LtkaaYSziyB'
}


# Функция для валидации данных
def validate_data(data):
    required_keys = ["volume", "number", "amountDif", "side", "priceMin", "priceMax"]
    for key in required_keys:
        if key not in data:
            return False
    if data["side"] not in ["BUY", "SELL"]:
        return False
    return True


# Функция для открытия ордера
def create_order(symbol, api_key, secret_key, quantity_usd, price):
    # Получаем цену торгуемой пары, для дальнейшего определения количества знаков после запятой
    ticker_url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    ticker_data = json.loads(requests.get(ticker_url).content)
    usd_rate = float(ticker_data['price'])

    # Определяем количество знаков после запятой
    num_decimals = len(str(usd_rate).split('.')[1])

    # Определяем диапазон допустимого значения lot_size
    url_info = 'https://api.binance.com/api/v3/exchangeInfo'
    response = requests.get(url_info)
    info = response.json()
    filters = next(item["filters"] for item in info["symbols"] if item["symbol"] == symbol)
    lot_size = float(next(filter["stepSize"] for filter in filters if filter["filterType"] == "LOT_SIZE"))

    # Определяем количество знаков после запятой
    num_decimals_lot = len(str(lot_size).split('.')[1])

    # Считаем объём в базовой валюте
    base_asset = quantity_usd / price

    # Определяем параметры для открытия ордера
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": "{:.{}f}".format(base_asset, num_decimals_lot).rstrip('0').rstrip('.'),
        "price": "{:.{}f}".format(price, num_decimals).rstrip('0').rstrip('.'),
        "newOrderRespType": "RESULT",
        "timestamp": int(time.time() * 1000),
        "recvWindow": 60000
    }

    # Создаём строку `query_string` в соответствии с API-методом для открытия лимитного ордера
    qs = "&".join("{}={}".format(k, v) for k, v in params.items())
    # Создаём подпись, используя секретный ключ с помощью хеш-функции SHA-256:
    signature = hmac.new(secret_key.encode("utf-8"), qs.encode("utf-8"), hashlib.sha256).hexdigest()

    # Формируем URL-адрес для API-метода, используя параметры и подпись:
    url = f"https://testnet.binance.vision/api/v3/order?{qs}&signature={signature}"

    # Добавляем свой `api_key` в словарь `headers` в запросе на размещение лимитного ордера
    headers = {"X-MBX-APIKEY": api_key}
    r = requests.post(url, headers=headers)
    if r.status_code != 200:
        raise Exception(json.loads(r.content))


# Функция для создания ордеров на бирже Binance
def main(data, test_data):
    # Вычисляем общий объем на каждый ордер
    order_volume = data['volume'] / data['number']

    # Создаем переменную для вычисления общего объема открытых ордеров
    total_price = 0

    # Создаем number ордеров
    for i in range(data['number']):
        # Выбираем случайную цену в диапазоне от priceMin до priceMax
        price = random.uniform(data['priceMin'], data['priceMax'])

        # Выбираем случайный объем в диапазоне от (order_volume - amountDif) до (order_volume + amountDif)
        amount = random.uniform(order_volume - data['amountDif'], order_volume + data['amountDif'])

        # Вычисляем общий объём открытых ордеров
        total_price += amount * price

        # Создаем ордер на бирже Binance с выбранной ценой и объемом
        create_order(test_data['symbol'], test_data['api_key'], test_data['secret_key'], amount, price)

    if data['side'] == "BUY":
        if total_price > data['volume']:
            raise Exception("Order total exceeds available funds")
    elif data['side'] == "SELL":
        if total_price < data['volume']:
            raise Exception("Order total does not meet required funds")


main(data, test_data)
