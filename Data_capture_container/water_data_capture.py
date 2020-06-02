from flask import Flask, render_template, jsonify, request
from Data_capture_container.database import new_db_connection, insert_raw_water_stats, create_table
import time
app = Flask(__name__)


def prep_db():
    database = r"water_raw.db"
    water_conn = new_db_connection(database)
    water_conn.execute('pragma journal_mode=wal;')
    create_table_raw_water = """CREATE TABLE IF NOT EXISTS water (
                                month text,
                                day text,
                                sensor_id int,
                                raw_value int,
                                time text
                                );"""

    create_table(water_conn, create_table_raw_water)
    return


def transform(raw):
    """
    Transforms the flat list into a nested dictionary structure
    """
    resp = dict()
    for item in raw:
        # convert the list into known attributes.  This should make the rest of
        # the code a lot more readable.
        month = item[0]
        day = item[1]
        entry = {
            'sensor': item[2],
            'rotations': item[3],
            'timestamp': float(item[4])
        }
        # if the month key doesn't exist, then we will create an empty dict.
        if month not in resp:
            resp[month] = dict()
        # if the day key doesn't exist, we will create and empty list.
        if day not in resp[month]:
            resp[month][day] = list()
        # if the entry is not already in the ledger, then add it.
        if entry not in resp[month][day]:
            resp[month][day].append(entry)
        # Re-sort the data to be from earliest time to latest time.
        resp[month][day].sort(key=lambda k: k['timestamp'])
    return resp


@app.route('/water/<sensorid>/<raw>/<timestamp>', methods=["POST"])
def post_info(sensorid, raw, timestamp):
    try:
        database = r"water_raw.db"
        water_conn = new_db_connection(database)
        water_conn.execute('pragma journal_mode=wal;')
        raw_list = []

        # pull out the month and Day to make data retreival easier.
        month = time.strftime("%B", time.localtime(float(timestamp)))
        day = time.strftime("%d", time.localtime(float(timestamp)))
        with water_conn:
            raw_list.append(month)
            raw_list.append(day)
            raw_list.append(sensorid)
            raw_list.append(raw)
            raw_list.append(timestamp)

            insert_raw_water_stats(water_conn, raw_list)

        return render_template("success.html")

    except TypeError:
        pass


@app.route('/', methods=["GET"])
@app.route('/water', methods=["GET"])
def get_info():
    try:
        database = r"water_raw.db"
        water_conn = new_db_connection(database)
        water_conn.execute('pragma journal_mode=wal;')
        raw_list = []

        sensor_id = request.args.get('sensor')
        with water_conn:
            cur = water_conn.cursor()

            # If a sensor isn't supplied, provide all of the data
            if sensor_id is None:
                cur.execute("SELECT * FROM water;")
            else:
                cur.execute("SELECT * FROM water where sensor_id ={};".format(sensor_id))

            rows = cur.fetchall()

            for x in rows:
                json_return = [x[0], x[1], x[2], x[3], x[4]]
                raw_list.append(json_return)

            return transform(raw_list)  # Send the list to get transformed into a nicely structured json blob

    except TypeError:
        pass


if __name__ == '__main__':
    prep_db()
    app.run(host="0.0.0.0", port=5004)
