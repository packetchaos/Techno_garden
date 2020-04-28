import RPi.GPIO as GPIO
import time,sys
import requests
import threading

GPIO.setmode(GPIO.BOARD)
recv = 13
GPIO.setup(recv, GPIO.IN)

tot_cnt=0
time_end=0.0
#gpio_last=0
constant = 1.79
#pulses = 0 # for dummy program for testing

def request_data(method, url_mod):
    url= "http://water.hyrule.local/water/"

    try:
        r = requests.request(method, url + url_mod, verify=True)
        return r

    except Exception as E:
        print(E)


def sensor_loop():
    while True:
        #global pulses # dummy
        #pulses = pulses + 1 # dummy

        pulses = 0
        rate_cnt = 0
        gpio_last = 0
        # 6 pulses is one rotation
        while pulses <=5:
            # Assign and monitor input
            gpio_cur = GPIO.input(recv)

            # if the input isn't 0 and isn't in it's last state, it changes state(pulsed)
            if gpio_cur !=0 and gpio_cur != gpio_last:
                pulses += 1

            # Make last state the current state for comparison
            gpio_last = gpio_cur

        # Rate is actual rotations
        rate_cnt =+ 1

        global tot_cnt
        tot_cnt += 1


def reporter_loop():
    tot_cnt_last = 0
    while True:
        global recv
        global tot_cnt
        if tot_cnt !=0 and tot_cnt != tot_cnt_last:
            url_string = str(recv) + "/" + str(tot_cnt) + "/" + str(time.time())
            request_data("POST", url_string)
        time.sleep(30)
        tot_cnt_last = tot_cnt


thread1 = threading.Thread(target=sensor_loop)
thread1.start()

thread2 = threading.Thread(target=reporter_loop)
thread2.start()

