import sqlite3
import datetime
from typing import Optional, Dict, List

class Database:
    def __init__(self, db_file: str = "penesism_bot.db"):
        self.db_file = db_file
        self.init_database()
    
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
        
        # Таблица сообщений для статистики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица уведомлений о ритуалах
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ritual_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ritual_time TEXT,
                last_sent DATE,
                FOREIGN KEY (ritual_time) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str, first_name: str):
        """Добавление нового пользователя"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def update_message_count(self, user_id: int):
        """Обновление счетчика сообщений пользователя"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Обновляем счетчик сообщений
        cursor.execute('''
            UPDATE users 
            SET message_count = message_count + 1,
                last_message_date = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        
        # Добавляем запись в таблицу сообщений
        cursor.execute('''
            INSERT INTO messages (user_id)
            VALUES (?)
        ''', (user_id,))
        
        # Обновляем ранг пользователя
        self._update_user_rank(cursor, user_id)
        
        conn.commit()
        conn.close()
    
    def _update_user_rank(self, cursor, user_id: int):
        """Обновление ранга пользователя на основе количества сообщений"""
        from config import RANKS
        
        cursor.execute('SELECT message_count FROM users WHERE user_id = ?', (user_id,))
        message_count = cursor.fetchone()[0]
        
        # Определяем новый ранг
        new_rank = 1
        for rank_level, rank_data in sorted(RANKS.items(), reverse=True):
            if message_count >= rank_data["messages_required"]:
                new_rank = rank_level
                break
        
        # Обновляем ранг
        cursor.execute('''
            UPDATE users SET rank = ? WHERE user_id = ?
        ''', (new_rank, user_id))
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
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
            from config import RANKS
            username, first_name, message_count, rank, join_date = result
            return {
                "username": username,
                "first_name": first_name,
                "message_count": message_count,
                "rank": rank,
                "rank_name": RANKS[rank]["name"],
                "next_rank_messages": self._get_next_rank_requirement(rank),
                "join_date": join_date
            }
        return None
    
    def _get_next_rank_requirement(self, current_rank: int) -> Optional[int]:
        """Получение количества сообщений для следующего ранга"""
        from config import RANKS
        
        if current_rank >= max(RANKS.keys()):
            return None
        
        next_rank = current_rank + 1
        return RANKS[next_rank]["messages_required"]
    
    def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Получение топ пользователей по количеству сообщений"""
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
        
        from config import RANKS
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
    
    def get_user_stats(self, user_id: int, days: int = 7) -> Dict:
        """Получение статистики пользователя за последние дни"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        
        cursor.execute('''
            SELECT COUNT(*) FROM messages 
            WHERE user_id = ? AND message_date > ?
        ''', (user_id, date_threshold))
        
        messages_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "messages_last_days": messages_count,
            "daily_average": round(messages_count / days, 1)
        }
    
    def set_ritual_notification_sent(self, ritual_time: str, date: str):
        """Отметка об отправке уведомления о ритуале"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ritual_notifications (ritual_time, last_sent)
            VALUES (?, ?)
        ''', (ritual_time, date))
        
        conn.commit()
        conn.close()
    
    def was_ritual_notification_sent_today(self, ritual_time: str) -> bool:
        """Проверка, было ли уже отправлено уведомление о ритуале сегодня"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        today = datetime.date.today().isoformat()
        
        cursor.execute('''
            SELECT COUNT(*) FROM ritual_notifications 
            WHERE ritual_time = ? AND last_sent = ?
        ''', (ritual_time, today))
        
        result = cursor.fetchone()[0] > 0
        conn.close()
        
        return result
