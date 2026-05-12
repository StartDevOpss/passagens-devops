import os
from src.providers.serpapi import buscar_voos_serpapi
from bot import enviar_notificacao_discord, classificar_grupo

def testar_categoria(origem, destino, dias_para_ida):
    print(f"\n🔍 Testando rota {origem} → {destino}...")
    ofertas = buscar_voos_serpapi(origem=origem, destino=destino, dias_para_ida=dias_para_ida)

    if not ofertas:
        print("⚠️ Nenhuma oferta encontrada.")
        return

    for oferta in ofertas:
        grupo = classificar_grupo(oferta)
        print(f"✈️ Oferta: {oferta} | Grupo: {grupo}")

        if isinstance(grupo, list):
            for g in grupo:
                enviar_notificacao_discord(oferta, grupo=g)
        else:
            enviar_notificacao_discord(oferta, grupo=grupo)

def main():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("❌ SERPAPI_KEY não encontrada.")
        return

    print(f"🔑 Usando SERPAPI_KEY: {api_key[:5]}... (ocultado)")

    # Teste Brasil
    testar_categoria("GRU", "SDU", 15)

    # Teste Internacional
    testar_categoria("GRU", "MIA", 20)

    # Teste Voos Malucos
    testar_categoria("GRU", "SDU", 10)

    # Teste Datas Específicas
    testar_categoria("GRU", "CDG", 25)

if __name__ == "__main__":
    main()
