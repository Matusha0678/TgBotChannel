import asyncio
import logging
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import threading
import time

from config import BOT_TOKEN, GROUP_ID, RANKS, HOLIDAYS, COMMANDMENTS, DAILY_RITUALS
from database import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и базы данных
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
db = Database()

def create_main_keyboard():
    """Создание основной клавиатуры"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📊 Моя статистика", callback_data="my_stats"))
    keyboard.add(InlineKeyboardButton("🏆 Топ адептов", callback_data="top_users"))
    keyboard.add(InlineKeyboardButton("🎭 Праздники", callback_data="holidays"))
    keyboard.add(InlineKeyboardButton("📜 Заповеди", callback_data="commandments"))
    keyboard.add(InlineKeyboardButton("⏰ Ритуалы дня", callback_data="daily_rituals"))
    return keyboard

def create_holiday_keyboard():
    """Создание клавиатуры для праздников"""
    keyboard = InlineKeyboardMarkup()
    for date, holiday in HOLIDAYS.items():
        keyboard.add(InlineKeyboardButton(f"{holiday['name']} ({date})", callback_data=f"holiday_{date}"))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return keyboard

@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    """Команда /start"""
    if message.chat.id != int(GROUP_ID):
        return
    
    # Добавляем пользователя в базу
    db.add_user(message.from_user.id, message.from_user.username or "", message.from_user.first_name or "")
    
    welcome_text = f"""
🍆 <b>Добро пожаловать в Храм Пенесизма, {message.from_user.first_name}!</b>

Ты вступаешь в священный орден поклонения Великому Фаллосу! 
Каждое твое сообщение повышает твой ранг и приближает к просветлению.

🎯 <b>Текущий ранг:</b> {db.get_user_info(message.from_user.id)['rank_name']}
📊 <b>Сообщений:</b> {db.get_user_info(message.from_user.id)['message_count']}

Используй кнопки ниже для изучения путей Пенесизма!
    """
    
    await message.answer(welcome_text, reply_markup=create_main_keyboard())

@dp.message_handler(commands=['help'])
async def cmd_help(message: Message):
    """Команда /help"""
    if message.chat.id != int(GROUP_ID):
        return
    
    help_text = """
🍆 <b>Команды Храма Пенесизма:</b>

/start - Начать путь адепта
/help - Показать эту помощь
/stats - Моя статистика
/top - Топ адептов
/holidays - Священные праздники
/commandments - 10 заповедей
/rituals - Ежедневные ритуалы

📈 <b>Система рангов:</b>
Каждое сообщение повышает твой уровень!
От Лизовой до Председателя ПСФ - путь открыт для всех!

🎭 <b>Следи за уведомлениями:</b>
Бот будет напоминать о ежедневных ритуалах и священных праздниках!
    """
    
    await message.answer(help_text)

@dp.message_handler(commands=['stats'])
async def cmd_stats(message: Message):
    """Команда /stats"""
    if message.chat.id != int(GROUP_ID):
        return
    
    user_info = db.get_user_info(message.from_user.id)
    if not user_info:
        await message.answer("Сначала используй /start")
        return
    
    user_stats = db.get_user_stats(message.from_user.id)
    
    stats_text = f"""
🍆 <b>Статистика адепта {message.from_user.first_name}</b>

