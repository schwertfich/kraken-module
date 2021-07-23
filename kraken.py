import time
import requests
import urllib.parse
import hashlib
import hmac
import base64
import json
import re


def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def kraken_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)             
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req

def exec(msg, user, predicted_cmd):

    cfg = user.get_module_config("kraken-module")
    command = predicted_cmd.split("-")
    api_key = cfg['api_key']
    api_sec = cfg['api_sec']
    your_currency = cfg['currency']
    currency_symbol = cfg['currency_symbol']
    cryptoticker = cfg['cryptoticker']
    print(cryptoticker)
    regex = r".*[von]\s"
    name = re.sub(regex, "", msg)
    crypto = cryptoticker[f'{name}']

    print(command)
    print(msg)

    status = requests.get('https://api.kraken.com/0/public/SystemStatus').json()
    print(status)

    if status['result']['status'] == "online":
        if command[0] == "user":
             # Construct the request and print the result
            resp = kraken_request('https://api.kraken.com/0/private/TradeBalance',
            {"nonce": str(int(1000*time.time())),
            "asset": your_currency},
            api_key, api_sec).json()
            return {"cod": 200, "msg": f"Deine Kraken Balance ist {float(resp['result']['eb']):.2f}{currency_symbol[your_currency]}"}
        elif command[0] == "market":
            resp = requests.get(f'https://api.kraken.com/0/public/Ticker?pair={crypto}{your_currency}').json()
            print(resp)
            return {"cod": 200, "msg": f"{name} ist zur Zeit {float(resp['result'][f'{crypto}{your_currency}']['o']):.2f}{currency_symbol[your_currency]} wert"}
        else:
            return {"cod": 500, "msg": "Unbekannter Command"}
    else:
        return {"cod": 404, "msg": "Kraken Api is not online", "reason": f"{status['result']}"}