#!/usr/bin/env python3
"""
Тестовый скрипт для SMS-аутентификации
Используйте для проверки API endpoints
"""

import requests
import json

# Конфигурация
BASE_URL = "http://localhost:5000/api"
TEST_PHONE = "+77019990438"

def test_request_code():
    """Тест запроса SMS кода"""
    print("🔐 Тестирование запроса SMS кода...")
    
    url = f"{BASE_URL}/sms-auth/request-code"
    data = {"phone_number": TEST_PHONE}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Успешно!")
            print(f"Сообщение: {result.get('message')}")
            print(f"Номер: {result.get('phone_number')}")
            print(f"Новый пользователь: {result.get('is_new_user')}")
            
            if result.get('test_mode'):
                print(f"🔐 ТЕСТОВЫЙ РЕЖИМ - Код: {result.get('code')}")
            
            return result.get('code')
        else:
            print("❌ Ошибка!")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None

def test_verify_code(phone, code):
    """Тест проверки SMS кода"""
    print(f"\n🔐 Тестирование проверки кода {code}...")
    
    url = f"{BASE_URL}/sms-auth/verify-code"
    data = {
        "phone_number": phone,
        "verification_code": code
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Успешно!")
            print(f"Сообщение: {result.get('message')}")
            print(f"Новый пользователь: {result.get('is_new_user')}")
            print(f"Access Token: {result.get('access_token')[:20]}...")
            print(f"Refresh Token: {result.get('refresh_token')[:20]}...")
            return result.get('access_token')
        else:
            print("❌ Ошибка!")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None

def test_resend_code():
    """Тест повторной отправки SMS кода"""
    print(f"\n🔐 Тестирование повторной отправки SMS...")
    
    url = f"{BASE_URL}/sms-auth/resend-code"
    data = {"phone_number": TEST_PHONE}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Успешно!")
            print(f"Сообщение: {result.get('message')}")
            
            if result.get('test_mode'):
                print(f"🔐 ТЕСТОВЫЙ РЕЖИМ - Новый код: {result.get('code')}")
            
            return result.get('code')
        else:
            print("❌ Ошибка!")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование SMS-аутентификации")
    print("=" * 50)
    
    # 1. Запрос кода
    code = test_request_code()
    if not code:
        print("❌ Не удалось получить код. Завершение теста.")
        return
    
    # 2. Проверка кода
    token = test_verify_code(TEST_PHONE, code)
    if not token:
        print("❌ Не удалось проверить код. Завершение теста.")
        return
    
    # 3. Тест повторной отправки (должен показать ошибку rate limiting)
    print("\n⏳ Ждем 2 секунды перед тестом повторной отправки...")
    import time
    time.sleep(2)
    
    new_code = test_resend_code()
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")
    
    if token:
        print("✅ Аутентификация прошла успешно!")
        print(f"🔑 Токен: {token[:30]}...")
    else:
        print("❌ Аутентификация не удалась")

if __name__ == "__main__":
    main()

