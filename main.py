from aiogram import Bot, Dispatcher, types, F
import logging
import asyncio

with open('token.txt') as f:   #чтение токена
    API_TOKEN = f.readline().strip()

bot = Bot(token=API_TOKEN)  #создаем сущности бота и диспетчера
dp = Dispatcher()


@dp.message(F.text == '/start')
async def send_welcome(message: types.Message):
    await message.answer('Привет! Я могу предоставить данные о погодных условиях! Напиши help, чтобы узнать мои команды!!')

@dp.message(F.text == '/help')
async def show_commands(message: types.Message):
    commands_msg = """Мои команды:
    /start - показать это сообщение снова
    /help - показать список доступных команд и краткую инструкцию по использованию бота
    /weather - составить маршрут и прогноз погоды!
    
    Напиши /weather, заполни информацию, ответив на пару вопросов, и получи персонализированный прогноз погода по всем точкам твоегом маршрута.
    """
    await message.answer(commands_msg)

# Запуск бота
if __name__ == '__main__':
    async def main():
        # Подключаем бота и диспетчера
        await dp.start_polling(bot)

    # Запускаем главный цикл
    asyncio.run(main())