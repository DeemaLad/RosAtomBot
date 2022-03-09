from config import API_TOKEN
import logging
import json
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text 
from sqlighter import SQLighter

from parser import check_new_updates, save_fresh_news, get_first_news

#Уровень логов
logging.basicConfig(level=logging.INFO)

#Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

#Инициализация соединения с БД
db = SQLighter('db.db')

"""Начало работы с ботом /start"""
@dp.message_handler(commands= ["start"])
async def start(message: types.Message):
	start_buttons = ["Подписаться на рассылку", "Отписаться от рассылки", "Получить информацию о новой закупке"]
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
	keyboard.add(*start_buttons)
	await message.answer("Выберите действие", reply_markup=keyboard)

"""Кнопка подписаться на рассылку"""
@dp.message_handler(Text(equals="Подписаться на рассылку"))
async def subscribe(message: types.Message):
	#Если пользователя в бд нет, добавляем его
	if (not db.subscriber_exists(message.from_user.id)):
		db.add_subscriber(message.from_user.id)
		#Если есть - обновляем статус подписки
	else:
		db.update_subscription(message.from_user.id, True)

	await message.answer("Вы успешно подписались на рассылку!")	

"""Кнопка отписаться от рассылки"""
@dp.message_handler(Text(equals="Отписаться от рассылки"))
async def unsubscribe(message: types.Message):
	#Если пользователя в бд нет, добавляем его с неактивной подпиской
	if (not db.subscriber_exists(message.from_user.id)):
		db.add_subscriber(message.from_user.id)
		await message.answer("Вы не подписаны на рассылку!")
		#Если есть - обновляем статус подписки
	else:
		db.update_subscription(message.from_user.id, False)

		await message.answer("Вы успешно отписались от рассылки!")	


"""Получаем свежую новость о новой закупке"""
@dp.message_handler(Text(equals="Получить информацию о новой закупке"))
async def get_fresh_news(message: types.Message):
	fresh_news = save_fresh_news()

	if (len(fresh_news))>= 1:
		for k, v in sorted(fresh_news.items()):
			news = f"{v['article_title']}\n" \
						 f"{v['article_desc']}\n" \
						 f"{v['article_url']}\n"

				
			await message.answer(news)
		
	else:
		await message.answer("Пока нет новой информации...")

"""Обновление json файла"""
async def update_json_db():
	while True:
		get_first_news() #Просто раз в какое-то кол-во времени получаем список новостей с сайта
		await asyncio.sleep(1800) #Раз в 1800 секунд. В скобках указывать секунды


"""Функция автоматической отправки новостей о новой закупке"""
async def news_every_minute():
	
	while True:
		fresh_news = check_new_updates()
		subscriptions = db.get_subscriptions() #cписок всех подписчиков(их id, user_id, status)
		
		#идентификаторы активных подписчиков(т.е которые подписаны на рассылку)
		subscriptions_user_id = []
		k = 1

		for i in subscriptions:
			subscriptions_user_id.append(i[k])
		

		if (len(fresh_news))>= 1:
			for k, v in sorted(fresh_news.items()):

				news = f"{v['article_title']}\n" \
							 f"{v['article_desc']}\n" \
							 f"{v['article_url']}\n"
				"""Рассылка сообщений активным подписчикам"""
				for user_id in subscriptions_user_id:
					await bot.send_message(user_id, news)
				
			
		else:
			for user_id in subscriptions_user_id:
				await bot.send_message(user_id, "Пока нет новой информации...", disable_notification=True)
			
		await asyncio.sleep(60) #Время отправки сообщений(в секундах)



#Лонг поллинг
if __name__ == '__main__':
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.create_task(news_every_minute())
	loop.create_task(update_json_db())
	executor.start_polling(dp)

