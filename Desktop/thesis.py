import RPi.GPIO as GPIO
import time, sys

import requests
import json
from pprint import pprint
import math
import datetime
import dateutil.relativedelta

GPIO.setmode(GPIO.BOARD)

inpt = 13
valve1 = 40
valve2 = 38
valve3 = 36

GPIO.setup(inpt, GPIO.IN)
GPIO.setup(valve1, GPIO.OUT)
GPIO.setup(valve2, GPIO.OUT)
GPIO.setup(valve3, GPIO.OUT)

def valve_on(pin):
    GPIO.output(pin, GPIO.LOW)  # Turn valve on
def valve_off(pin):
    GPIO.output(pin, GPIO.HIGH)  # Turn valve off

rate_cnt = 0
tot_cnt = 0
time_zero = 0.0
time_start = 0.0
time_end = 0.0
gpio_last = 0
pulses = 0
constant = 1.79

# @14.6130769,120.9989896
lat = '14.5905251'
lon = '120.9775773'
api_key = '9767517021d939f4f938a444372d5530'
cnt = '1'
units = 'metric'
url = 'http://api.openweathermap.org/data/2.5/forecast/'+'?lat=' + lat + '&lon=' + lon + '&cnt=' + cnt + '&units=' + units + '&appid=' + api_key

# datetime object containing current date and time
now = datetime.datetime.now()
currentMonth = datetime.datetime.now().month

weather = requests.get(url).json()

temp_min = weather['list'][0]['main']['temp_min']
temp_max = weather['list'][0]['main']['temp_max']
speed_wind = weather['list'][0]['wind']['speed']
ground_level = weather['list'][0]['main']['grnd_level']
sunrise = weather['city']['sunrise']
sunset = weather['city']['sunset']
mean_daily_temp = weather['list'][0]['main']['temp']
humidity = weather['list'][0]['main']['humidity']

dt1 = datetime.datetime.fromtimestamp(sunrise) # 1973-11-29 22:33:09
dt2 = datetime.datetime.fromtimestamp(sunset) # 1977-06-07 23:44:50
rd = dateutil.relativedelta.relativedelta (dt2, dt1)
actual_sunlight_duration = rd.hours
# pprint(weather)

# for entry in weather['list']:
#     cmd = entry['main']
#     print(cmd)

def getMeanTemp(min_temp, max_temp):
    mean_temp = (min_temp + max_temp) / 2
    return mean_temp

def getWindSpeed2M(wind_speed, height_above_ground = 10):
    u2 = (wind_speed * 4.87) / math.log((67.8 * height_above_ground) - 5.42)
    return u2

def getSlopeVapourPressure(temp_mean):
    exp = 2.7183
    slope_vapour_pressure = (4098*(0.6108*exp*((17.27 * temp_mean) / (temp_mean + 237.3))))/((temp_mean+237.3)**2)
    return slope_vapour_pressure

def getPsychrometric(pressure_ground_level):
    # convert hectopascal to kilopascal
    pressure_ground_level = pressure_ground_level / 10
    psychrometric = 0.000665 * pressure_ground_level
    return psychrometric

def getMeanSaturationVaporPressure(min_temp, max_temp):
    exp = 2.7183
    minSaturationVaporPressure = 0.6108*exp*((17.27 * max_temp) / (max_temp + 237.3))
    maxSaturationVaporPressure = 0.6108*exp*((17.27 * min_temp) / (min_temp + 237.3))
    meanSaturationVaporPressure = (minSaturationVaporPressure + maxSaturationVaporPressure) / 2
    return meanSaturationVaporPressure

def getNetRadiation(net_shortwave, net_longwave):
    net_radiation = net_shortwave - net_longwave
    return net_radiation

def getNetShortwave(incoming_solar_radiation):
    albedo = 0.23
    net_shortwave = (1 - albedo) * incoming_solar_radiation
    return net_shortwave

def getNetLongwave(stefanBoltzmanConstant, min_temp, max_temp, actualVaporPressure, incoming_solar_radiation, clear_sky_solar_radiation):
    bracket1 = ((max_temp + 273.16)**4 + (min_temp + 273.16)**4)/2
    bracket2 = 0.34 - (0.14 * math.sqrt(actualVaporPressure))
    bracket3 = (1.35 * (incoming_solar_radiation / clear_sky_solar_radiation)) - 0.35
    net_longwave = stefanBoltzmanConstant * bracket1 * bracket2 * bracket3
    return net_longwave

def getClearSkyRadiation(station_elevation, extraterrestrial_radiation):
    clear_sky_solar_radiation = extraterrestrial_radiation * (0.75 + (0.00002 * station_elevation))
    return clear_sky_solar_radiation