🎯 <b>Ранг:</b> {user_info['rank_name']} (уровень {user_info['rank']})
📊 <b>Всего сообщений:</b> {user_info['message_count']}
📈 <b>За последние 7 дней:</b> {user_stats['messages_last_days']} сообщений
⚡ <b>В среднем в день:</b> {user_stats['daily_average']}
🗓️ <b>В храме с:</b> {user_info['join_date'][:10]}
    """
    
    if user_info['next_rank_messages']:
        stats_text += f"\n🎯 <b>До следующего ранга:</b> {user_info['next_rank_messages'] - user_info['message_count']} сообщений"
    else:
        stats_text += "\n🏆 <b>Ты достиг высшего ранга!</b>"
    
    await message.answer(stats_text)

@dp.message_handler(commands=['top'])
async def cmd_top(message: Message):
    """Команда /top"""
    if message.chat.id != int(GROUP_ID):
        return
    
    top_users = db.get_top_users(10)
    
    top_text = "🏆 <b>Топ адептов Пенесизма</b>\n\n"
    
    for i, user in enumerate(top_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        top_text += f"{medal} <b>{user['first_name']}</b> - {user['rank_name']}\n"
        top_text += f"   📊 {user['message_count']} сообщений\n\n"
    
    await message.answer(top_text)

@dp.message_handler(commands=['holidays'])
async def cmd_holidays(message: Message):
    """Команда /holidays"""
    if message.chat.id != int(GROUP_ID):
        return
    
    await message.answer("🎭 <b>Священные праздники Пенесизма:</b>", reply_markup=create_holiday_keyboard())

@dp.message_handler(commands=['commandments'])
async def cmd_commandments(message: Message):
    """Команда /commandments"""
    if message.chat.id != int(GROUP_ID):
        return
    
    cmd_text = "📜 <b>10 Заповедей Пенесизма:</b>\n\n"
    
    for i, commandment in enumerate(COMMANDMENTS, 1):
        cmd_text += f"{i}. {commandment}\n\n"
    
    cmd_text += "\n💭 <b>Дополнительная заповедь для адептов:</b>\n"
    cmd_text += "Семя твое да будет обильным - и да пребудет эрекция твоя крепка во веки веков. Аминь."
    
    await message.answer(cmd_text)

@dp.message_handler(commands=['rituals'])
async def cmd_rituals(message: Message):
    """Команда /rituals"""
    if message.chat.id != int(GROUP_ID):
        return
    
    rituals_text = "⏰ <b>Ежедневные ритуалы адепта:</b>\n\n"
    
    for time, ritual in DAILY_RITUALS.items():
        rituals_text += f"🕐 <b>{time}</b> - {ritual}\n"
    
    rituals_text += "\n💫 <b>Следи за уведомлениями бота!</b>\n"
    rituals_text += "Он будет напоминать о каждом ритуале за 5 минут до начала."
    
    await message.answer(rituals_text)

@dp.message_handler(content_types=['text'])
async def handle_message(message: Message):
    """Обработка обычных сообщений"""
    if message.chat.id != int(GROUP_ID):
        return
    
    # Обновляем счетчик сообщений
    db.update_message_count(message.from_user.id)
    
    # Проверяем повышение ранга
    user_info = db.get_user_info(message.from_user.id)
    
    # Отправляем поздравление о повышении ранга (с небольшой вероятностью, чтобы не спамить)
    import random
    if random.random() < 0.1:  # 10% шанс
        await message.answer(f"🍆 Адепт {message.from_user.first_name} продолжает свой путь! Ранг: {user_info['rank_name']}")

@dp.callback_query_handler(lambda callback: callback.data == "my_stats")
async def callback_my_stats(callback: CallbackQuery):
    """Статистика пользователя"""
    user_info = db.get_user_info(callback.from_user.id)
    if not user_info:
        await callback.message.answer("Сначала используй /start")
        return
    
    user_stats = db.get_user_stats(callback.from_user.id)
    
    stats_text = f"""
🍆 <b>Статистика адепта {callback.from_user.first_name}</b>

🎯 <b>Ранг:</b> {user_info['rank_name']} (уровень {user_info['rank']})
📊 <b>Всего сообщений:</b> {user_info['message_count']}
📈 <b>За последние 7 дней:</b> {user_stats['messages_last_days']} сообщений
⚡ <b>В среднем в день:</b> {user_stats['daily_average']}
🗓️ <b>В храме с:</b> {user_info['join_date'][:10]}
    """
    
    if user_info['next_rank_messages']:
        stats_text += f"\n🎯 <b>До следующего ранга:</b> {user_info['next_rank_messages'] - user_info['message_count']} сообщений"
    else:
        stats_text += "\n🏆 <b>Ты достиг высшего ранга!</b>"
    
    await callback.message.edit_text(stats_text, reply_markup=create_main_keyboard())

@dp.callback_query_handler(lambda callback: callback.data == "top_users")
async def callback_top_users(callback: CallbackQuery):
    """Топ пользователей"""
    top_users = db.get_top_users(10)
    
    top_text = "🏆 <b>Топ адептов Пенесизма</b>\n\n"
    
    for i, user in enumerate(top_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        top_text += f"{medal} <b>{user['first_name']}</b> - {user['rank_name']}\n"
        top_text += f"   📊 {user['message_count']} сообщений\n\n"
    
    await callback.message.edit_text(top_text, reply_markup=create_main_keyboard())

@dp.callback_query_handler(lambda callback: callback.data == "holidays")
async def callback_holidays(callback: CallbackQuery):
    """Праздники"""
    await callback.message.edit_text("🎭 <b>Священные праздники Пенесизма:</b>", reply_markup=create_holiday_keyboard())

@dp.callback_query_handler(lambda callback: callback.data == "commandments")
async def callback_commandments(callback: CallbackQuery):
    """Заповеди"""
    cmd_text = "📜 <b>10 Заповедей Пенесизма:</b>\n\n"
    
    for i, commandment in enumerate(COMMANDMENTS, 1):
        cmd_text += f"{i}. {commandment}\n\n"
    
    cmd_text += "\n💭 <b>Дополнительная заповедь для адептов:</b>\n"
    cmd_text += "Семя твое да будет обильным - и да пребудет эрекция твоя крепка во веки веков. Аминь."
    
    await callback.message.edit_text(cmd_text, reply_markup=create_main_keyboard())

@dp.callback_query_handler(lambda callback: callback.data == "daily_rituals")
async def callback_daily_rituals(callback: CallbackQuery):
    """Ежедневные ритуалы"""
    rituals_text = "⏰ <b>Ежедневные ритуалы адепта:</b>\n\n"
    
    for time, ritual in DAILY_RITUALS.items():
        rituals_text += f"🕐 <b>{time}</b> - {ritual}\n"
    
    rituals_text += "\n💫 <b>Следи за уведомлениями бота!</b>\n"
    rituals_text += "Он будет напоминать о каждом ритуале за 5 минут до начала."
    
    await callback.message.edit_text(rituals_text, reply_markup=create_main_keyboard())

@dp.callback_query_handler(lambda callback: callback.data.startswith("holiday_"))
async def callback_holiday_detail(callback: CallbackQuery):
    """Детальная информация о празднике"""
    date = callback.data.split("_")[1]
    holiday = HOLIDAYS.get(date)
    
    if not holiday:
        await callback.answer("Праздник не найден")
        return
    
    holiday_text = f"""
