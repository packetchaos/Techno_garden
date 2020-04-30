import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from Data_capture_container.database import new_db_connection


def request_data(method, url_mod):
    url = "http://localhost:5004"
    try:
        r = requests.request(method, url + url_mod,  headers={'Content-type': 'application/json'}, verify=True)
        return r.json()
    except Exception as E:
        print(E)


def get_data():
    data = request_data("GET", "/water")
    pulse_list = []
    date_list = []
    water_dict = {}
    last_value = 0

    for update in data:
        #print(update['sensor_id'], update["rotation_count"], update['time'])
        newtime = time.strftime("%b %c %H:%M:%S", time.localtime(float(update["time"])))
        if update['sensor_id'] != 5:
            if float(update["rotation_count"]) <= (time.time() - (10*60*60)):
                # 455 pulses per liter - source: http://pnrsolution.org/Datacenter/Vol4/Issue3/16.pdf
                liters = (int(update['rotation_count']) - last_value)/455
                pulse_list.append(liters)
                date_list.append(newtime)
                last_value = int(update["rotation_count"])
                print(update['sensor_id'], update['rotation_count'], round(liters, 2), newtime)

    water_dict['liters'] = pulse_list
    water_dict['date'] = date_list

    series = pd.DataFrame(water_dict, columns=['liters', 'date'])
    series.plot(y='liters', x='date', kind='bar')
    plt.show()


def delete_row():
    database = r"water_raw.db"
    water_conn = new_db_connection(database)
    water_conn.execute('pragma journal_mode=wal;')

    with water_conn:
        cur = water_conn.cursor()
        cur.execute("delete from water where sensor_id='5';")
        #cur.execute(("select sensor_id from water;"))


#time_loop()
get_data()
#delete_row()
