import requests
import time
import pandas as pd
import io
import matplotlib.pyplot as plt
from Data_capture_container.database import new_db_connection
from flask import Flask, Response, render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure


app = Flask(__name__)


def request_data(method, url_mod):
    #url = "http://0.0.0.0:5004"
    url = "http://water.hyrule.local"
    try:
        r = requests.request(method, url + url_mod,  headers={'Content-type': 'application/json'}, verify=True)
        return r.json()
    except Exception as E:
        print(E)


@app.route('/')
def main_route():
    total_data = request_data("GET", "/water")

    today = time.strftime("%B%d", time.localtime(time.time()))
    value_list = []

    # need to find the lowest value for our starting point
    for i in total_data:
        date = time.strftime("%B%d", time.localtime(float(i["time"])))

        if date == today:
            value_list.append(i['rotation_count'])

    start_value = min(value_list)
    end_value = max(value_list)
    total = ((end_value - start_value)/100)/4

    return render_template("data.html", total=total)


@app.route('/today.png')
def display_data():
    data = request_data("GET", "/water")
    pulse_list = []
    date_list = []
    water_dict = {}
    today = time.strftime("%B%d", time.localtime(time.time()))
    lowest_value = []

    # need to find the lowest value for our starting point
    for i in data:
        date = time.strftime("%B%d", time.localtime(float(i["time"])))

        if date == today:
            lowest_value.append(i['rotation_count'])

    last_value = min(lowest_value)

    # Now go through the list again to compare values for Gallons per 30 seconds
    for update in data:
        # make time readable
        newtime = time.strftime("%H:%M", time.localtime(float(update["time"])))
        date = time.strftime("%B%d", time.localtime(float(update["time"])))

        # single_out a sensor
        if update['sensor_id'] != 5:
            if date == today:
                # 455 pulses per liter - source: http://pnrsolution.org/Datacenter/Vol4/Issue3/16.pdf
                liters = ((int(update['rotation_count']) - last_value)/100)/4
                pulse_list.append(liters)
                date_list.append(newtime)
                last_value = int(update["rotation_count"])
                print(update['sensor_id'], update['rotation_count'], round(liters, 2), newtime)

    water_dict['liters'] = pulse_list
    water_dict['date'] = date_list

    #series = pd.DataFrame(water_dict, columns=['liters', 'date'])
    #series.plot(y='liters', x='date', kind='bar')
    #plt.show()

    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    axis.plot(date_list, pulse_list)
    output  = io.BytesIO()

    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")

def get_data():
    data = request_data("GET", "/water")
    pulse_list = []
    date_list = []
    water_dict = {}
    today = time.strftime("%B%d", time.localtime(time.time()))
    lowest_value = []

    # need to find the lowest value for our starting point
    for i in data:
        date = time.strftime("%B%d", time.localtime(float(i["time"])))

        if date == today:
            lowest_value.append(i['rotation_count'])

    last_value = min(lowest_value)

    # Now go through the list again to compare values for Gallons per 30 seconds
    for update in data:
        # make time readable
        newtime = time.strftime("%B %d %H:%M:%S", time.localtime(float(update["time"])))
        date = time.strftime("%B%d", time.localtime(float(update["time"])))

        # single_out a sensor
        if update['sensor_id'] != 5:
            if date == today:
                # 455 pulses per liter - source: http://pnrsolution.org/Datacenter/Vol4/Issue3/16.pdf
                liters = ((int(update['rotation_count']) - last_value)/100)/4
                pulse_list.append(liters)
                date_list.append(newtime)
                last_value = int(update["rotation_count"])
                print(update['sensor_id'], update['rotation_count'], round(liters, 2), newtime)

    water_dict['liters'] = pulse_list
    water_dict['date'] = date_list

    series = pd.DataFrame(water_dict, columns=['liters', 'date'])
    series.plot(y='liters', x='date', kind='bar')
    plt.show()

def new_get():
    data = request_data("GET", "/water")
    pulse_list = []
    date_list = []
    water_dict = {}
    last_value = 0

    print(data)

def delete_row():
    database = r"water_raw.db"
    water_conn = new_db_connection(database)
    water_conn.execute('pragma journal_mode=wal;')

    with water_conn:
        cur = water_conn.cursor()
        cur.execute("delete from water where sensor_id='5';")
        #cur.execute(("select sensor_id from water;"))


#time_loop()
#get_data()
#delete_row()
#new_get()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
