# networks.py

NETWORKS = {
    1: {
        "name": "Ethereum Mainnet",
        "rpc_url": "https://eth.llamarpc.com",
        "gas_limit": 3000000,
        "min_amount": 0.0001,  # минимальная сумма для ETH
        "max_amount": 0.0005   # максимальная сумма для ETH
    },
    56: {
        "name": "Binance Smart Chain",
        "rpc_url": "https://bsc-dataseed.binance.org/",
        "gas_limit": 3000000,
        "min_amount": 0.001,    # минимальная сумма для BNB
        "max_amount": 0.005     # максимальная сумма для BNB
    },
    5000: {
        "name": "Mantle",
        "rpc_url": "https://rpc.mantle.xyz",
        "gas_limit": 30000000,
        "min_amount": 0.1,      # минимальная сумма для MNT
        "max_amount": 0.1       # максимальная сумма для MNT
    },
    42161: {
        "name": "Arbitrum One",
        "rpc_url": "https://arb1.arbitrum.io/rpc",
        "gas_limit": 2000000,
        "min_amount": 0.0001,    # минимальная сумма для Arbitrum
        "max_amount": 0.0005     # максимальная сумма для Arbitrum
    }
}

def get_network_by_chainid(chainid):
    """
    Получает информацию о сети на основе ChainID.

    :param chainid: ChainID сети
    :return: Словарь с информацией о сети или None, если сеть не найдена
    """
    return NETWORKS.get(chainid, None)
