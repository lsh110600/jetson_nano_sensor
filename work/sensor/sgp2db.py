# code Integrated version

import time, sys
import pymysql
import board, busio
from sgp30 import SGP30

def select_sensor_data(sensor_name, data_name):
    '''
    sensor_name = bme280 / scd30 / veml7700 / sgp30
    sensor_data = humidity / temperature / pressure / altitude / light / co2 / voc
    '''
    if sensor_name == bme280:
        d = dict(humidity = sensor_name.relative_humidity, temperature = sensor_name.temperature, pressure = sensor_name.pressure,  altitude = sensor_name.altitude)
    
    elif sensor_name == scd30:
        d = dict(humidity = sensor_name.relative_humidity, temperature = sensor_name.temperature)
 
    elif sensor_name == veml7700:
        d = dict(light = sensor_name.light)

    else:
        (eco2, tvoc) = sgp30.get_air_quality_value()
        d = dict(co2 = eco2, voc = tvoc)

    if d[data_name] is not None:
        return d[data_name]
    else:
        select_sensor_data(sensor_name, data_name)   


def initial_set(sensor_name, data_name, retries=10, delay_seconds=1):
    for i in range(retries):
        for j in range(len(data_name)):
            data = select_sensor_data(sensor_name, data_name[j])
            if data is not None :
                print('. ', end='')
                time.sleep(delay_seconds)
            else:
                print('None')
def crude_progress_bar():
    sys.stdout.write('.')
    sys.stdout.flush()

def switch_sensor_name(value):
	return {'bme280': bme280, 'scd30' : scd30, 'veml7700' : veml7700, 'sgp30' : sgp30}.get(value, -1)

conn = pymysql.connect(host="localhost", user="lsh110600", passwd="1234", db ="sensor_db")
print("Sensor warming up, please wait...")

sgp30 = SGP30()
sgp30.start_measurement(crude_progress_bar)

bme280 = 'bme280'
scd30 = 'scd30'
veml7700 = 'veml7700'

#initial setting
#sensor_name_list = [bme280, scd30, veml7700, sgp30]
sensor_data_list_bme = ['humidity', 'temperature', 'pressure', 'altitude']
sensor_data_list_scd = ['humidity', 'temperature']
sensor_data_list_veml= ['light']
sensor_data_list_sgp = ['co2', 'voc']

variable_ea = 2

try:
    with conn.cursor() as cur:
        sql = "insert into sgp30 values(%s, %s, %s)"
        while True:
            for _ in range(0, variable_ea):
                globals()['val{}'.format(_)] =  str(select_sensor_data(sgp30, sensor_data_list_sgp[_]))
            if val0 is not None and val1 is not None:
                print(val0, val1)
                cur.execute(sql, (time.strftime("%Y-%m-%d %H-%M-%S", time.localtime()),val0, val1))
                conn.commit()
            else:
                print("Failded to get reading")			
            time.sleep(1)
except KeyboardInterrupt:
    exit()
finally :
    conn.close()
			    

'''
# value print 
while True:
	data = scd30.data_available
	if data:
		print("-"*35)
		print("*"*5, "BME280", "*"*5) 
		print("Temperature: %0.1f C" % bme280.temperature)
		print("Humidity: %0.1f %%" % bme280.relative_humidity)
		print("Pressure: %0.1f hPa" % bme280.pressure)
		print("Altitude = %0.2f meters \n" % bme280.altitude)

		print("*"*5, "SCD30", "*"*5) 
		print("CO2:", scd30.eCO2, "PPM")
		print("Temperature:", scd30.temperature, "degrees C")
		print("Humidity::", scd30.relative_humidity, "%%rH \n")
	
		print("*"*5, "VEML7700", "*"*5) 
		print("Ambient light:", veml7700.light)
		print("\n")
		
		print("*"*5, "SGP30", "*"*5) 
		result = sgp30.get_air_quality()
		print(result)
		print("-"*35)

		time.sleep(2)
		print("\n")
'''
