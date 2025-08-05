#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def testar_api_amil():
    """Testa a API do formulário Amil sem autenticação"""
    try:
        print("🧪 Testando API do Formulário Amil (sem autenticação)...")
        print("=" * 60)
        
        # URL da API
        url = 'http://127.0.0.1:8000/api/amil/'
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição GET
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            # Parsear JSON
            data = response.json()
            
            print(f"✅ API funcionando corretamente!")
            print(f"📈 Total de registros: {data.get('count', 0)}")
            print(f"🎯 Success: {data.get('success', False)}")
            
            if data['success'] and data['count'] > 0:
                print(f"\n🎯 REGISTRO MAIS RECENTE:")
                mais_recente = data['data'][0]
                print(f"   ID: {mais_recente['id']}")
                print(f"   Nome: {mais_recente['nome']}")
                print(f"   CPF: {mais_recente['cpf']}")
                print(f"   Created: {mais_recente.get('created_at', 'N/A')}")
            else:
                print("❌ Nenhum registro encontrado na API")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Servidor Django não está rodando")
        print("💡 Execute: python manage.py runserver")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Servidor demorou muito para responder")
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta")
        print(f"📄 Resposta recebida: {response.text}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def testar_api_porto():
    """Testa a API do formulário Porto sem autenticação"""
    try:
        print("\n🧪 Testando API do Formulário Porto (sem autenticação)...")
        print("=" * 60)
        
        # URL da API
        url = 'http://127.0.0.1:8000/api/porto/'
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição GET
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            # Parsear JSON
            data = response.json()
            
            print(f"✅ API funcionando corretamente!")
            print(f"📈 Total de registros: {data.get('count', 0)}")
            print(f"🎯 Success: {data.get('success', False)}")
            
            if data['success'] and data['count'] > 0:
                print(f"\n🎯 REGISTRO MAIS RECENTE:")
                mais_recente = data['data'][0]
                print(f"   ID: {mais_recente['id']}")
                print(f"   Nome: {mais_recente.get('nomeCompleto', 'N/A')}")
                print(f"   CPF: {mais_recente.get('cpf', 'N/A')}")
            else:
                print("❌ Nenhum registro encontrado na API")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Servidor Django não está rodando")
        print("💡 Execute: python manage.py runserver")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Servidor demorou muito para responder")
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON da resposta")
        print(f"📄 Resposta recebida: {response.text}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def main():
    print("🚀 Testando APIs públicas (sem autenticação)...")
    print("=" * 60)
    
    # Testar API Amil
    testar_api_amil()
    
    # Testar API Porto
    testar_api_porto()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    main() 