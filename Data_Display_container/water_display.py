import requests
import time
import io
from flask import Flask, Response, render_template, request
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

app = Flask(__name__)

'''
Set the compare_value to null to auto set to today's date if 
no query params are in the URL
'''
compare_date = ''


def request_data(method, url_mod):
    # Change to URL of your environment
    url = "http://water.hyrule.local"
    try:
        r = requests.request(method, url + url_mod,  headers={'Content-type': 'application/json'}, verify=True)
        return r.json()
    except Exception as E:
        print(E)


@app.route('/')
@app.route('/stats')
def main_route():
    total_data = request_data("GET", "/water")

    # grab today's date to use if no date is provided
    today = time.strftime("%B%d", time.localtime(time.time()))

    # grab the Month and Day from URL Params
    month = request.args.get('month')
    day = request.args.get('day')

    global compare_date
    compare_date = str(month) + str(day)

    # If there is no Query params compare_Date with be NoneNone
    if compare_date == 'NoneNone':
        compare_date = today

    # List to hold parsed data for graphing
    value_list = []
    total_list = []

    # Need to find the lowest value for our starting point
    # This will be used in case the program isn't reset every day
    # Water.py should be reset daily so the rotations don't grow to a massive number.
    for i in total_data:
        # Grab the month and day for comparison - jan20 for jan 20th
        date = time.strftime("%B%d", time.localtime(float(i["time"])))

        # date to Display
        r_date = time.strftime("%B %d %H:%M:%S", time.localtime(float(i["time"])))

        # Only grab calculations for a single day; use compare_date
        if date == compare_date:
            value_list.append(i['rotation_count'])
            temp_list = [i["rotation_count"], i['sensor_id'], str(r_date)]
            total_list.append(temp_list)

    try:
        # Grab min and max values to calculate the total used
        start_value = min(value_list)
        end_value = max(value_list)
    except ValueError:
        # If the water didn't run, set the values to zero to avoid an error.
        start_value = 0
        end_value = 0

    # Grab the total and convert into Gallons.
    total = ((end_value - start_value)/100)/4

    return render_template("data.html", total=total, total_list=total_list, compare_date=compare_date)


@app.route('/today.png')
def display_data():
    # grab raw data from Water_capture container
    data = request_data("GET", "/water")

    pulse_list = []
    date_list = []
    lowest_value = []
    today = time.strftime("%B%d", time.localtime(time.time()))
    # only Graph water usage for a single day; use compare_date.
    global compare_date
    if compare_date == 'NoneNone':
        compare_date = today

    # need to find the lowest value for our starting point
    # This is to avoid incorrect calculations when water.py is run for more than one day.
    for i in data:
        date = time.strftime("%B%d", time.localtime(float(i["time"])))

        if date == compare_date:
            # grab all of the rotations to find the lowest value as a starting point.
            lowest_value.append(i['rotation_count'])
    try:
        # Set the lowest value to the last value for our calculations and graphing
        last_value = min(lowest_value)
    except ValueError:
        # set the value to zero to display a blank graph; better than an Error
        last_value = 0

    # Now go through the list again to compare values for Gallons per 60 seconds
    for update in data:
        # make time readable
        newtime = time.strftime("%H:%M", time.localtime(float(update["time"])))

        # Grab the MonthDay string for capturing a single day of data
        date = time.strftime("%B%d", time.localtime(float(update["time"])))

        # single_out a sensor
        # Eventually set this dynamically
        if update['sensor_id'] == 13:

            # Grab only a single day using compare_Date(URL params)
            if date == compare_date:
                # 455 pulses per liter - source: http://pnrsolution.org/Datacenter/Vol4/Issue3/16.pdf
                # rate is rotations between reporting times. current - last value
                gallons = ((int(update['rotation_count']) - last_value)/100)/4
                pulse_list.append(gallons)
                date_list.append(newtime)

                # set the last value to the current value for rate calculation
                last_value = int(update["rotation_count"])

    # Set the figure size
    fig = Figure(figsize=(16, 9))
    axis = fig.add_subplot(1, 1, 1)

    # use the date and pulse count to graph the data
    axis.plot(date_list, pulse_list, color='tab:green')

    # Set the Title of the Graph
    axis.set_title("Water Usage by Minute")

    output = io.BytesIO()

    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype="image/png")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
