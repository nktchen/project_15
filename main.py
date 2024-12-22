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


@dp.message(F.text == '/start') #TODO добавить инлайн для команды help
async def send_welcome(message: types.Message):
    user_states[message.from_user.id] = {
        'state': BOT_INFORMATION,
        'locations': [],
        'time': None
    }

    await message.answer('Привет! Я могу предоставить данные о погодных условиях в каждой точке твоего маршрута! Напиши /help, чтобы узнать все мои команды!!')

@dp.message(F.text == '/help') #TODO добавить инлайн для команды weather
async def show_commands(message: types.Message):
    commands_msg = """Мои команды:
    /start - показать приветственное сообщение
    /help - показать список доступных команд и краткую инструкцию по использованию бота
    /weather - составить маршрут и прогноз погоды!
    Напиши /weather, заполни информацию, ответив на пару вопросов, и получи персонализированный прогноз погода по всем точкам твоегом маршрута.
    """
    await message.answer(commands_msg)

@dp.message(F.text == '/weather')
async def weather(message: types.Message):
    user_states[message.from_user.id]['state'] = LOCATION_INFORMATION
    await message.answer('Чтобы расчитать маршрут, введите ОТКУДА вы едете:')




@dp.message(F.text)
async def process_city(message: types.Message):
    if user_states[message.from_user.id]['state'] == LOCATION_INFORMATION:
        city_name = message.text
        user_states[message.from_user.id]['locations'].append(city_name)
        await message.answer(f"Вы ввели {len(user_states[message.from_user.id]['locations'])} город: {city_name}")


# Запуск бота
if __name__ == '__main__':
    async def main():
        # Подключаем бота и диспетчера
        await dp.start_polling(bot)

    # Запускаем главный цикл
    asyncio.run(main())