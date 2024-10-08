# menu.py

def display_wallets(wallets):
    """
    Отображает список кошельков и возвращает выбор пользователя.
    
    :param wallets: Список кошельков
    :return: Список индексов выбранных кошельков
    """
    print("Доступные кошельки:")
    for i, wallet in enumerate(wallets):
        print(f"{i + 1}. {wallet['address']}")
    
    print("\nВведите номера кошельков через запятую (например, 1, 2, 3), или 'a' для выбора всех:")
    
    user_input = input("Ваш выбор: ").strip()

    # Если пользователь выбрал все кошельки
    if user_input.lower() == 'a':
        return list(range(len(wallets)))

    try:
        # Преобразуем введенные номера в список индексов
        selected_indices = [int(x.strip()) - 1 for x in user_input.split(',') if x.strip().isdigit()]

        # Проверяем, что индексы в допустимом диапазоне
        if all(0 <= idx < len(wallets) for idx in selected_indices):
            return selected_indices
        else:
            print("Ошибка: Ты правда думаешь, что у тебя такая большая ферма?")
            return display_wallets(wallets)

    except ValueError:
        print("Ошибка: Инструкцию читал? Перечитай и сделай нормально")
        return display_wallets(wallets)
    
# menu.py

def display_markets(markets):
    """
    Отображает список маркетов и возвращает выбор пользователя.
    
    :param markets: Список рынков
    :return: Список индексов выбранных рынков
    """
    print("Где ты хочешь лудоманить сегодня?:")
    for i, market in enumerate(markets):
        print(f"{i + 1}. {market['yt_name']} - ${market['yt_price']} (Market Address: {market['market_address']})")
    
    print("\nВведите номера YT через запятую (например, 1, 2, 3), или 'a' для выбора всех:")
    
    user_input = input("Ваш выбор: ").strip()

    # Если пользователь выбрал все рынки
    if user_input.lower() == 'a':
        return list(range(len(markets)))

    try:
        # Преобразуем введенные номера в список индексов
        selected_indices = [int(x.strip()) - 1 for x in user_input.split(',') if x.strip().isdigit()]

        # Проверяем, что индексы в допустимом диапазоне
        if all(0 <= idx < len(markets) for idx in selected_indices):
            return selected_indices
        else:
            print("Ошибка: ты на номера смотрел? Так зачем ты вводишь левые цифры?")
            return display_markets(markets)

    except ValueError:
        print("Ошибка: Инструкцию читал? Перечитай и сделай нормально.")
        return display_markets(markets)

def post_selection_menu():
    """
    Меню после выбора токенов для покупки, предлагает вернуться в меню выбора сети или в главное меню.
    """
    print("\nЧто ты хочешь делать дальше?")
    print("1. Я планирую палить дальше, покажи мне другие сети")
    print("2. Вернуться в главное меню")

    user_input = input("Ваш выбор (1/2): ").strip()

    if user_input == '1':
        return 'network_selection'
    elif user_input == '2':
        return 'main_menu'
    else:
        print("Ошибка: неправильно введен выбор. Попробуй снова.")
        return post_selection_menu()

