import requests
import time


def request_data(method, url_mod):
    url = "http://localhost:5001/water/"

    try:
        r = requests.request(method, url + url_mod, verify=True)
        return r

    except Exception as E:
        print(E)


def time_loop():

    while True:
        request_data("POST", "/5/234/09192982")
        time.sleep(5)


time_loop()
