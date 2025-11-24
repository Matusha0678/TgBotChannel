import requests
import threading
import time
import datetime
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Ранги и их требования в сообщениях
RANKS = {
    1: {"name": "Лизовой", "messages_required": 0},
    2: {"name": "Кунимен", "messages_required": 50},
    3: {"name": "ЧленоСосатель", "messages_required": 150},
    4: {"name": "ТестостерованнаяЯзва", "messages_required": 300},
    5: {"name": "Страж Пениса", "messages_required": 500},
    6: {"name": "Мудрец Пениссизма", "messages_required": 750},
    7: {"name": "Председатель ПСФ", "messages_required": 1000}
}

# 13 священных праздников пенесизма
HOLIDAYS = {
    "12-01": {
        "name": "Конец NNN",
        "description": "Главный праздник массового семяизвержения",
        "rituals": [
            "23:59 - Построение у гигантского фаллоса",
            "00:00 - Одновременная мастурбация",
            "00:01 - Коллективный крик 'СВОБОДА!'",
            "00:05 - Освящение первого семени",
            "00:30 - Начало оргий",
            "До утра - Непрерывные сексуальные практики"
        ]
    },
    "20-03": {
        "name": "Эрекционное равноденствие",
        "description": "Весеннее пробуждение сексуальной энергии",
        "rituals": [
            "Утром - Ритуалы оплодотворения земли семенем",
            "Днем - Танцы с расписными фаллосами на полях",
            "Вечером - Эрекционная медитация"
        ]
    },
    "03-04": {
        "name": "День Тройного Проникновения",
        "description": "Праздник в честь 9-й заповеди",
        "rituals": [
            "Утром - Подготовка к ритуалам",
            "Днем - Групповые ритуалы с участием трех партнеров",
            "Вечером - Соревнования по выносливости"
        ]
    },
    "15-05": {
        "name": "Фестиваль Священной Смазки",
        "description": "Освящение масел и лубрикантов",
        "rituals": [
            "Утром - Освящение масел и лубрикантов",
            "Днем - Ритуальные обливания смазкой",
            "Вечером - Соревнования по скольжению на членах"
        ]
    },
    "21-06": {
        "name": "Летнее семяизвержение",
        "description": "Самый длинный день - самый длинный акт",
        "rituals": [
            "На рассвете - Массовая мастурбация на восходе солнца",
            "Днем - Сбор семени для ритуальных целей",
            "Вечером - Непрерывные сексуальные практики"
        ]
    },
    "12-07": {
        "name": "День Вагины",
        "description": "Поклонение священному входу",
        "rituals": [
            "Утром - Ритуальные оральные службы",
            "Днем - Изготовление вагинальных амулетов",
            "Вечером - Поклонение священному входу"
        ]
    },
    "02-08": {
        "name": "Праздник Ануса",
        "description": "Почитание заднего входа",
        "rituals": [
            "Утром - Анальные медитации",
            "Днем - Ритуальные клизмы очищения",
            "Вечером - Почитание заднего входа"
        ]
    },
    "01-09": {
        "name": "Фаллический новый год",
        "description": "Начало церковного года пенесизма",
        "rituals": [
            "Утром - Освящение новых секс-игрушек",
            "Днем - Ритуалы повышения потенции",
            "Вечером - Фаллические празднования"
        ]
    },
    "15-10": {
        "name": "День Согласия",
        "description": "Праздник добровольности",
        "rituals": [
            "Утром - Обучение искусству соблазнения",
            "Днем - Подписание сексуальных контрактов",
            "Вечером - Праздник добровольности"
        ]
    },
    "31-10": {
        "name": "Ночь Множественных Оргазмов",
        "description": "Сексуальные шабаши",
        "rituals": [
            "Вечером - Сексуальные шабаши",
            "Ночью - Ритуалы продления оргазма",
            "До утра - Соревнования по количеству кульминаций"
        ]
    },
    "01-11": {
        "name": "День Безопасного Секса",
        "description": "Начало NNN как испытания веры",
        "rituals": [
            "Утром - Освящение презервативов",
            "Днем - Ритуалы защиты от ЗППП",
            "Вечером - Начало NNN как испытания веры"
        ]
    },
    "17-11": {
        "name": "Праздник Священной Простаты",
        "description": "Мужское здоровье и удовольствие",
        "rituals": [
            "Утром - Массажные ритуалы",
            "Днем - Медитации на точку G",
            "Вечером - Праздник мужского здоровья"
        ]
    },
    "25-12": {
        "name": "День Зачатия",
        "description": "Символическое рождение нового культа",
        "rituals": [
            "Утром - Ритуалы плодородия",
            "Днем - Обмен сексуальными подарками",
            "Вечером - Символическое рождение нового культа"
        ]
    }
}

