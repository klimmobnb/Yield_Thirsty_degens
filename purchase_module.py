import random
import time
import json
import requests
from web3 import Web3
import logging
from modules.networks import get_network_by_chainid

# Устанавливаем максимальную цену газа для Ethereum (в Gwei)
MAX_GAS_PRICE_ETH = Web3.to_wei(5, 'gwei')  # Лимит на 5 Gwei

gas_retry_delay = 60  # Время ожидания 1 минута
# Настройка логирования
logging.basicConfig(filename='transaction_log.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Модуль свапов запущен.")

logging.debug(f"MAX_GAS_PRICE_ETH установлена на {MAX_GAS_PRICE_ETH} Wei.")

# Загрузка задач из файла
def load_tasks(filename):
    try:
        logging.debug(f"Загрузка задач из файла: {filename}")
        with open(filename, 'r') as f:
            tasks = json.load(f)
            logging.debug(f"Задачи успешно загружены: {tasks}")
            return tasks
    except FileNotFoundError:
        logging.error(f"Файл {filename} не найден.")
        return None

# Сохранение обновленных задач в файл
def save_tasks(tasks, filename):
    with open(filename, 'w') as f:
        json.dump(tasks, f, indent=4)

# Загрузка приватных ключей из файла wallets.txt
def load_private_keys(filename):
    private_keys = {}
    try:
        logging.debug(f"Загрузка приватных ключей из файла: {filename}")
        with open(filename, 'r') as f:
            for line in f:
                private_key = line.strip()
                account = Web3().eth.account.from_key(private_key)  # Создаем экземпляр Web3 для работы с приватным ключом
                wallet_address = account.address
                private_keys[wallet_address] = private_key
                logging.debug(f"Приватный ключ загружен для адреса: {wallet_address}")
        return private_keys
    except FileNotFoundError:
        logging.error(f"Файл {filename} не найден.")
        return None
    except Exception as e:
        logging.error(f"Ошибка при загрузке приватных ключей: {e}")
        return None

# Выполнение свапа через API Pendle
def execute_swap(chain_id, market_address, wallet_address, yt_token, swap_amount, web3, private_key, gas_limit):
    logging.info(f"Начало выполнения свапа для кошелька {wallet_address}, ChainID: {chain_id}, Сумма свапа: {swap_amount}")
    
    tx = {}
    amount_in_wei = int(swap_amount * 1e18)
    logging.debug(f"Сумма свапа в Wei: {amount_in_wei}")

    url = f"https://api-v2.pendle.finance/core/v1/sdk/{chain_id}/markets/{market_address}/swap"
    params = {
        "receiver": wallet_address,
        "slippage": 0.002,
        "enableAggregator": "true",
        "tokenIn": "0x0000000000000000000000000000000000000000",  # Нативный токен
        "tokenOut": yt_token,
        "amountIn": amount_in_wei
    }

    logging.debug(f"Отправляем запрос к API Pendle: URL: {url}, Параметры: {json.dumps(params, indent=4)}")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        swap_data = response.json()
        logging.debug(f"Получен ответ от Pendle API: {json.dumps(swap_data, indent=4)}")

        tx_data = swap_data['tx']
        gas_price = web3.eth.gas_price
        logging.debug(f"Текущая цена газа: {gas_price} Wei")

        if chain_id == 1 and gas_price > MAX_GAS_PRICE_ETH:
            logging.warning(f"Цена газа {web3.from_wei(gas_price, 'gwei')} Gwei превышает лимит.")
            print(f"Цена газа {web3.from_wei(gas_price, 'gwei')} Gwei превышает лимит.")
            return False

        tx_value = int(tx_data['value'])
        tx = {
            'to': tx_data['to'],
            'value': tx_value,
            'data': tx_data['data'],
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': web3.eth.get_transaction_count(wallet_address),
            'chainId': chain_id
        }

        logging.debug(f"Параметры транзакции перед подписанием: {json.dumps(tx, indent=4)}")

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        logging.debug(f"Транзакция подписана.")

        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logging.info(f"Транзакция отправлена! Хэш: {web3.to_hex(tx_hash)}")
        print(f"Транзакция отправлена! Хэш: {web3.to_hex(tx_hash)}")
        return True

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP ошибка при свапе: {http_err}")
        print(f"HTTP ошибка при свапе: {http_err}")
        return False
    except Exception as err:
        logging.error(f"Ошибка при свапе: {err}")
        print(f"Ошибка при свапе: {err}")
        return False

# Запуск процесса свапов
def start_purchase_process():
    logging.info("Запуск процесса выполнения свапов.")
    
    private_keys = load_private_keys('wallets.txt')
    if not private_keys:
        logging.error("Нет загруженных приватных ключей. Завершение работы.")
        print("Нет загруженных приватных ключей. Завершение работы.")
        return

    min_delay = float(input("Введите минимальную задержку между транзакциями (в секундах): "))
    max_delay = float(input("Введите максимальную задержку между транзакциями (в секундах): "))
    logging.debug(f"Минимальная задержка: {min_delay}, Максимальная задержка: {max_delay}")
    
    while True:
        tasks = load_tasks('tasks.json')
        if not tasks:
            logging.info("Нет оставшихся задач. Все задачи выполнены.")
            print("Нет оставшихся задач. Все задачи выполнены.")
            break  # Выход из цикла если нет задач

        for task in tasks[:]:  # Итерируем копию списка задач
            wallet_address = task['wallet_address']
            market_address = task['market_address']
            yt_token = task['yt_token']
            chain_id = task['chain_id']

            logging.debug(f"Начало выполнения задачи для кошелька {wallet_address}, ChainID {chain_id}.")
            print(f"Начало выполнения задачи для кошелька {wallet_address}, ChainID {chain_id}.")

            if wallet_address not in private_keys:
                logging.warning(f"Приватный ключ для кошелька {wallet_address} не найден. Пропуск задачи.")
                print(f"Приватный ключ для кошелька {wallet_address} не найден. Пропуск задачи.")
                continue

            private_key = private_keys[wallet_address]
            network = get_network_by_chainid(chain_id)

            if not network:
                logging.error(f"Неизвестная сеть с ChainID: {chain_id}. Пропуск задачи.")
                print(f"Неизвестная сеть с ChainID: {chain_id}. Пропуск задачи.")
                continue

            rpc_url = network['rpc_url']
            gas_limit = network['gas_limit']

            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if not web3.is_connected():
                logging.error(f"Ошибка подключения к сети {network['name']} с ChainID {chain_id}. Пропуск.")
                print(f"Ошибка подключения к сети {network['name']} с ChainID {chain_id}. Пропуск.")
                continue

            # Проверка цены газа перед проверкой баланса
            gas_price = web3.eth.gas_price
            if chain_id == 1 and gas_price > MAX_GAS_PRICE_ETH:
                logging.warning(f"Цена газа {web3.from_wei(gas_price, 'gwei')} Gwei превышает лимит.")
                print(f"Цена газа {web3.from_wei(gas_price, 'gwei')} Gwei превышает лимит. Пропуск задачи.")
                time.sleep(gas_retry_delay)
                continue

            min_amount = network.get('min_amount', 0.0)
            max_amount = network.get('max_amount', 0.0)
            if min_amount == 0 and max_amount == 0:
                logging.warning(f"Пропуск сети {network['name']} с ChainID {chain_id} из-за неизвестных параметров.")
                print(f"Пропуск сети {network['name']} с ChainID {chain_id} из-за неизвестных параметров.")
                continue

            # Определение суммы свапа
            swap_amount = random.uniform(min_amount, max_amount)
            logging.info(f"Свапаем {swap_amount} нативного токена для YT токена {yt_token} на маркете {market_address}.")
            print(f"Свапаем {swap_amount} нативного токена для YT токена {yt_token}")

            # Проверка баланса перед выполнением транзакции
            balance = web3.eth.get_balance(wallet_address)
            required = int(swap_amount * 1e18) + (gas_limit * gas_price)
            if balance < required:
                logging.error(f"Недостаточно средств на кошельке {wallet_address}. Баланс: {balance}, требуется: {required}")
                print(f"Недостаточно средств на кошельке {wallet_address}. Баланс: {balance}, требуется: {required}")
                continue

            # Выполнение свапа
            success = execute_swap(chain_id, market_address, wallet_address, yt_token, swap_amount, web3, private_key, gas_limit)
            if success:
                logging.info(f"Транзакция успешно выполнена для {wallet_address}. Удаление задачи из очереди.")
                print(f"Транзакция успешно выполнена для {wallet_address}. Удаление задачи из очереди.")
                tasks.remove(task)  # Удаление выполненной задачи
                save_tasks(tasks, 'tasks.json')  # Сохранение обновленного списка задач

if __name__ == "__main__":
    start_purchase_process()
