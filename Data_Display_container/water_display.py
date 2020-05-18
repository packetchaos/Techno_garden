import requests
import time
import io
from flask import Flask, Response, render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

app = Flask(__name__)


def request_data(method, url_mod):
    url = "http://water.hyrule.local:5004"
    try:
        r = requests.request(method, url + url_mod,  headers={'Content-type': 'application/json'}, verify=True)
        return r.json()
    except Exception as E:
        print(E)


@app.route('/')
@app.route('/stats')
def main_route():
    # Get all of the data - Will refine to users request once Json is formated properly
    # Need to handle an Error if the site is down TypeError
    total_data = request_data("GET", "/water")

    # For now get the information today
    today = time.strftime("%B%d", time.localtime(time.time()))

    # List to hold parsed data for graphing
    value_list = []
    total_list = []
    # need to find the lowest value for our starting point
    for i in total_data:
        # Grab the month and day for comparison - 120 for jan 20th
        date = time.strftime("%B%d", time.localtime(float(i["time"])))

        r_date = time.strftime("%B %d %H:%M:%S", time.localtime(float(i["time"])))

        if date == today:
            value_list.append(i['rotation_count'])
            temp_list = []
            temp_list.append(i["rotation_count"])
            temp_list.append(i['sensor_id'])
            temp_list.append(str(r_date))
            total_list.append(temp_list)


    try:
        start_value = min(value_list)
        end_value = max(value_list)
    except:
        start_value = 0
        end_value = 0

    # Grab the total and convert into Gallons.
    total = ((end_value - start_value)/100)/4
    return render_template("data.html", total=total, total_list=total_list)


@app.route('/today.png')
def display_data():
    data = request_data("GET", "/water")
    pulse_list = []
    date_list = []
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
                #print(update['sensor_id'], update['rotation_count'], round(liters, 2), newtime)

    fig = Figure(figsize=(16,9))
    axis = fig.add_subplot(1,1,1)
    axis.plot(date_list, pulse_list, color='tab:green')
    axis.set_title("Water Usage by Minute")
    output = io.BytesIO()

    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