# 10 заповедей пенесизма
COMMANDMENTS = [
    "Да не будет у тебя других богов перед Пенисом - лишь фаллос истинный владыка твой",
    "Не сотвори себе кумира из импотентов - ибо лишь стоящий член достоин поклонения",
    "Поминай день совокупления - шесть дней работай, седьмой - посвяти непрерывной ебле",
    "Почитай вагину и анус - как священные врата в царствие пенесное",
    "Не воздерживайся - ибо отказ от плоти есть смертный грех",
    "Не прелюбодействуй без согласия - но всякое согласное соитие есть благо",
    "Не опускай член брата твоего - поддерживай стоячих духом и плотью",
    "Не произноси имени Пениса всуе - лишь в момент наивысшего наслаждения",
    "Не желай жены ближнего - но если желаешь, предложи тройное проникновение",
    "Возлюби вагину ближнего - как святыню, требующую регулярного окропления"
]

# Ежедневные ритуалы
DAILY_RITUALS = {
    "07:00": "Утренняя эрекция (обязательная)",
    "12:00": "Полуденная мастурбация",
    "18:00": "Групповая медитация",
    "00:00": "Ночное совокупление"
}

class SimpleBot:
    def __init__(self):
        self.token = BOT_TOKEN
        self.group_id = GROUP_ID
        self.db_file = "penesism_bot.db"
        self.init_database()
        self.last_update_id = 0
        
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                message_count INTEGER DEFAULT 0,
                rank INTEGER DEFAULT 1,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_message_date DATETIME
            )
        ''')
        
        # Таблица сообщений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица уведомлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ritual_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ritual_time TEXT,
                last_sent DATE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Отправка сообщения"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
            return None
    
    def add_user(self, user_id, username, first_name):
        """Добавление пользователя"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def update_message_count(self, user_id):
        """Обновление счетчика сообщений"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET message_count = message_count + 1,
                last_message_date = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        
        cursor.execute('''
            INSERT INTO messages (user_id)
            VALUES (?)
        ''', (user_id,))
        
        # Обновляем ранг
        cursor.execute('SELECT message_count FROM users WHERE user_id = ?', (user_id,))
        message_count = cursor.fetchone()[0]
        
        new_rank = 1
        for rank_level, rank_data in sorted(RANKS.items(), reverse=True):
            if message_count >= rank_data["messages_required"]:
                new_rank = rank_level
                break
        
        cursor.execute('UPDATE users SET rank = ? WHERE user_id = ?', (new_rank, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_info(self, user_id):
        """Получение информации о пользователе"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, first_name, message_count, rank, join_date
            FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            username, first_name, message_count, rank, join_date = result
            next_rank = None
            if rank < max(RANKS.keys()):
                next_rank = RANKS[rank + 1]["messages_required"]
            
            return {
                "username": username,
                "first_name": first_name,
                "message_count": message_count,
                "rank": rank,
                "rank_name": RANKS[rank]["name"],
                "next_rank_messages": next_rank,
                "join_date": join_date
            }
        return None
    
    def get_top_users(self, limit=10):
        """Получение топ пользователей"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, first_name, message_count, rank
            FROM users
            ORDER BY message_count DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        users = []
        for username, first_name, message_count, rank in results:
            users.append({
                "username": username,
                "first_name": first_name,
                "message_count": message_count,
                "rank": rank,
                "rank_name": RANKS[rank]["name"]
            })
        
        return users
    
    def get_updates(self):
        """Получение обновлений"""
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {'offset': self.last_update_id + 1, 'timeout': 30}
        
        try:
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get('ok'):
                updates = data.get('result', [])
                for update in updates:
                    self.last_update_id = update['update_id']
                return updates
        except Exception as e:
            print(f"Ошибка получения обновлений: {e}")
        
        return []
    
    def handle_message(self, message):
        """Обработка сообщения"""
        if message.get('chat', {}).get('id') != int(self.group_id):
            return
        
        if 'text' not in message:
            return
        
        user = message.get('from', {})
        user_id = user.get('id')
        text = message['text']
        
        if not user_id:
            return
        
        # Добавляем пользователя
        self.add_user(user_id, user.get('username', ''), user.get('first_name', ''))
        
        # Обрабатываем команды
        if text.startswith('/'):
            self.handle_command(message, text, user)
        else:
            # Обновляем счетчик сообщений
            self.update_message_count(user_id)
            
            # Иногда показываем ранг
            import random
            if random.random() < 0.1:
                user_info = self.get_user_info(user_id)
                if user_info:
                    self.send_message(
                        int(self.group_id),
                        f"🍆 Адепт {user_info['first_name']} продолжает свой путь! Ранг: {user_info['rank_name']}"
                    )
    
    def handle_command(self, message, text, user):
        """Обработка команд"""
        user_id = user['id']
        command = text.lower()
        
        if command == '/start':
            self.add_user(user_id, user.get('username', ''), user.get('first_name', ''))
            user_info = self.get_user_info(user_id)
            
            welcome_text = f"""
🍆 <b>Добро пожаловать в Храм Пенесизма, {user['first_name']}!</b>

Ты вступаешь в священный орден поклонения Великому Фаллосу! 
Каждое твое сообщение повышает твой ранг и приближает к просветлению.

🎯 <b>Текущий ранг:</b> {user_info['rank_name']}
📊 <b>Сообщений:</b> {user_info['message_count']}

<b>Доступные команды:</b>
/start - Начать путь адепта
/stats - Моя статистика
/top - Топ адептов
/holidays - Священные праздники
/commandments - 10 заповедей
/rituals - Ежедневные ритуалы
/help - Помощь
            """
            
            self.send_message(int(self.group_id), welcome_text)
            
        elif command == '/help':
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
            """
            
            self.send_message(int(self.group_id), help_text)
            
        elif command == '/stats':
            user_info = self.get_user_info(user_id)
            if not user_info:
                self.send_message(int(self.group_id), "Сначала используй /start")
                return
            
            stats_text = f"""
🍆 <b>Статистика адепта {user['first_name']}</b>

🎯 <b>Ранг:</b> {user_info['rank_name']} (уровень {user_info['rank']})
📊 <b>Всего сообщений:</b> {user_info['message_count']}
🗓️ <b>В храме с:</b> {user_info['join_date'][:10]}
            """
            
            if user_info['next_rank_messages']:
                stats_text += f"\n🎯 <b>До следующего ранга:</b> {user_info['next_rank_messages'] - user_info['message_count']} сообщений"
            else:
                stats_text += "\n🏆 <b>Ты достиг высшего ранга!</b>"
            
            self.send_message(int(self.group_id), stats_text)
            
        elif command == '/top':
            top_users = self.get_top_users(10)
            
            top_text = "🏆 <b>Топ адептов Пенесизма</b>\n\n"
            
            for i, user in enumerate(top_users, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                top_text += f"{medal} <b>{user['first_name']}</b> - {user['rank_name']}\n"
                top_text += f"   📊 {user['message_count']} сообщений\n\n"
            
            self.send_message(int(self.group_id), top_text)
            
        elif command == '/holidays':
            holidays_text = "🎭 <b>Священные праздники Пенесизма:</b>\n\n"
            
            for date, holiday in HOLIDAYS.items():
                holidays_text += f"📅 <b>{date}</b> - {holiday['name']}\n"
                holidays_text += f"   {holiday['description']}\n\n"
            
            self.send_message(int(self.group_id), holidays_text)
            
        elif command == '/commandments':
            cmd_text = "📜 <b>10 Заповедей Пенесизма:</b>\n\n"
            
            for i, commandment in enumerate(COMMANDMENTS, 1):
                cmd_text += f"{i}. {commandment}\n\n"
            
            cmd_text += "\n💭 <b>Дополнительная заповедь для адептов:</b>\n"
            cmd_text += "Семя твое да будет обильным - и да пребудет эрекция твоя крепка во веки веков. Аминь."
            
            self.send_message(int(self.group_id), cmd_text)
            
        elif command == '/rituals':
            rituals_text = "⏰ <b>Ежедневные ритуалы адепта:</b>\n\n"
            
            for time, ritual in DAILY_RITUALS.items():
                rituals_text += f"🕐 <b>{time}</b> - {ritual}\n"
            
            rituals_text += "\n💫 <b>Следи за уведомлениями бота!</b>\n"
            rituals_text += "Он будет напоминать о каждом ритуале за 5 минут до начала."
            
            self.send_message(int(self.group_id), rituals_text)
    
    def check_rituals(self):
        """Проверка ритуалов"""
        while True:
            try:
                now = datetime.datetime.now()
                
                # Проверка ритуалов
                for ritual_time, ritual_description in DAILY_RITUALS.items():
                    hour, minute = map(int, ritual_time.split(":"))
                    ritual_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    reminder_time = ritual_datetime - datetime.timedelta(minutes=5)
                    
                    if (now.hour == reminder_time.hour and now.minute == reminder_time.minute):
                        self.send_message(
                            int(self.group_id),
                            f"⏰ <b>НАПОМИНАНИЕ О РИТУАЛЕ!</b>\n\n"
                            f"🕐 <b>{ritual_time}</b>\n"
                            f"🔮 {ritual_description}\n\n"
                            f"🍆 Адепты Пенесизма, время для священных деяний!"
                        )
                
                # Проверка праздников
                if now.hour == 9 and now.minute == 0:
                    today = now.strftime("%m-%d")
                    holiday = HOLIDAYS.get(today)
                    
                    if holiday:
                        holiday_text = f"""
🎭🎉 <b>СЕГОДНЯ СВЯЩЕННЫЙ ПРАЗДНИК!</b> 🎉🎭

<b>{holiday['name']}</b>

{holiday['description']}

🔮 <b>Ритуалы дня:</b>
"""
                        
                        for ritual in holiday['rituals']:
                            holiday_text += f"• {ritual}\n"
                        
                        holiday_text += "\n🍆 <b>Все адепты Пенесизма к ритуалам!</b>"
                        
                        self.send_message(int(self.group_id), holiday_text)
                
                time.sleep(60)  # Проверяем каждую минуту
                
            except Exception as e:
                print(f"Ошибка в проверке ритуалов: {e}")
                time.sleep(60)
    
    def run(self):
        """Запуск бота"""
        print("🍆 Бот Храма Пенесизма запускается...")
        
        # Запуск потока для проверки ритуалов
        ritual_thread = threading.Thread(target=self.check_rituals, daemon=True)
        ritual_thread.start()
        
        # Основной цикл обработки сообщений
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    if 'message' in update:
                        self.handle_message(update['message'])
                    elif 'callback_query' in update:
                        # Для простоты игнорируем callback запросы
                        pass
                
                time.sleep(1)  # Небольшая задержка между запросами
                
            except KeyboardInterrupt:
                print("\n🍆 Бот останавливается...")
                break
            except Exception as e:
                print(f"Ошибка в основном цикле: {e}")
                time.sleep(5)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ Ошибка: Не настроен BOT_TOKEN в файле .env")
        print("Пожалуйста, укажите правильное значение в файле .env")
    elif GROUP_ID == "your_group_id_here":
        print("⚠️ Внимание: GROUP_ID не настроен")
        print("Бот запустится, но будет работать только после добавления в группу и указания ID")
        print()
        bot = SimpleBot()
        bot.run()
    else:
        bot = SimpleBot()
        bot.run()
