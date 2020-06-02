import requests
import time
import io
from flask import Flask, Response, render_template, request
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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
    sensor = request.args.get('sensor')

    # grab today's date to use if no date is provided
    today = time.strftime("%B%d", time.localtime(time.time()))

    # grab the Month and Day from URL Params
    month = request.args.get('month')
    day = request.args.get('day')

    total_data = request_data("GET", "/water?sensor=" + str(sensor) + "&month=" + str(month) + "&day=" + str(day))

    global compare_date
    compare_date = str(month) + str(day)

    # If there is no Query params compare_Date with be NoneNone
    if compare_date == 'NoneNone':
        compare_date = today
        month = time.strftime("%B", time.localtime(time.time()))
        day = time.strftime("%d", time.localtime(time.time()))

    # List to hold parsed data for graphing
    value_list = []
    total_list = []

    # Need to find the lowest value for our starting point
    # This will be used in case the program isn't reset every day
    # Water.py should be reset daily so the rotations don't grow to a massive number.
    for i in total_data[month][day]:
        # Grab the month and day for comparison - jan20 for jan 20th
        date = time.strftime("%B%d", time.localtime(float(i["timestamp"])))

        # date to Display
        r_date = time.strftime("%B %d %H:%M:%S", time.localtime(float(i["timestamp"])))

        # Only grab calculations for a single day; use compare_date
        if date == compare_date:
            value_list.append(i['rotations'])
            temp_list = [i["rotations"], i['sensor'], str(r_date)]
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
    line_name = "Unknown"

    if sensor == '13':
        line_name = "Main Line"
    elif sensor == '15':
        line_name = "Pepper Bed"

    return render_template("data.html", total=total, total_list=total_list, compare_date=compare_date, sensor=sensor, month=month, day=day, line_name=line_name)


@app.route('/<sensor>/<month>/<day>/today.png')
def display_data(sensor, month, day):
    # grab raw data from Water_capture container
    data = request_data("GET", "/water?sensor=" + sensor + "&month=" + str(month) + "&day=" + str(day))

    pulse_list = []
    date_list = []
    lowest_value = []
    today = time.strftime("%B%d", time.localtime(time.time()))

    # only Graph water usage for a single day; use compare_date.
    global compare_date
    compare_date = str(month) + str(day)

    # If there is no Query params compare_Date with be NoneNone
    if compare_date == 'NoneNone':
        compare_date = today
        month = time.strftime("%B", time.localtime(time.time()))
        day = time.strftime("%d", time.localtime(time.time()))

    # need to find the lowest value for our starting point
    # This is to avoid incorrect calculations when water.py is run for more than one day.
    for i in data[month][day]:
        # grab all of the rotations to find the lowest value as a starting point.
        lowest_value.append(i['rotations'])
    try:
        # Set the lowest value to the last value for our calculations and graphing
        last_value = min(lowest_value)
    except ValueError:
        # set the value to zero to display a blank graph; better than an Error
        last_value = 0

    # Now go through the list again to compare values for Gallons per 60 seconds
    for update in data[month][day]:
        # make time readable
        newtime = time.strftime("%H:%M", time.localtime(float(update["timestamp"])))

        # Grab the MonthDay string for capturing a single day of data
        date = time.strftime("%B%d", time.localtime(float(update["timestamp"])))

        if date == compare_date:
            # 455 pulses per liter - source: http://pnrsolution.org/Datacenter/Vol4/Issue3/16.pdf
            # rate is rotations between reporting times. current - last value
            gallons = ((int(update['rotations']) - last_value)/100)/4
            pulse_list.append(gallons)
            date_list.append(newtime)

            # set the last value to the current value for rate calculation
            last_value = int(update["rotations"])

    # Set the figure size
    fig = Figure(figsize=(16, 7))

    # Hide the whitepace of the figure
    fig.patch.set_visible(False)

    axis = fig.add_subplot(1, 1, 1)

    # use the date and pulse count to graph the data
    axis.stackplot(date_list, pulse_list, color='#19C3E5')

    # Set the spine colors
    axis.spines['bottom'].set_color('#9beafa')
    axis.spines['top'].set_color('#9beafa')
    axis.spines['left'].set_color('#9beafa')
    axis.spines['right'].set_color('#9beafa')

    # Add an Y label
    axis.set_ylabel('Gallons per Minute')

    # Set the Y axis colors
    axis.tick_params(axis='y', colors='#9beafa')

    # Set the X axis colors - rotate X axis for readability
    axis.tick_params(axis='x', colors='#9beafa', rotation=90)
    axis.yaxis.label.set_color('#9beafa')

    # Set the Title of the Graph
    axis.set_title("Water Usage", color='#9beafa')

    # Set the facecolor to the darkmode color
    axis.set_facecolor('#222')
    output = io.BytesIO()

    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype="image/png")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
