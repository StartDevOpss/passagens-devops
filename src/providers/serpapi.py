import requests
import os
from datetime import datetime, timedelta

def buscar_voos_serpapi(origem):
    # Datas dinâmicas (ex: daqui a 30 dias)
    data_ida = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    params = {
        "engine": "google_flights",
        "departure_id": origem,
        "currency": "BRL",
        "api_key": os.getenv("SERPAPI_KEY")
    }
    
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=20)
        dados = r.json()
        
        vool_encontrados = []
        # Normaliza os dados da SerpAPI para o formato do nosso bot
        for voo in dados.get("best_flights", []):
            vool_encontrados.append({
                "origem": origem,
                "preco": voo.get("price"),
                "internacional": True if voo.get("price", 0) > 2000 else False # Exemplo de lógica
            })
        return vool_encontrados
    except Exception as e:
        return []