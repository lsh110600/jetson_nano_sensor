# code Integrated version


import time, sys

import board, busio
from sgp30 import SGP30
import adafruit_bme280
import adafruit_scd30
import adafruit_veml7700

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
print("Temperature offset:", scd30.temperature_offset)
print("Measurement interval:", scd30.measurement_interval)
print("Self-calibration enabled:", scd30.self_calibration_enabled)
print("Ambient Pressure:", scd30.ambient_pressure)
print("Altitude:", scd30.altitude, "meters above sea level")
print("Forced recalibration reference:", scd30.forced_recalibration_reference)

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
	
