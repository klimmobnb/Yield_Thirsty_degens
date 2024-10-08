# wallet.py

from eth_account import Account

def load_wallets(file_path):
    """
    Загружает кошельки на основе приватных ключей из файла.
    
    :param file_path: Путь к файлу с приватными ключами
    :return: Список словарей с адресами и приватными ключами
    """
    wallets = []

    try:
        with open(file_path, 'r') as f:
            keys = f.readlines()
        
        for key in keys:
            key = key.strip()
            if key:
                # Создаем аккаунт на основе приватного ключа
                account = Account.from_key(key)
                wallets.append({
                    'address': account.address,
                    'private_key': key
                })
                
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return None

    except Exception as e:
        print(f"Ошибка при загрузке кошельков: {e}")
        return None
    
    return wallets
