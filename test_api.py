"""
Скрипт для тестирования API WhatsApp Bot & CRM Platform
Запуск: python test_api.py
"""
import requests
import json
from datetime import datetime

# Конфигурация
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.ENDC}\n")

# Хранилище токенов
tokens = {
    "access_token": None,
    "refresh_token": None
}

# Хранилище ID созданных объектов
created_ids = {
    "user_id": None,
    "business_id": None,
}

def test_health_check():
    """Тест 1: Проверка здоровья API"""
    print_section("ТЕСТ 1: Health Check")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API доступен: {data.get('status')}")
            print_info(f"Версия: {data.get('version')}")
            print_info(f"Окружение: {data.get('environment')}")
            return True
        else:
            print_error(f"Статус код: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка подключения: {str(e)}")
        return False

def test_register():
    """Тест 2: Регистрация нового пользователя"""
    print_section("ТЕСТ 2: Регистрация пользователя")
    
    timestamp = datetime.now().strftime("%H%M%S")
    test_user = {
        "email": f"test_{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "business_name": f"Test Business {timestamp}"
    }
    
    print_info(f"Email: {test_user['email']}")
    print_info(f"Business: {test_user['business_name']}")
    
    try:
        response = requests.post(f"{API_URL}/auth/register", json=test_user)
        
        if response.status_code == 201:
            data = response.json()
            print_success("Регистрация успешна!")
            print_info(f"User ID: {data.get('id')}")
            print_info(f"Email: {data.get('email')}")
            
            created_ids['user_id'] = data.get('id')
            created_ids['business_id'] = data.get('business_id')
            
            # Сохраняем данные для входа
            test_user['user_id'] = data.get('id')
            return True, test_user
        else:
            print_error(f"Статус код: {response.status_code}")
            print_error(f"Ответ: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Ошибка: {str(e)}")
        return False, None

def test_login(user_data):
    """Тест 3: Вход в систему"""
    print_section("ТЕСТ 3: Вход в систему")
    
    login_data = {
        "username": user_data['email'],
        "password": user_data['password']
    }
    
    print_info(f"Вход как: {login_data['username']}")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            tokens['access_token'] = data.get('access_token')
            tokens['refresh_token'] = data.get('refresh_token')
            
            print_success("Вход выполнен успешно!")
            print_info(f"Access Token: {tokens['access_token'][:50]}...")
            print_info(f"Token Type: {data.get('token_type')}")
            return True
        else:
            print_error(f"Статус код: {response.status_code}")
            print_error(f"Ответ: {response.text}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {str(e)}")
        return False

def test_get_current_user():
    """Тест 4: Получение текущего пользователя"""
    print_section("ТЕСТ 4: Получение данных текущего пользователя")
    
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}"
    }
    
    try:
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Данные получены!")
            print_info(f"ID: {data.get('id')}")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Имя: {data.get('full_name')}")
            print_info(f"Роль: {data.get('role')}")
            print_info(f"Business ID: {data.get('business_id')}")
            return True
        else:
            print_error(f"Статус код: {response.status_code}")
            print_error(f"Ответ: {response.text}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {str(e)}")
        return False

def test_create_bot():
    """Тест 5: Создание бота (должно упасть, т.к. нет WhatsApp номера)"""
    print_section("ТЕСТ 5: Попытка создать бота (ожидается ошибка)")
    
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Content-Type": "application/json"
    }
    
    bot_data = {
        "name": "Test Bot",
        "description": "Тестовый бот для проверки API",
        "whatsapp_number_id": 999,  # Несуществующий ID
        "welcome_message": "Привет! Я тестовый бот.",
        "default_response": "Извините, я не понял ваш вопрос."
    }
    
    print_info(f"Название: {bot_data['name']}")
    
    try:
        response = requests.post(f"{API_URL}/bots/", json=bot_data, headers=headers)
        
        if response.status_code == 404:
            print_success("Правильная ошибка! WhatsApp номер не найден (как и ожидалось)")
            error_data = response.json()
            print_info(f"Сообщение: {error_data.get('detail')}")
            return True
        elif response.status_code == 201:
            print_error("Бот создан, но не должен был! (нет WhatsApp номера)")
            return False
        else:
            print_error(f"Неожиданный статус код: {response.status_code}")
            print_error(f"Ответ: {response.text}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {str(e)}")
        return False

def test_list_bots():
    """Тест 6: Получение списка ботов"""
    print_section("ТЕСТ 6: Получение списка ботов")
    
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}"
    }
    
    try:
        response = requests.get(f"{API_URL}/bots/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Список получен! Количество ботов: {len(data)}")
            
            if len(data) == 0:
                print_info("Список пуст (ожидаемо, т.к. мы не смогли создать бота)")
            else:
                for i, bot in enumerate(data, 1):
                    print_info(f"Бот {i}: {bot.get('name')} (ID: {bot.get('id')})")
            
            return True
        else:
            print_error(f"Статус код: {response.status_code}")
            print_error(f"Ответ: {response.text}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {str(e)}")
        return False

def test_unauthorized_access():
    """Тест 7: Попытка доступа без токена"""
    print_section("ТЕСТ 7: Попытка доступа без авторизации")
    
    try:
        response = requests.get(f"{API_URL}/bots/")
        
        if response.status_code == 401:
            print_success("Правильно! Доступ запрещен без токена")
            error_data = response.json()
            print_info(f"Сообщение: {error_data.get('detail')}")
            return True
        else:
            print_error(f"Неожиданный статус код: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {str(e)}")
        return False

def test_api_docs():
    """Тест 8: Проверка доступности документации"""
    print_section("ТЕСТ 8: Проверка документации API")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        
        if response.status_code == 200:
            print_success("Swagger UI доступен!")
            print_info(f"URL: {BASE_URL}/docs")
            return True
        else:
            print_error(f"Статус код: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {str(e)}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     WhatsApp Bot & CRM Platform - API Testing Suite       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    results = []
    
    # Тест 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Тест 2: Регистрация
    success, user_data = test_register()
    results.append(("Регистрация", success))
    
    if not success:
        print_error("Регистрация не удалась. Остальные тесты пропущены.")
        return
    
    # Тест 3: Вход
    results.append(("Вход в систему", test_login(user_data)))
    
    if not tokens['access_token']:
        print_error("Вход не выполнен. Остальные тесты пропущены.")
        return
    
    # Тест 4: Получение текущего пользователя
    results.append(("Получение профиля", test_get_current_user()))
    
    # Тест 5: Создание бота (ожидается ошибка)
    results.append(("Создание бота", test_create_bot()))
    
    # Тест 6: Список ботов
    results.append(("Список ботов", test_list_bots()))
    
    # Тест 7: Доступ без авторизации
    results.append(("Защита endpoints", test_unauthorized_access()))
    
    # Тест 8: Документация
    results.append(("Документация API", test_api_docs()))
    
    # Итоги
    print_section("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASSED{Colors.ENDC}" if result else f"{Colors.RED}✗ FAILED{Colors.ENDC}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}Итого: {passed}/{total} тестов пройдено{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!{Colors.ENDC}\n")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Некоторые тесты не пройдены{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Тестирование прервано пользователем{Colors.ENDC}")
    except Exception as e:
        print_error(f"Критическая ошибка: {str(e)}")
