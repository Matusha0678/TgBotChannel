import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

def reset_webhook():
    """Сброс webhook для освобождения бота"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ Webhook сброшен!")
                print(f"Результат: {data.get('result', 'Unknown')}")
                return True
            else:
                print(f"❌ Ошибка: {data.get('description', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка сброса webhook: {e}")
        return False

def get_webhook_info():
    """Проверка статуса webhook"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                webhook_info = data.get('result', {})
                print("📡 Информация о webhook:")
                print(f"   URL: {webhook_info.get('url', 'Нет')}")
                print(f"   Custom certificate: {webhook_info.get('has_custom_certificate', False)}")
                print(f"   Pending update count: {webhook_info.get('pending_update_count', 0)}")
                print(f"   Last error date: {webhook_info.get('last_error_date', 'Нет')}")
                print(f"   Last error message: {webhook_info.get('last_error_message', 'Нет')}")
                return webhook_info
            else:
                print(f"❌ Ошибка: {data.get('description', 'Unknown')}")
                return None
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка получения информации: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Сброс webhook бота...")
    
    if not BOT_TOKEN:
        print("❌ Токен не найден!")
        exit(1)
    
    print("\n📡 Текущий статус webhook:")
    get_webhook_info()
    
    print("\n🔄 Сброс webhook...")
    if reset_webhook():
        print("\n✅ Бот освобожден для polling!")
        print("Теперь можно запускать бота локально или на Railway")
    else:
        print("\n❌ Не удалось сбросить webhook")