def getIncomingSolarRadiation(actual_sunlight_duration, extraterrestrial_radiation,  max_sunlight_duration = 12):
    extraterrestrial_radiation_clear_days = 1
    incoming_solar_radiation = extraterrestrial_radiation * (extraterrestrial_radiation_clear_days * (actual_sunlight_duration/max_sunlight_duration))
    return incoming_solar_radiation

def getAverageDailyExtraTerrestrialRadiation(month):
    averageDailyExtraTerrestrialRadiation = {
        1: 29.6,
        2: 32.6,
        3: 35.9,
        4: 38.0,
        5: 38.5,
        6: 38.4,
        7: 38.3,
        8: 38.0,
        9: 36.4,
        10: 33.4,
        11: 30.1,
        12: 28.5
    }
    return averageDailyExtraTerrestrialRadiation.get(month, 'Invalid month')

stefan_boltzman = 4.903*(10**-9)
soil_heat_flux = 0
crop_coefficient = 1.05
mm_day = 0.0364
number_of_plants = 3

mean_temp = getMeanTemp(temp_min, temp_max)
wind_speed = getWindSpeed2M(speed_wind)
slope_vapour_pressure = getSlopeVapourPressure(mean_temp)
psychometric = getPsychrometric(ground_level)
mean_saturation_vapor_pressure = getMeanSaturationVaporPressure(temp_min, temp_max)
average_daily_extraterrestrial_radiation = getAverageDailyExtraTerrestrialRadiation(currentMonth)
incoming_solar_radiation = getIncomingSolarRadiation(actual_sunlight_duration, average_daily_extraterrestrial_radiation)
clear_sky_solar_radiation = getClearSkyRadiation(5, average_daily_extraterrestrial_radiation)

net_shortwave = getNetShortwave(incoming_solar_radiation)
net_longwave = getNetLongwave(stefan_boltzman, temp_min, temp_max, mean_saturation_vapor_pressure, incoming_solar_radiation, clear_sky_solar_radiation)
net_radiation = getNetRadiation(net_shortwave, net_longwave)

numerator = (0.048 * slope_vapour_pressure * (net_radiation - soil_heat_flux) + psychometric * (900 / (mean_daily_temp + 273) * wind_speed) * mean_saturation_vapor_pressure)
denominator = slope_vapour_pressure + psychometric * (1 + (0.34 * wind_speed))

eto = numerator / denominator
etc = crop_coefficient * eto

total_liters = etc * mm_day * number_of_plants * 100


# dd/mm/YY H:M:S
dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
print("Date:", dt_string)	
print('etc value is:', etc)
print('Total Liters:', total_liters)
print('Temperature(C):', mean_daily_temp)
print('Humidity(%):', humidity)
print('Wind Speed(m/s):', wind_speed)

def log(*params):
    with open("/home/pi/Desktop/logger.txt", "a") as log:
        for param in params:
            log.write(str(param)+' ')
        log.write('\n')

log("Date:", dt_string)	
log('etc value is:', etc)
log('Total Liters:', total_liters)
log('Temperature(C):', mean_daily_temp)
log('Humidity(%):', humidity)
log('Wind Speed(m/s):', wind_speed, '\n')

print('Water Flow - Approximate')

time_zero = time.time()

valve_off(valve1)
valve_off(valve2)
valve_off(valve3)
time.sleep(3)
valve_on(valve1)

total_liters = 100

while True:
	rate_cnt = 0
	pulses = 0
	time_start = time.time()
	while pulses <= 5:
		gpio_cur = GPIO.input(inpt)
		if gpio_cur != 0 and gpio_cur != gpio_last:
			pulses += 1
		gpio_last = gpio_cur
		try:
			None
		except KeyboardInterrupt:
			GPIO.cleanup()
			print('Done')
			sys.exit()

	rate_cnt += 1
	tot_cnt += 1
	time_end = time.time()

    	total_water = round(tot_cnt * constant, 1)
    	rate = round((rate_cnt * constant) / (time_end - time_start), 2)
    	minutes_running = round((time.time()-time_zero) / 60.2), '\t', time.asctime(time.localtime(time.time()))

	print('Liters per minute', rate, 'approximate')
	print('Total ', total_water)
	print('Time (min & clock) ', minutes_running, '\n')

    	if total_water <= total_liters:
        	valve_on(valve1)
        	valve_off(valve2)
        	valve_off(valve3)
    	elif total_water <= (total_liters + (total_liters * 0.7)):
        	valve_off(valve1)
        	valve_on(valve2)
        	valve_off(valve3)
	elif total_water <= (total_liters + (total_liters * 0.7) + (total_liters * 1)):
        	valve_off(valve1)
        	valve_off(valve2)
        	valve_on(valve3)
    	else:
        	valve_off(valve1)
        	valve_off(valve2)
        	valve_off(valve3)
		sys.exit()