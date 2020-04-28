import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from Data_capture_container.database import new_db_connection


def request_data(method, url_mod):
    url = "http://water.hyrule.local:5004"

    try:
        r = requests.request(method, url + url_mod,  headers={'Content-type': 'application/json'}, verify=True)
        return r.json()

    except Exception as E:
        print(E)


def time_loop():

    while True:
        request_data("POST", "/water/5/234/09192982")
        time.sleep(5)


def get_data():
    data = request_data("GET", "/water")
    pulse_list = []
    date_list = []
    water_dict = {}
    for update in data:
        #newtime = datetime.datetime.fromtimestamp(float(update[2])).strftime('%c')
        if float(update[2]) > (time.time() - (12*60*60)):
            liters = int(update[1])/455
            pulse_list.append(liters)
            date_list.append((float(update[2])))

    water_dict['liters'] = pulse_list
    water_dict['date'] = date_list

    print(water_dict)


    series = pd.DataFrame(water_dict, columns=['liters', 'date'])
    #print(series)
    series.plot(y='liters', x='date', kind='line')
    plt.show()

def delete_row():
    database = r"water_raw.db"
    water_conn = new_db_connection(database)
    water_conn.execute('pragma journal_mode=wal;')

    with water_conn:
        cur = water_conn.cursor()
        cur.execute("select * from water;")


time_loop()
#get_data()
#delete_row()
