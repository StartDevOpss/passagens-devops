import os

def get_webhook_url(flight_data):
    price = flight_data.get('price', 99999)
    is_intl = flight_data.get('international', False)
    destination = flight_data.get('destination', '')

    # 1. Canal #voos-malucos (Erro tarifário ou preço muito baixo)
    if price < 1500 and is_intl:
        return os.getenv("WEBHOOK_MALUCOS")

    # 2. Canal #internacional
    if is_intl:
        return os.getenv("WEBHOOK_INTERNACIONAL")

    # 3. Canal #brasil
    return os.getenv("WEBHOOK_BRASIL")