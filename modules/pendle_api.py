# pendle_api.py

from web3 import Web3
from web3.utils.address import to_checksum_address

# pendle_api.py

import requests

def get_pendle_markets(chain_id):
    """
    Выполняет запрос к API Pendle для получения рынков на основе chain_id.
    
    :param chain_id: ChainID выбранной сети
    :return: Отформатированные данные о рынках
    """
    url = f"https://api-v2.pendle.finance/core/v1/{chain_id}/markets"
    params = {
        'order_by': 'name:1',
        'skip': 0,
        'limit': 100,
        'is_expired': 'false',
        'q': 'yt',
        'is_active': 'true'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        markets_data = response.json().get('results', [])
        
        # Форматируем данные о рынках
        formatted_markets = []
        for market in markets_data:
            market_address = market.get('address')
            yt_token = market.get('yt', {}).get('address')
            yt_name = market.get('yt', {}).get('name')
            yt_price = round(market.get('yt', {}).get('price', {}).get('usd', 0), 3)
            
            formatted_markets.append({
                'market_address': market_address,
                'yt_name': yt_name,
                'yt_price': yt_price,
                'yt_token': yt_token
            })
        
        return formatted_markets
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API Pendle: {e}")
        return None

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]

def get_token_balance(web3, wallet_address, token_address):
    """
    Проверяет баланс токена на кошельке.

    :param web3: Инстанс Web3 для подключения к сети.
    :param wallet_address: Адрес кошелька.
    :param token_address: Адрес токена.
    :return: Баланс токена на кошельке.
    """
    try:
        token_contract = web3.eth.contract(address=to_checksum_address(token_address), abi=ERC20_ABI)
        wallet_checksum = to_checksum_address(wallet_address)
        balance = token_contract.functions.balanceOf(wallet_checksum).call()
        return balance
    except Exception as e:
        print(f"Ошибка при проверке баланса токена: {e}")
        return 0