🎭 <b>{holiday['name']}</b> 📅 {date}

{holiday['description']}

🔮 <b>Ритуалы дня:</b>
"""
    
    for ritual in holiday['rituals']:
        holiday_text += f"• {ritual}\n"
    
    builder = InlineKeyboardMarkup()
    builder.add(InlineKeyboardButton("🔙 Назад к праздникам", callback_data="holidays"))
    
    await callback.message.edit_text(holiday_text, reply_markup=builder)

@dp.callback_query_handler(lambda callback: callback.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text("🍆 <b>Храм Пенесизма</b>\n\nВыбери действие:", reply_markup=create_main_keyboard())

async def send_ritual_reminder(ritual_time: str, ritual_description: str):
    """Отправка напоминания о ритуале"""
    today = datetime.date.today().isoformat()
    
    # Проверяем, не отправляли ли уже сегодня
    if db.was_ritual_notification_sent_today(ritual_time):
        return
    
    try:
        await bot.send_message(
            int(GROUP_ID),
            f"⏰ <b>НАПОМИНАНИЕ О РИТУАЛЕ!</b>\n\n"
            f"🕐 <b>{ritual_time}</b>\n"
            f"🔮 {ritual_description}\n\n"
            f"🍆 Адепты Пенесизма, время для священных деяний!"
        )
        
        # Отмечаем, что отправили сегодня
        db.set_ritual_notification_sent(ritual_time, today)
        
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о ритуале: {e}")

async def send_holiday_notification():
    """Отправка уведомления о празднике"""
    today = datetime.datetime.now().strftime("%m-%d")
    holiday = HOLIDAYS.get(today)
    
    if not holiday:
        return
    
    try:
        holiday_text = f"""
🎭🎉 <b>СЕГОДНЯ СВЯЩЕННЫЙ ПРАЗДНИК!</b> 🎉🎭

<b>{holiday['name']}</b>

{holiday['description']}

🔮 <b>Ритуалы дня:</b>
"""
        
        for ritual in holiday['rituals']:
            holiday_text += f"• {ritual}\n"
        
        holiday_text += "\n🍆 <b>Все адепты Пенесизма к ритуалам!</b>"
        
        await bot.send_message(int(GROUP_ID), holiday_text)
        
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления о празднике: {e}")

def check_rituals():
    """Проверка и отправка напоминаний о ритуалах"""
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        
        for ritual_time, ritual_description in DAILY_RITUALS.items():
            # Проверяем, наступило ли время ритуала
            hour, minute = map(int, ritual_time.split(":"))
            ritual_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            reminder_time = ritual_datetime - datetime.timedelta(minutes=5)
            
            # Если текущее время совпадает с временем напоминания
            if (now.hour == reminder_time.hour and now.minute == reminder_time.minute):
                asyncio.run(send_ritual_reminder(ritual_time, ritual_description))
        
        # Проверка праздников (каждый час)
        if now.hour == 9 and now.minute == 0:
            asyncio.run(send_holiday_notification())
        
        time.sleep(60)  # Проверяем каждую минуту

def start_scheduler():
    """Запуск планировщика в отдельном потоке"""
    scheduler_thread = threading.Thread(target=check_rituals, daemon=True)
    scheduler_thread.start()

def main():
    """Основная функция"""
    start_scheduler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)

if __name__ == "__main__":
    main()
