import socket
import threading
import time
import requests
import os
import sys
import subprocess

# Настройки сервера
HOST = '127.0.0.1'
PORT = 55555

# URL для проверки обновлений и кода
UPDATE_URL = "https://raw.githubusercontent.com/xxxbeatiful/chat/main/version.txt"
SCRIPT_URL = "https://raw.githubusercontent.com/xxxbeatiful/chat/main/server.py"
CURRENT_VERSION = "1.0"  # Укажи текущую версию, которая совпадает с version.txt

# Создаем сокет
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = []

# Функция для проверки обновлений
def check_for_updates():
    print("Проверка обновлений...")
    try:
        response = requests.get(UPDATE_URL)
        latest_version = response.text.strip()
        if latest_version != CURRENT_VERSION:
            print(f"Найдено обновление! Текущая версия: {CURRENT_VERSION}, Новая версия: {latest_version}")
            # Скачиваем новый код
            new_code = requests.get(SCRIPT_URL).text
            with open("server.py", "w", encoding="utf-8") as f:
                f.write(new_code)
            print("Код обновлен. Перезапускаем сервер...")
            # Перезапускаем сервер
            subprocess.Popen([sys.executable, "server.py"])
            sys.exit()
        else:
            print("Обновлений не найдено.")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")

# Функция для отправки сообщений всем клиентам
def broadcast(message):
    for client in clients:
        client.send(message)

# Функция для обработки клиента
def handle(client):
    while True:
        try:
            # Получаем сообщение от клиента
            message = client.recv(1024)
            broadcast(message)
        except:
            # Если клиент отключился
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} покинул чат!'.encode('utf-8'))
            usernames.remove(username)
            break

# Функция для принятия новых клиентов
def receive():
    while True:
        client, address = server.accept()
        print(f"Подключился {address}")

        # Запрашиваем имя пользователя
        client.send('NAME'.encode('utf-8'))
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        # Оповещаем всех о новом пользователе
        print(f'Имя пользователя: {username}')
        broadcast(f'{username} присоединился к чату!'.encode('utf-8'))
        client.send('Вы подключены к чату!'.encode('utf-8'))

        # Запускаем поток для обработки клиента
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Функция для периодической проверки обновлений
def update_checker():
    while True:
        check_for_updates()
        time.sleep(3600)  # Проверяем каждые 60 минут

# Запускаем сервер
if __name__ == "__main__":
    print("Сервер запущен...")
    # Запускаем поток для проверки обновлений
    update_thread = threading.Thread(target=update_checker)
    update_thread.start()
    # Запускаем принятие клиентов
    receive()
