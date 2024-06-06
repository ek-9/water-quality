from ML import dl_
import PumpControl
import modb
import pymysql

conn = pymysql.connect(host='103.252.1.144', user='sensor', password='sensor', db='sensor', port=3306)
