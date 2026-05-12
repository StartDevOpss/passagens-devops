import os

def get_webhook_url(flight_data):
    price = flight_data.get('price', 99999)
    is_intl = flight_data.get('international', False)
    destination = flight_data.get('destination', '')
    date = flight_data.get('date', '') # A data que aparece como '2026-10-15'

    # 1. Canal #voos-malucos (Erro tarifário ou preço muito baixo)
    if price < 10000 and is_intl:
        return os.getenv("WEBHOOK_MALUCOS")

    # 2. NOVO: Canal #datas-especificas (Exemplo: Filtro para Dezembro/Janeiro ou feriados)
    # Se a data contiver "-12-" (dezembro) ou "-01-" (janeiro)
    if "-12-" in date or "-01-" in date:
        return os.getenv("WEBHOOK_DATAS_ESPECIFICAS")

    # 3. Canal #internacional
    if is_intl:
        return os.getenv("WEBHOOK_INTERNACIONAL")

    # 4. Canal #brasil
    return os.getenv("WEBHOOK_BRASIL")