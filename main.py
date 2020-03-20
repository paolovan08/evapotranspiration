import requests
import json
from pprint import pprint
import math
import datetime
import dateutil.relativedelta

lat = '14.5905251'
lon = '120.9775773'
api_key = '9767517021d939f4f938a444372d5530'
cnt = '1'
units = 'metric'
url = 'http://api.openweathermap.org/data/2.5/forecast/'+'?lat=' + lat + '&lon=' + lon + '&cnt=' + cnt + '&units=' + units + '&appid=' + api_key

# datetime object containing current date and time
now = datetime.datetime.now()

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

currentMonth = datetime.datetime.now().month

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

def getStefanBoltzman(temperature):
    temperature = round(temperature * 2) / 2
    stefanBoltzman = {
        1.0: 27.70,
        1.5: 27.90,
        2.0: 28.11,
        2.5: 28.31,
        3.0: 28.52,
        3.5: 28.72,
        4.0: 28.93,
        4.5: 29.14,
        5.0: 29.35,
        5.5: 29.56,
        6.0: 29.78,
        6.5: 29.99,
        7.0: 30.21,
        7.5: 30.42,
        8.0: 30.64,
        8.5: 30.86,
        9.0: 31.08,
        9.5: 31.30,
        10.0: 31.52,
        10.5: 31.74,
        11.0: 31.97,
        11.5: 32.19,
        12.0: 32.42,
        12.5: 32.65,
        13.0: 32.88,
        13.5: 33.11,
        14.0: 33.34,
        14.5: 33.57,
        15.0: 33.81,
        15.5: 34.04,
        16.0: 34.28,
        16.5: 34.52,
        17.0: 34.75,
        17.5: 34.99,
        18.0: 35.24,
        18.5: 35.48,
        19.0: 35.72,
        19.5: 35.97,
        20.0: 36.21,
        20.5: 36.46,
        21.0: 36.71,
        21.5: 36.96,
        22.0: 37.21,
        22.5: 37.47,
        23.0: 37.72,
        23.5: 37.98,
        24.0: 38.23,
        24.5: 38.49,
        25.0: 38.75,
        25.5: 39.01,
        26.0: 39.27,
        26.5: 39.53,
        27.0: 39.80,
        27.5: 40.06,
        28.0: 40.33,
        28.5: 40.60,
        29.0: 40.87,
        29.5: 41.14,
        30.0: 41.41,
        30.5: 41.69,
        31.0: 41.96,
        31.5: 42.24,
        32.0: 42.52,
        32.5: 42.80,
        33.0: 43.08,
        33.5: 43.36,
        34.0: 43.64,
        34.5: 43.94,
        35.0: 44.21,
        35.5: 44.50,
        36.0: 44.79,
        36.5: 45.08,
        37.0: 45.37,
        37.5: 45.67,
        38.0: 45.96,
        38.5: 46.26,
        39.0: 46.56,
        39.5: 46.85,
        40.0: 47.15,
        40.5: 47.46,
        41.0: 47.76,
        41.5: 48.06,
        42.0: 48.37,
        42.5: 48.68,
        43.0: 48.99,
        43.5: 49.30,
        44.0: 49.61,
        44.5: 49.92,
        45.0: 50.24,
        45.5: 50.56,
        46.0: 50.87,
        46.5: 51.19,
        47.0: 51.51,
        47.5: 51.84,
        48.0: 52.16,
        48.5: 52.49
    }
    return stefanBoltzman.get(temperature, 'Invalid temp')


mean_temp = getMeanTemp(temp_min, temp_max)
# print(mean_temp, 'mean_temp')
wind_speed = getWindSpeed2M(speed_wind)
# print(wind_speed, 'wind_speed')
slope_vapour_pressure = getSlopeVapourPressure(mean_temp)
# print(slope_vapour_pressure, 'slope')
psychometric = getPsychrometric(ground_level)
# print(psychometric, 'psycho')
mean_saturation_vapor_pressure = getMeanSaturationVaporPressure(temp_min, temp_max)
# print(mean_saturation_vapor_pressure, 'mean sat')
average_daily_extraterrestrial_radiation = getAverageDailyExtraTerrestrialRadiation(currentMonth)
# print(average_daily_extraterrestrial_radiation, 'average daily')
incoming_solar_radiation = getIncomingSolarRadiation(actual_sunlight_duration, average_daily_extraterrestrial_radiation)
# print(incoming_solar_radiation, 'incoming')
clear_sky_solar_radiation = getClearSkyRadiation(5, average_daily_extraterrestrial_radiation)
# print(clear_sky_solar_radiation, 'clear sky')
# stefan_boltzman = getStefanBoltzman(mean_temp)
stefan_boltzman = 4.903*(10**-9)
# print(stefan_boltzman, 'stefan')
net_shortwave = getNetShortwave(incoming_solar_radiation)
# print(net_shortwave, 'net')
net_longwave = getNetLongwave(stefan_boltzman, temp_min, temp_max, mean_saturation_vapor_pressure, incoming_solar_radiation, clear_sky_solar_radiation)
# print(net_longwave, 'net longwave')
net_radiation = getNetRadiation(net_shortwave, net_longwave)
# print(net_radiation, 'net rad')
# crop_evapotranspiration = (0.048 * slope_vapour_pressure * ())
# print(net_radiation)
soil_heat_flux = 0
crop_coefficient = 1.05

numerator = (0.048 * slope_vapour_pressure * (net_radiation - soil_heat_flux) + psychometric * (900 / (mean_daily_temp + 273) * wind_speed) * mean_saturation_vapor_pressure)
denominator = slope_vapour_pressure + psychometric * (1 + (0.34 * wind_speed))

eto = numerator / denominator
etc = crop_coefficient * eto

# dd/mm/YY H:M:S
dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
print("Date:", dt_string)	
print('etc value is:', etc)
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
log('Temperature(C):', mean_daily_temp)
log('Humidity(%):', humidity)
log('Wind Speed(m/s):', wind_speed, '\n')