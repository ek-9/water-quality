import minimalmodbus
import time
import dbconnect
import requests
import psycopg2
import sys
from datetime import datetime

def convert_register_value(value1, value2):
    value2 = int(value2, 16)
    value1 = int(value1, 16)
    digit = value2 // 256
    value = value1 / (10 ** digit)

    return value

def read_register1(instrument, arr) :
    for register_address in range(16):
        response = instrument.read_register(register_address, functioncode=int('0x04', 16))
        arr.append(hex(response))
        time.sleep(0.5)


sensor_port = "/dev/tty.usbserial-10"
sensor_address_ph = 0x01
sensor_address_DO = 0x03
sensor_address_con = 0x04

now = time

try:
    # ph sensor connect
    instrument_ph = minimalmodbus.Instrument(port=sensor_port, slaveaddress=sensor_address_ph)
    instrument_ph.serial.baudrate = 9600
    instrument_ph.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument_ph.serial.bytesize = 8
    instrument_ph.serial.stopbits = 1
    instrument_ph.serial.timeout = 1

    # DO sensor connect
    instrument_DO = minimalmodbus.Instrument(port=sensor_port, slaveaddress=sensor_address_DO)
    instrument_DO.serial.baudrate = 9600
    instrument_DO.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument_DO.serial.bytesize = 8
    instrument_DO.serial.stopbits = 1
    instrument_DO.serial.timeout = 1

    instrument_con = minimalmodbus.Instrument(port=sensor_port, slaveaddress=sensor_address_con)
    instrument_con.serial.baudrate = 9600
    instrument_con.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument_con.serial.bytesize = 8
    instrument_con.serial.stopbits = 1
    instrument_con.serial.timeout = 1



except Exception as e:
    print("Could not connect : ", e)

if __name__ == '__main__':
    try:
        flag = 0

        while True:
            try :
                print(1) # 연결 잘 됐나 확인
                # ----------------------------------------------------------------------------------------------------------------
                # read ph senso용
                address_value_ph = []
                read_register1(instrument_ph, address_value_ph)

                ph = convert_register_value(address_value_ph[0], address_value_ph[1])
                temp = convert_register_value(address_value_ph[8], address_value_ph[9])
                time.sleep(2)
                #-----------------------------------------------------------------------------------------------------------------

                # ----------------------------------------------------------------------------------------------------------------
                # read DO sensor
                address_value_DO = []
                read_register1(instrument_DO, address_value_DO)

                do_value = convert_register_value(address_value_DO[0], address_value_DO[1])
                time.sleep(2)
                # ----------------------------------------------------------------------------------------------------------------

                # ----------------------------------------------------------------------------------------------------------------
                # read con sensor
                address_value_con = []
                read_register1(instrument_con, address_value_con)

                con = convert_register_value(address_value_con[0], address_value_con[1])
                con *= 100
                time.sleep(2)
                # ----------------------------------------------------------------------------------------------------------------

                # ----------------------------------------------------------------------------------------------------------------
                #send data to db

                now_time = datetime.now()
                current_time = now_time.strftime('%Y-%m-%d %H:%M:%S')

                print(current_time)
                print("ph : ", ph, "temp : ", temp)
                print("DO : ", do_value)
                print("con : ", con)

                # db = dbconnect.CRUD()
                # db.save_sensor_data(current_time,temp, ph, do_value,con)

                conn = pymysql.connect(host='localhost', user ='root', password ='soda', db ='water_sensor')
                cur = conn.cursor()
                # cur.execute("INSERT INTO water_sensor VALUES (%s, %s, %s, %s, %s)",(current_time, ph, temp, do_value, con))

                conn.commit()

                # ----------------------------------------------------------------------------------------------------------------
                # send data to server

                fishfarm_id = 3

                url_temp = "http://223.130.133.182/api/v1/temperature"

                json_temp = {
                    "timestamp": current_time,
                    "id" : fishfarm_id,
                    "temperature" : temp
                }

                url_ph = "http://223.130.133.182/api/v1/ph"

                json_ph = {
                    "timestamp": current_time,
                    "id": 2,
                    "pH": ph
                }

                url_do = "http://223.130.133.182/api/v1/do"

                json_do = {
                    "timestamp": current_time,
                    "id": 2,
                    "DO": do_value
                }

                url_con = "http://223.130.133.182/api/v1/conductivity"

                json_con = {
                    "timestamp": current_time,
                    "id": fishfarm_id,
                    "conductivity": con
                }

                response_temp = requests.post(url_temp, json=json_temp)
                response_ph = requests.post(url_ph, json=json_ph)
                response_do = requests.post(url_do, json=json_do)
                response_con = requests.post(url_con, json=json_con)
                # ----------------------------------------------------------------------------------------------------------------


            except Exception as e:
                print("ERROR : ", e)

    except minimalmodbus.NoResponseError:
        print("No request")

    finally:
        instrument_ph.serial.close()
        instrument_DO.serial.close()
        instrument_con.serial.close()

    time.sleep(1)


