import telebot
import requests as req
from config import open_weather_token, telebot_token
import datetime

bot = telebot.TeleBot(telebot_token)
list_city = []

@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, <b>{message.from_user.first_name} <u>{message.from_user.last_name}</u></b>! ' \
           f'Напиши название интересующего города и я расскажу тебе о погоде в этом городе!'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler(content_types=['text'])
def understanding_city(message):
    try:
        geo = req.get(
            f'http://api.openweathermap.org/geo/1.0/direct?q={message.text}&limit=5&appid={open_weather_token}'
        )
        data1 = geo.json()
        while True:
            list_city.clear()
            for geo1 in data1:
                country = geo1['country']
                if 'state' in geo1:
                    state = geo1['state']
                else:
                    state = geo1['country']
                lat = geo1['lat']
                lon = geo1['lon']
                name = geo1['name']
                list_city.append([country, state, lat, lon, name])
            if len(list_city) > 1:
                bot.send_message(message.chat.id, 'Я нашел несколько таких городов:')
                for city in list_city:
                    bot.send_message(message.chat.id, f'{list_city.index(city)+1}. Страна: {city[0]}; Область: {city[1]}; Широта: {city[2]}; Долгота: {city[3]}')
                enter_message(message)
            else:
                get_weather(list_city[0][2], list_city[0][3], message)
            break
    except:
        bot.send_message(message.chat.id, 'Введите название города!')

@bot.message_handler(content_types=['text'])
def enter_message(message):
    bot.send_message(message.chat.id, f'Введите номер: ')
    bot.register_next_step_handler(message, pogoda_choice)

def pogoda_choice(message):
    try:
        for oblast in list_city:
                if list_city.index(oblast)+1 == int(message.text):
                    lon_finish = oblast[2]
                    lat_finish = oblast[3]
                    get_weather(lon_finish, lat_finish, message)
    except:
        bot.send_message(message.chat.id, 'Попробуйте еще раз!!!')

@bot.message_handler(content_types=['text'])
def get_weather(lat, lon, message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    r = req.get(
        (f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={open_weather_token}&units=metric')
    )
    data = r.json()
    city = list_city[0][-1]
    cur_weather = data['main']['temp']
    weather_description = data["weather"][0]["main"]
    if weather_description in code_to_smile:
        wd = code_to_smile[weather_description]
    else:
        wd = "Посмотри в окно, не пойму что там за погода!"
    humidity = data['main']['humidity']
    pressure = int(data['main']['pressure'] / 1.33333)
    speed_wind = data['wind']['speed']
    sunrise_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
    sunset_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunset'])
    bot.send_message(message.from_user.id,
                     f'Погода в городе: {city}\nТемпература: {cur_weather} °С {wd}\nВлажность: {humidity} %\n'
                     f'Давление: {pressure} мм. рт. ст.\nСкорость ветра: {speed_wind} м/с\n'
                     f'Восход солнца: {sunrise_timestamp}\nЗаход солнца: {sunset_timestamp}')

bot.polling(none_stop=True)
