# code Integrated version


import time, sys

import board, busio
from sgp30 import SGP30
import adafruit_bme280, adafruit_scd30, adafruit_veml7700
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np 
import argparse

parser = argparse.ArgumentParser(description="--sensor_name --data_name")
parser.add_argument('--sensor_name', required = True, help='bme280 / scd30 / veml7700 / sgp30')
parser.add_argument('--data_name', required = True, help='humidity / temperature / pressure / altitude / light / co2 / voc ')

def crude_progress_bar():
      sys.stdout.write('.')
      sys.stdout.flush()

print("Sensor warming up, please wait...")
sgp30 = SGP30()
sgp30.start_measurement(crude_progress_bar)
sys.stdout.write('\n')

i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
scd30 = adafruit_scd30.SCD30(i2c)
veml7700 = adafruit_veml7700.VEML7700(i2c)

#initial setting
bme280.sea_level_pressure = 1013.25
'''
print("Temperature offset:", scd30.temperature_offset)
print("Measurement interval:", scd30.measurement_interval)
print("Self-calibration enabled:", scd30.self_calibration_enabled)
print("Ambient Pressure:", scd30.ambient_pressure)
print("Altitude:", scd30.altitude, "meters above sea level")
print("Forced recalibration reference:", scd30.forced_recalibration_reference)
'''

def switch_sensor_name(value):
	return {'bme280': bme280, 'scd30' : scd30, 'veml7700' : veml7700, 'sgp30' : sgp30}.get(value, -1)


args = parser.parse_args()
sensor_name = switch_sensor_name(args.sensor_name)
data_name = args.data_name


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

# Graph y range setting
def setting_ylim(sensor_name, data_name, num=10):
    list_ylim = []
    for _ in range(num):
	    list_ylim.append(select_sensor_data(sensor_name, data_name))
    print(list_ylim)
    max_index = list_ylim.index(max(list_ylim))
    min_index = list_ylim.index(min(list_ylim))
    list_ylim[max_index] = None
    list_ylim[min_index] = None
    
    list_mean = sum(filter(None,list_ylim))/(num-2)  
    ylim_low = list_mean - (list_mean - min(filter(None,list_ylim)))*10
    ylim_high = list_mean+ (max(filter(None,list_ylim)) - list_mean)*10

    print(ylim_low,ylim_high) 
    return (ylim_low, ylim_high)

# real-time graph
fig = plt.figure()
ax = plt.axes(xlim=(0, 50), ylim=setting_ylim(sensor_name, data_name))
line, = ax.plot([], [], lw=1, c='blue',marker='d',ms=2)
max_points = 50
line, = ax.plot(np.arange(max_points), 
                np.ones(max_points, dtype=np.float)*np.nan, lw=1, c='blue',marker='d',ms=2)

def read_retry(retries=100, delay_seconds=2, platform=None):
    for i in range(retries):
        data = select_sensor_data(sensor_name, data_name)

        if data is not None :
            return data
        time.sleep(delay_seconds)
    return (None, None, None, None)

def init():
    return line

def animate(i,data='h'):
    y = read_retry() 
    old_y = line.get_ydata()
    new_y = np.r_[old_y[1:], y]
    line.set_ydata(new_y)
    print(new_y)
    return line,

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=False)
ax.autoscale_view() 
plt.show()

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
