import requests
import time
import random
from Data_capture_container.database import new_db_connection


def request_data(method, url_mod):
    url = "http://water.hyrule.local/water/"

    try:
        r = requests.request(method, url + url_mod, verify=True)
        return r

    except Exception as E:
        print(E)


def time_loop():
    # loop to enter in real data for testing
    old_data = []

    for z in range(0, 100000, 10000):
        old_data.append([13, random.random()*10000, time.time()])
        time.sleep(1)

    for x in old_data:
        request_data("POST", str(x[0]) + "/" + str(x[1]) + "/" + str(x[2]))
        time.sleep(1)


def display():
    import json
    database = r"water_raw.db"
    water_conn = new_db_connection(database)
    water_conn.execute('pragma journal_mode=wal;')
    raw_list = []
    with water_conn:
        cur = water_conn.cursor()
        cur.execute("SELECT * FROM water;")

        rows = cur.fetchall()
        '''for x in rows:
            month = time.strftime("%B", time.localtime(float(x[2])))
            day = time.strftime("%d", time.localtime(float(x[2])))
            print(month + day)
            print(x)'''

        print(json.dumps(rows))


#display()
time_loop()
