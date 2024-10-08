from modules.wallet import load_wallets
from modules.menu import display_wallets, display_markets, post_selection_menu
from modules.networks import get_network_by_chainid
from modules.pendle_api import get_pendle_markets, get_token_balance
from modules.task_scheduler import schedule_tasks
from purchase_module import start_purchase_process  # Представьте, что модуль покупки реализован здесь
from web3 import Web3

def main():
    print("Lets burn some money!")
    
    print("Выберите действие:")
    print("1. Запланировать задачи")
    print("2. Начать покупку")
    
    choice = int(input("Введите номер опции: "))
    
    if choice == 1:
        # Запуск планировщика задач
        plan_tasks()
    elif choice == 2:
        # Запуск процесса покупки
        start_purchase_process()
    else:
        print("Тут всего две цифры, и из этих двух цифр ты не смог выбрать правильную")
        main()

def plan_tasks():
    # Список поддерживаемых ChainID
    supported_chainids = [1, 56, 5000, 42161]
    
    print("Выберите сеть для работы:")
    for i, chainid in enumerate(supported_chainids):
        network = get_network_by_chainid(chainid)
        print(f"{i + 1}. {network['name']} (ChainID: {chainid})")
    
    network_choice = int(input("Введите номер сети: ")) - 1
    selected_chainid = supported_chainids[network_choice]
    selected_network = get_network_by_chainid(selected_chainid)
    
    print(f"Вы выбрали сеть: {selected_network['name']} (ChainID: {selected_chainid})")
    rpc_url = selected_network['rpc_url']
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # Загрузка кошельков из файла wallets.txt
    wallets = load_wallets('wallets.txt')
    if not wallets:
        print("Ошибка: не удалось загрузить кошельки.")
        return
    
    # Отображение меню для выбора кошельков
    selected_indices = display_wallets(wallets)
    selected_wallets = [wallets[i] for i in selected_indices]

    print(f"Вы выбрали {len(selected_wallets)} кошельков:")
    for wallet in selected_wallets:
        print(f"{wallet['address']}")

    # Выполнение запроса к API Pendle на основе выбранного chain_id
    markets = get_pendle_markets(selected_chainid)
    if markets:
        print("Получены данные о рынках:")
        selected_market_indices = display_markets(markets)
        selected_markets = [markets[i] for i in selected_market_indices]
        
        print("Проверка наличия YT токенов на кошельках...")
        # Сопоставляем кошельки с токенами
        all_tasks = []
        for wallet in selected_wallets:
            purchase_list = []
            wallet_address = wallet['address']
            for market in selected_markets:
                yt_token = market['yt_token']
                yt_name = market['yt_name']
                
                # Проверяем баланс YT токена на кошельке
                balance = get_token_balance(web3, wallet_address, yt_token)
                if balance == 0:
                    purchase_list.append(market)
                else:
                    print(f"YT токен {yt_name} уже есть на кошельке {wallet_address}")
            
            if purchase_list:
                print(f"\nДля кошелька {wallet_address} нужно купить следующие YT токены:")
                for item in purchase_list:
                    print(f"YT Token: {item['yt_name']}")
                all_tasks.append((wallet_address, purchase_list, selected_network, selected_chainid))
            else:
                print(f"\nНа кошельке {wallet_address} уже есть все выбранные YT токены.")
        
        # Запланировать задачи
        if all_tasks:
            schedule_tasks(selected_wallets, selected_markets, selected_network, selected_chainid)
    
        # После планирования задач предлагаем выбор
        next_action = post_selection_menu()  # Вызов меню с выбором действий
        
        if next_action == 'network_selection':
            plan_tasks()  # Возврат в меню выбора сети
        elif next_action == 'main_menu':
            main()  # Возврат в главное меню
    else:
        print("Не удалось получить данные о рынках.")

if __name__ == "__main__":
    main()
