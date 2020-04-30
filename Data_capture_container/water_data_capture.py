from flask import Flask, render_template, jsonify
from Data_capture_container.database import new_db_connection, insert_raw_water_stats, create_table


app = Flask(__name__)


def prep_db():
    database = r"water_raw.db"
    water_conn = new_db_connection(database)
    water_conn.execute('pragma journal_mode=wal;')
    create_table_raw_water = """CREATE TABLE IF NOT EXISTS water (
                                sensor_id int,
                                raw_value float,
                                time text
                                );"""

    create_table(water_conn, create_table_raw_water)
    return


@app.route('/water/<sensorid>/<raw>/<time>', methods=["POST"])
def post_info(sensorid, raw, time):
    try:
        database = r"water_raw.db"
        water_conn = new_db_connection(database)
        water_conn.execute('pragma journal_mode=wal;')
        raw_list = []

        with water_conn:
            raw_list.append(sensorid)
            raw_list.append(raw)
            raw_list.append(time)

            insert_raw_water_stats(water_conn, raw_list)

        return render_template("success.html")

    except TypeError:
        pass


@app.route('/water', methods=["GET"])
def get_info():
    try:
        database = r"water_raw.db"
        water_conn = new_db_connection(database)
        water_conn.execute('pragma journal_mode=wal;')
        raw_list = []
        with water_conn:
            cur = water_conn.cursor()
            cur.execute("SELECT * FROM water;")

            rows = cur.fetchall()
            for x in rows:
                json_return = {"sensor_id": x[0], "rotation_count": x[1], "time": x[2]}

                raw_list.append(json_return)

            return jsonify(raw_list)

    except TypeError:
        pass


if __name__ == '__main__':
    prep_db()
    app.run(host="0.0.0.0", port=5004)
