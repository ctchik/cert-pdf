import time
import requests

count = 0
while True:
    count += 1
    data = requests.get('https://chain.api.btc.com/v3/tx/0eab89a271380b09987bcee5258fca91f28df4dadcedf892658b9bc261050d96?verbose=3')
    print(data.content)
    print('count = ' + str(count))
    time.sleep(3)
