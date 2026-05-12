import os
from src.providers.serpapi import buscar_voos_serpapi

def main():
    # Verifica se a variável de ambiente está disponível
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("❌ SERPAPI_KEY não encontrada.")
        return

    print(f"🔑 Usando SERPAPI_KEY: {api_key[:5]}... (ocultado)")

    try:
        # Teste com rota comum (São Paulo → Rio de Janeiro)
        ofertas = buscar_voos_serpapi(origem="GRU", destino="SDU", dias_para_ida=15)

        print(f"📊 API retornou {len(ofertas)} ofertas.")
        for oferta in ofertas:
            print(oferta)

    except Exception as e:
        print(f"❌ Erro ao chamar buscar_voos_serpapi: {e}")

if __name__ == "__main__":
    main()
