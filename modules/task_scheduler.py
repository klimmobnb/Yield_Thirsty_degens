import json
import os
import random

TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            try:
                tasks = json.load(f)
                # Проверяем структуру каждой задачи
                if not all(['wallet_address' in task and 'yt_token' in task and 'chain_id' in task for task in tasks]):
                    print("Ошибка: Структура задач в файле tasks.json неверная.")
                    return []
                return tasks
            except json.JSONDecodeError:
                print("Ошибка: Невозможно декодировать tasks.json.")
                return []
    return []

def save_tasks(tasks):
    # Перемешиваем задачи
    random.shuffle(tasks)
    
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def task_exists(wallet_address, yt_token, chain_id):
    tasks = load_tasks()
    for task in tasks:
        if task['wallet_address'] == wallet_address and task['yt_token'] == yt_token and task['chain_id'] == chain_id:
            return True
    return False

def add_task(wallet_address, selected_markets, network, chain_id):
    tasks = load_tasks()
    
    for market in selected_markets:
        yt_token = market['yt_token']
        if not task_exists(wallet_address, yt_token, chain_id):
            task = {
                "wallet_address": wallet_address,
                "yt_token": yt_token,
                "market_address": market['market_address'],
                "chain_id": chain_id
            }
            tasks.append(task)
            print(f"Добавлена новая задача для покупки YT токена {yt_token} на кошельке {wallet_address}.")
        else:
            print(f"Задача для покупки YT токена {yt_token} на кошельке {wallet_address} уже существует.")
    
    # Сохраняем задачи и перемешиваем их
    save_tasks(tasks)

def schedule_tasks(selected_wallets, selected_markets, selected_network, selected_chainid):
    for wallet in selected_wallets:
        wallet_address = wallet['address']
        print(f"Планируем задачи для кошелька {wallet_address} в сети {selected_network['name']}...")
        add_task(wallet_address, selected_markets, selected_network, selected_chainid)
