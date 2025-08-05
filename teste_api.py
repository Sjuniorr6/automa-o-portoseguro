import requests
import json

def testar_api():
    try:
        print("Testando API da Amil...")
        response = requests.get('http://127.0.0.1:8000/api/amil/')
        
        print(f"Status Code: {response.status_code}")
        print(f"URL acessada: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta da API: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data['success'] and data['count'] > 0:
                print(f"✅ API funcionando! Encontrados {data['count']} registros")
                return True
            else:
                print("⚠️ API funcionando, mas nenhum registro encontrado")
                return False
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

if __name__ == "__main__":
    testar_api() 