from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
import asyncio

with open('token.txt') as f:   #чтение токена
    API_TOKEN = f.readline().strip()

bot = Bot(token=API_TOKEN)  #создаем сущности бота и диспетчера
dp = Dispatcher()

user_states = {}

#Состояния!
BOT_INFORMATION = 'SHOWING COMMANDS' #состояние показа информации о боте
LOCATION_INFORMATION = 'COLLECTING LOCATIONS' #состояние сбора информации о метах маршрута
TIME_INFORMATION = 'COLLECTING TIMES' #состояние сбора времени
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
@dp.message(F.text == '/help') #TODO добавить инлайн для команды weather
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
    await message.answer('Чтобы расчитать маршрут, введите ОТКУДА, КУДА, и остальные части вашего маршрута:')

@dp.message(F.text) #Обработчик обычных сообщений не команд
async def process_msg(message: types.Message):
    # если в состоянии выбора, то вносим города в состояния, при вводе предлагаем завершить ввод с помощью инлайн кнокпи
    if user_states[message.from_user.id]['state'] == LOCATION_INFORMATION:
        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text='Да', callback_data='confirm_locations')]])
        city_name = message.text
        user_states[message.from_user.id]['locations'].append(city_name)
        await message.answer(f"Вы ввели {len(user_states[message.from_user.id]['locations'])} город: {city_name}, закончить выбор? Если нет, то введите следующий город", reply_markup=inline_keyboard)

@dp.callback_query(F.data == 'confirm_locations') #Подтверждение маршрута
async def confirm_locations(callback_query: types.CallbackQuery):
    print(user_states[callback_query.from_user.id])
    print(len(user_states[callback_query.from_user.id]['locations']))
    if len(user_states[callback_query.from_user.id]['locations']) >= 2:
        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text='Да', callback_data='time')], [types.InlineKeyboardButton(text='Нет', callback_data='restart_weather')]])
        await callback_query.message.answer(f'Вы выбрали города: {[str(city) for city in user_states[callback_query.from_user.id]['locations']]}')
        await callback_query.message.answer(f'Подтверждаете выбор?', reply_markup=types.ReplyKeyboardRemove())

    else:
        await callback_query.message.answer('Слишком мало точек маршрута! нужно минимум 2. Продолжайте вводить города')
@dp.callback_query(F.data == 'restart_weather')

async def restart_weather(callback_query: types.CallbackQuery): #если не подтведили выбор городов, начинаем ввод заново
    await weather()

@dp.callback_query(F.data == 'time') #Обработка выбора времени
async def process_time(callback_query: types.CallbackQuery):



# Запуск бота
if __name__ == '__main__':
    async def main():
        # Подключаем бота и диспетчера
        await dp.start_polling(bot)

    # Запускаем главный цикл
    asyncio.run(main())