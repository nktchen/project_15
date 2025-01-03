from aiogram import Bot, Dispatcher, types, F
import asyncio
from web.weather_checker_model import WeatherModel

with open('token.txt') as f:   #чтение токена
    API_TOKEN = f.readline().strip()

bot = Bot(token=API_TOKEN)  #создаем сущности бота и диспетчера, API KEY для AccuWeather (мне не жалко, пусть крадут)
dp = Dispatcher()
weather_model = WeatherModel('mqiZotA2vL62GqZwFlLA1p9UQG5jWlOg')

user_states = {}

#Состояния!
BOT_INFORMATION = 'SHOWING COMMANDS' #состояние показа информации о боте
LOCATION_INFORMATION = 'COLLECTING LOCATIONS' #состояние сбора информации о метах маршрута
TIME_INFORMATION = 'COLLECTING TIMES' #состояние сбора времени
GETTING_INFORMATION = 'COLLECTING THINGS' #запрос к API прогноза погоды
SHOW_WEATHER_INFORMATION = 'SHOWING WEATHER!' #показ прогноза погоды

#Начало работы бота
#Стартовое сообщение бота
@dp.message(F.text == '/start') #TODO добавить инлайн для команды help
async def send_welcome(message: types.Message):
    user_states[message.from_user.id] = { #Объект хранения состояний
        'state': BOT_INFORMATION,
        'locations': [],
        'time': None
    }

    await message.answer('Привет! Я могу предоставить данные о погодных условиях в каждой точке твоего маршрута! Напиши /help, чтобы узнать все мои команды!!')


#команда help
@dp.message(F.text == '/help')
async def show_commands(message: types.Message):
    commands_msg = """Мои команды:
    /start - показать приветственное сообщение
    /help - показать список доступных команд и краткую инструкцию по использованию бота
    /weather - составить маршрут и прогноз погоды!
    Напиши /weather, заполни информацию, ответив на пару вопросов, и получи персонализированный прогноз погода по всем точкам твоегом маршрута.
    """
    await message.answer(commands_msg)


#Переходим в состояние выбора городов, ожидаем ввода городов.
@dp.message(F.text == '/weather')
async def weather(message: types.Message):
    user_states[message.from_user.id]['state'] = LOCATION_INFORMATION
    await message.answer('Чтобы расчитать маршрут, введите ОТКУДА, КУДА, и остальные части вашего маршрута, ГОРОДА ВВОДИТЕ НА АНГЛИЙСКОМ!!!!:')


#Обработчик ввода городов, ошибок при вводе
@dp.message(F.text)
async def process_msg(message: types.Message):
    # если в состоянии выбора, то вносим города в состояния, при вводе предлагаем завершить ввод с помощью инлайн кнокпи
    if user_states[message.from_user.id]['state'] == LOCATION_INFORMATION:
        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text='Да', callback_data='confirm_locations')]])
        city_name = message.text
        user_states[message.from_user.id]['locations'].append(city_name)
        await message.answer(f"Вы ввели {len(user_states[message.from_user.id]['locations'])} город: {city_name}, закончить выбор? Если нет, то введите следующий город", reply_markup=inline_keyboard)
    else:
        await message.answer('НЕТ ТАКОЙ КОМАНДЫ!!!!! напишите /help для списка команд')


#Подтверждение маршрута
@dp.callback_query(F.data == 'confirm_locations')
async def confirm_locations(callback_query: types.CallbackQuery):
    if len(user_states[callback_query.from_user.id]['locations']) >= 2:
        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text='Да', callback_data='time')], [types.InlineKeyboardButton(text='Нет', callback_data='restart_weather')]])
        await callback_query.message.answer(f'Вы выбрали города: {' '.join([str(city) for city in user_states[callback_query.from_user.id]['locations']])}')
        await callback_query.message.answer(f'Подтверждаете выбор?', reply_markup=inline_keyboard)
    else:
        await callback_query.message.answer('Слишком мало точек маршрута! нужно минимум 2. Продолжайте вводить города')


#если не подтведили выбор городов, начинаем ввод заново, повторяет функционал weather()
@dp.callback_query(F.data == 'restart_weather')
async def restart_weather(callback_query: types.CallbackQuery):
    user_states[callback_query.from_user.id]['locations'] = []
    await callback_query.message.answer('Начинаю ввод заново...')
    user_states[callback_query.from_user.id]['state'] = LOCATION_INFORMATION
    await callback_query.message.answer('Начинаю ввод заново... Введите ОТКУДА, КУДА и остальные части вашего маршрута:')


#Обработка выбора времени
@dp.callback_query(F.data == 'time')
async def process_time(callback_query: types.CallbackQuery):
    user_states[callback_query.from_user.id]['state'] = TIME_INFORMATION
    inline_keyboard = types.InlineKeyboardMarkup( #создание инлайн кнопок
            inline_keyboard=[[types.InlineKeyboardButton(text='Сейчас', callback_data='now')],
                         [types.InlineKeyboardButton(text='Через час', callback_data='one_hour')],
                         [types.InlineKeyboardButton(text='Через 3 часа', callback_data='three_hours')],
                         [types.InlineKeyboardButton(text='Через день', callback_data='tommorow')]])
    await callback_query.message.answer('Выберите время, через которое выводить прогноз погоды:', reply_markup=inline_keyboard)


#обработка  выбора времени через инлайн клаву, обращение к API, вывод погоды
@dp.callback_query(F.data.in_(['now', 'one_hour', 'three_hours', 'tomorrow']))
async def api(callback_query: types.CallbackQuery):
    user_states[callback_query.from_user.id]['state'] = GETTING_INFORMATION
    selected_time = callback_query.data
    user_states[callback_query.from_user.id]['time'] = selected_time
    await callback_query.message.answer('делаю запросы к API...')

    location_keys = [weather_model.get_location_key(city) for city in user_states[callback_query.from_user.id]['locations']]
    if any([key_resp == 'ПРОБЛЕМА С ГОРОДАМИ' for key_resp in location_keys]): #Если есть проблема с обращением к апи города
        await callback_query.message.answer('ПРОБЛЕМА С ГОРОДАМИ, введите /help')

    weathers = [weather_model.get_weather_data(key_city) for key_city in location_keys]
    if any([weather_resp == 'ПРОБЛЕМА ПРИ ОБРАЩЕНИИ К API' for weather_resp in weathers]): #Если есть проблема с обращением к апи погода
        await callback_query.message.answer('ПРОБЛЕМА ПРИ ОБРАЩЕНИИ К API ПОГОДЫ, введите /help')
    user_states[callback_query.from_user.id]['state'] = SHOW_WEATHER_INFORMATION
    i = 0
    weather_info = 'Прогноз для '
    for weather_data in weathers:
        weather_info += f"""
Город : {user_states[callback_query.from_user.id]['locations'][i]}
Температура: {weather_data['temperature']} градусов Цельсия
Идут ли осадки: {weather_data['is_precipitation']}
Скорость ветра: {weather_data['wind']} м/c
            
            """
        i+=1
    weather_info += '\nспасибо за использование бота!!! :) для перезапуска нажмите - /weather'
    await callback_query.message.answer(weather_info)

# Запуск бота
if __name__ == '__main__':
    async def main():
        # Подключаем бота и диспетчера
        await dp.start_polling(bot)

    # Запускаем главный цикл
    asyncio.run(main())