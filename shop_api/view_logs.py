# view_logs.py
import os
import sys


def view_logs():
    """Просмотр логов приложения"""
    log_dir = 'logs'
    
    if not os.path.exists(log_dir):
        print("❌ Папка с логами не найдена")
        return
    
    files = {
        'shop_api.log': '📋 Все действия',
        'errors.log': '❌ Только ошибки',
        'auth.log': '🔐 Авторизация',
        'requests.log': '🌐 HTTP запросы'
    }
    
    print("\n" + "=" * 60)
    print("📊 ПОСЛЕДНИЕ СОБЫТИЯ ИЗ ЛОГОВ")
    print("=" * 60)
    
    for filename, description in files.items():
        filepath = os.path.join(log_dir, filename)
        if os.path.exists(filepath):
            print(f"\n📄 {description} ({filename}):")
            print("-" * 40)
            with open(filepath, 'r', encoding='utf-8') as f:
                # Показываем последние 5 строк
                lines = f.readlines()
                for line in lines[-5:]:
                    print(line.strip())
        else:
            print(f"\n⚠️ Файл {filename} еще не создан")


def watch_logs():
    """Режим наблюдения за логами (Ctrl+C для выхода)"""
    import time
    
    log_file = 'logs/shop_api.log'
    if not os.path.exists(log_file):
        print(f"❌ Файл {log_file} не найден")
        return
    
    print("\n🔍 Режим наблюдения за логами (Ctrl+C для выхода)")
    print("=" * 60)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        # Переходим в конец файла
        f.seek(0, 2)
        
        try:
            while True:
                line = f.readline()
                if line:
                    print(line.strip())
                else:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n👋 Выход из режима наблюдения")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'watch':
        watch_logs()
    else:
        view_logs()