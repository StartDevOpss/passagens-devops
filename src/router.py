import os

def get_webhook_url(flight_data):
    # Pega o preço, se não vier nada, assume um valor alto
    price = flight_data.get('price', 99999)
    destination = flight_data.get('destination', '').lower()
    date = flight_data.get('date', '')

    # TESTE DE FORÇA BRUTA: Se o preço for menor que 20.000 (ou seja, quase qualquer voo)
    # ele vai tentar enviar para o Discord.
    
    # 1. Canal #voos-malucos (Preço muito baixo)
    if price < 4000:
        return os.getenv("WEBHOOK_MALUCOS")

    # 2. Canal #datas-especificas
    if "-12-" in date or "-01-" in date:
        return os.getenv("WEBHOOK_DATAS_ESPECIFICAS")

    # 3. Se o destino não for no Brasil (Lógica simples para teste)
    # Se você quiser testar internacional agora, mude para True temporariamente
    is_intl = True 
    
    if is_intl:
        return os.getenv("WEBHOOK_INTERNACIONAL")

    # 4. Canal #brasil
    return os.getenv("WEBHOOK_BRASIL")