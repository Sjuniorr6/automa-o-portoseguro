import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import json
from datetime import datetime

def buscar_dados_formulario():
    """
    Busca os dados do formulário Amil da API
    """
    try:
        print("Buscando dados do formulário na API...")
        response = requests.get('http://127.0.0.1:8000/api/amil/')
        
        print(f"Status da API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total de registros na API: {data.get('count', 0)}")
            
            if data['success'] and data['count'] > 0:
                # Listar todos os registros para debug
                print("📋 Listando todos os registros:")
                for i, registro in enumerate(data['data']):
                    print(f"  [{i}] ID: {registro['id']} - Nome: {registro['nome']} - Created: {registro.get('created_at', 'N/A')}")
                
                # Pega o PRIMEIRO registro (mais recente) - primeiro da lista
                formulario = data['data'][0]  # Mudança aqui: [0] pega o primeiro elemento (mais recente)
                print(f"✅ PRIMEIRO REGISTRO SELECIONADO (MAIS RECENTE):")
                print(f"   ID: {formulario['id']}")
                print(f"   Nome: {formulario['nome']}")
                print(f"   CPF: {formulario['cpf']}")
                print(f"   Created: {formulario.get('created_at', 'N/A')}")
                return formulario
            else:
                print("❌ Nenhum formulário encontrado na API")
                return None
        else:
            print(f"❌ Erro ao buscar dados: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return None

def preencher_formulario_dinamico(driver, wait, dados):
    """
    Preenche o formulário com os dados da API
    """
    try:
        print("🎯 Iniciando preenchimento dinâmico do formulário...")
        print(f"📋 Dados recebidos da API: {dados}")
        
        # Aguardar mais tempo para o formulário carregar completamente
        print("⏳ Aguardando carregamento completo do formulário...")
        time.sleep(5)
        
        # Função melhorada para encontrar campos por múltiplos métodos (rápida)
        def encontrar_campo_flexivel(nome_campo, placeholders=None, name_contains=None, max_tentativas=2):
            print(f"🔍 Procurando campo {nome_campo}...")
            
            for tentativa in range(max_tentativas):
                try:
                    # 1. Tentar por name exato (rápido)
                    try:
                        campo = driver.find_element(By.XPATH, f"//input[@name='{nome_campo}']")
                        if campo.is_displayed() and campo.is_enabled():
                            print(f"✅ Campo {nome_campo} encontrado por name exato")
                            return campo
                    except:
                        pass
                    
                    # 2. Tentar por name contendo (rápido)
                    if name_contains:
                        try:
                            campo = driver.find_element(By.XPATH, f"//input[contains(@name, '{name_contains}')]")
                            if campo.is_displayed() and campo.is_enabled():
                                print(f"✅ Campo {nome_campo} encontrado por name contendo")
                                return campo
                        except:
                            pass
                    
                    # 3. Tentar por placeholder (rápido)
                    if placeholders:
                        for placeholder in placeholders:
                            try:
                                campo = driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}']")
                                if campo.is_displayed() and campo.is_enabled():
                                    print(f"✅ Campo {nome_campo} encontrado por placeholder: {placeholder}")
                                    return campo
                            except:
                                continue
                    
                    # 4. Tentar por label (múltiplas variações) - rápido
                    label_variations = [
                        f"//label[contains(text(), '{nome_campo}')]/following-sibling::input",
                        f"//label[contains(text(), '{nome_campo.lower()}')]/following-sibling::input",
                        f"//label[contains(text(), '{nome_campo.upper()}')]/following-sibling::input",
                        f"//label[contains(translate(text(), 'ÁÀÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßáàâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ', 'AAAAAAACEEEEIIIIDNOOOOOOUUUUYBsaaaaaaaceeeeiiiidnoooooouuuuyby'), '{nome_campo.lower()}')]/following-sibling::input"
                    ]
                    
                    for label_xpath in label_variations:
                        try:
                            campo = driver.find_element(By.XPATH, label_xpath)
                            if campo.is_displayed() and campo.is_enabled():
                                print(f"✅ Campo {nome_campo} encontrado por label")
                                return campo
                        except:
                            continue
                    
                    # 5. Tentar por ID (rápido)
                    try:
                        campo = driver.find_element(By.ID, nome_campo.lower().replace(' ', '_'))
                        if campo.is_displayed() and campo.is_enabled():
                            print(f"✅ Campo {nome_campo} encontrado por ID")
                            return campo
                    except:
                        pass
                    
                    # 6. Tentar por input genérico (último recurso) - rápido
                    inputs = driver.find_elements(By.TAG_NAME, "input")
                    for input_field in inputs:
                        if input_field.is_displayed() and input_field.is_enabled():
                            print(f"✅ Campo {nome_campo} encontrado por input genérico")
                            return input_field
                    
                    time.sleep(0.5)  # Reduzido para 0.5 segundos
                except Exception as e:
                    print(f"❌ Tentativa {tentativa + 1} falhou: {e}")
                    time.sleep(0.5)  # Reduzido para 0.5 segundos
            
            print(f"❌ Campo {nome_campo} não encontrado após {max_tentativas} tentativas")
            return None
        
        # Função específica para encontrar campos de data (rápida e eficiente)
        def encontrar_campo_data(nome_campo, max_tentativas=1):
            print(f"📅 Procurando campo de data: {nome_campo}...")
            
            for tentativa in range(max_tentativas):
                try:
                    # Várias variações de placeholders para datas
                    date_placeholders = [
                        'dd/mm/aaaa', 'DD/MM/AAAA', 'dd/mm/yyyy', 'DD/MM/YYYY',
                        'Data', 'data', 'DATE', 'date'
                    ]
                    
                    # Várias variações de names para datas
                    date_names = [
                        nome_campo.lower(), nome_campo.upper(), 
                        nome_campo.lower().replace(' ', '_'),
                        nome_campo.lower().replace(' ', ''),
                        'data', 'date'
                    ]
                    
                    # Tentar por placeholder (rápido)
                    for placeholder in date_placeholders:
                        try:
                            campo = driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}']")
                            if campo.is_displayed() and campo.is_enabled():
                                print(f"✅ Campo de data {nome_campo} encontrado por placeholder: {placeholder}")
                                return campo
                        except:
                            continue
                    
                    # Tentar por name (rápido)
                    for name in date_names:
                        try:
                            campo = driver.find_element(By.XPATH, f"//input[contains(@name, '{name}')]")
                            if campo.is_displayed() and campo.is_enabled():
                                print(f"✅ Campo de data {nome_campo} encontrado por name: {name}")
                                return campo
                        except:
                            continue
                    
                    # Tentar por label (rápido)
                    label_variations = [
                        f"//label[contains(text(), '{nome_campo}')]/following-sibling::input",
                        f"//label[contains(text(), 'Data')]/following-sibling::input",
                        f"//label[contains(text(), 'data')]/following-sibling::input"
                    ]
                    
                    for label_xpath in label_variations:
                        try:
                            campo = driver.find_element(By.XPATH, label_xpath)
                            if campo.is_displayed() and campo.is_enabled():
                                print(f"✅ Campo de data {nome_campo} encontrado por label")
                                return campo
                        except:
                            continue
                    
                    # Tentar buscar por qualquer input que pareça ser de data
                    try:
                        inputs = driver.find_elements(By.TAG_NAME, "input")
                        for input_field in inputs:
                            if input_field.is_displayed() and input_field.is_enabled():
                                placeholder = input_field.get_attribute('placeholder') or ''
                                name = input_field.get_attribute('name') or ''
                                if any(word in placeholder.lower() or word in name.lower() for word in ['data', 'date', 'dd/mm']):
                                    print(f"✅ Campo de data {nome_campo} encontrado por busca genérica")
                                    return input_field
                    except:
                        pass
                    
                except Exception as e:
                    print(f"❌ Tentativa {tentativa + 1} para campo de data falhou: {e}")
            
            print(f"❌ Campo de data {nome_campo} não encontrado - pulando...")
            return None
        
        # Função auxiliar para tentar diferentes métodos de localização (mantida para compatibilidade)
        def encontrar_campo_texto(placeholders, name_contains=None, max_tentativas=3):
            for tentativa in range(max_tentativas):
                try:
                    # Tentar por placeholder
                    for placeholder in placeholders:
                        try:
                            campo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@placeholder='{placeholder}']")))
                            return campo
                        except:
                            continue
                    
                    # Tentar por name se especificado
                    if name_contains:
                        try:
                            campo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[contains(@name, '{name_contains}')]")))
                            return campo
                        except:
                            pass
                    
                    # Tentar por input genérico
                    inputs = driver.find_elements(By.TAG_NAME, "input")
                    for input_field in inputs:
                        if input_field.is_displayed() and input_field.is_enabled():
                            return input_field
                    
                    time.sleep(1)
                except:
                    time.sleep(1)
            return None
        
        # Função específica para encontrar campos por name exato
        def encontrar_campo_por_name(name_exato):
            try:
                campo = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@name='{name_exato}']")))
                return campo
            except:
                return None
        
        # 1. NOME - usando name exato encontrado no formulário
        if dados.get('nome'):
            try:
                nome_field = driver.find_element(By.XPATH, "//input[@name='beneficiaryOwner.nome']")
                if nome_field:
                    nome_field.click()
                    time.sleep(1)
                    nome_field.clear()
                    time.sleep(1)
                    nome_field.send_keys(dados['nome'])
                    print(f"✅ Nome preenchido: {dados['nome']}")
                    time.sleep(2)
                else:
                    print("❌ Campo nome não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher nome: {e}")
        
        # 2. CPF - usando name exato encontrado no formulário
        if dados.get('cpf'):
            try:
                cpf_field = driver.find_element(By.XPATH, "//input[@name='beneficiaryOwner.cpf']")
                if cpf_field:
                    cpf_field.click()
                    time.sleep(1)
                    cpf_field.clear()
                    time.sleep(1)
                    cpf_field.send_keys(dados['cpf'])
                    print(f"✅ CPF preenchido: {dados['cpf']}")
                    time.sleep(2)
                else:
                    print("❌ Campo CPF não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher CPF: {e}")
        
        # 3. NOME NO CARTÃO - usando name exato encontrado no formulário
        if dados.get('nome_cartao'):
            try:
                cartao_field = driver.find_element(By.XPATH, "//input[@name='beneficiaryOwner.nomeCartao']")
                if cartao_field:
                    cartao_field.click()
                    time.sleep(1)
                    cartao_field.clear()
                    time.sleep(1)
                    cartao_field.send_keys(dados['nome_cartao'])
                    print(f"✅ Nome no cartão preenchido: {dados['nome_cartao']}")
                    time.sleep(2)
                else:
                    print("❌ Campo nome no cartão não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher nome no cartão: {e}")
        
        # 4. DATA DE INCLUSÃO - PULANDO (já preenchida automaticamente pelo sistema)
        print("⚠️ Data de inclusão já preenchida automaticamente pelo sistema - pulando")
        
        # 5. DATA DE REGISTRO - PULANDO (já preenchida automaticamente pelo sistema)
        print("⚠️ Data de registro já preenchida automaticamente pelo sistema - pulando")
        
        # 6. DATA DE NASCIMENTO - usando XPath específico fornecido
        if dados.get('data_nascimento'):
            try:
                data_nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').strftime('%d/%m/%Y')
                # Usar o XPath específico fornecido
                nascimento_field = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/form/fieldset/div[1]/div[2]/div/div[4]/div[3]/div/div/div[1]/input')
                if nascimento_field:
                    nascimento_field.click()
                    time.sleep(1)
                    nascimento_field.clear()
                    time.sleep(1)
                    nascimento_field.send_keys(data_nascimento)
                    print(f"✅ Data de nascimento preenchida: {data_nascimento}")
                    time.sleep(2)
                else:
                    print("❌ Campo data de nascimento não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher data de nascimento: {e}")
        
        # 7. SEXO - usando método flexível
        if dados.get('sexo'):
            try:
                print("🔍 Procurando campo Sexo...")
                if dados['sexo'] == 'M':
                    sexo_masculino = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='M']")))
                    sexo_masculino.click()
                    print("✅ Sexo selecionado: Masculino")
                    time.sleep(2)
                elif dados['sexo'] == 'F':
                    sexo_feminino = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='F']")))
                    sexo_feminino.click()
                    print("✅ Sexo selecionado: Feminino")
                    time.sleep(2)
            except Exception as e:
                print(f"❌ Erro ao selecionar sexo: {e}")
        
        # 8. NACIONALIDADE - usando método flexível
        if dados.get('nacionalidade'):
            try:
                print("🔍 Procurando campo Nacionalidade...")
                if dados['nacionalidade'] == 'B':
                    nacionalidade_brasileiro = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='B']")))
                    nacionalidade_brasileiro.click()
                    print("✅ Nacionalidade selecionada: Brasileiro")
                    time.sleep(2)
                elif dados['nacionalidade'] == 'E':
                    nacionalidade_estrangeiro = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='E']")))
                    nacionalidade_estrangeiro.click()
                    print("✅ Nacionalidade selecionada: Estrangeiro")
                    time.sleep(2)
            except Exception as e:
                print(f"❌ Erro ao selecionar nacionalidade: {e}")
        
        # 9. NOME DA MÃE - usando name exato encontrado no formulário
        if dados.get('nome_mae'):
            try:
                mae_field = driver.find_element(By.XPATH, "//input[@name='beneficiaryOwner.nomeMae']")
                if mae_field:
                    mae_field.click()
                    time.sleep(1)
                    mae_field.clear()
                    time.sleep(1)
                    mae_field.send_keys(dados['nome_mae'])
                    print(f"✅ Nome da mãe preenchido: {dados['nome_mae']}")
                    time.sleep(2)
                else:
                    print("❌ Campo nome da mãe não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher nome da mãe: {e}")
        
        # 10. NOME DO PAI (opcional) - usando name exato encontrado no formulário
        if dados.get('nome_pai'):
            try:
                pai_field = driver.find_element(By.XPATH, "//input[@name='beneficiaryOwner.nomePai']")
                if pai_field:
                    pai_field.click()
                    time.sleep(1)
                    pai_field.clear()
                    time.sleep(1)
                    pai_field.send_keys(dados['nome_pai'])
                    print(f"✅ Nome do pai preenchido: {dados['nome_pai']}")
                    time.sleep(2)
                else:
                    print("❌ Campo nome do pai não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher nome do pai: {e}")
        
        print("🎉 Campos essenciais preenchidos com sucesso!")
        print("🛑 Automação finalizada - navegador será mantido aberto")
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Erro geral ao preencher formulário: {e}")

def click_menu_element(driver, wait):
    """
    Clica no elemento do menu especificado
    """
    try:
        print("Procurando elemento do menu...")
        menu_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[2]/nav/div/ul/div[4]/div[1]')))
        print("Elemento do menu encontrado!")
        
        # Clicar no elemento
        menu_element.click()
        print("Elemento do menu clicado com sucesso!")
        
        incluir_titulares = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[2]/nav/div/ul/div[4]/div[2]/ul/div/div[1]/a')))
        incluir_titulares.click()
        print("Incluir titulares clicado com sucesso!")

        time.sleep(2)
        #aqui <<<
        # Lidar com popup que pode aparecer após clicar em incluir titulares
        try:
            # Aguardar um pouco para popup aparecer
            time.sleep(2)
            
            # Clicar no botão Ok do popup usando o XPath específico
            try:
                ok_button = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div/div/div[3]/div/button')
                ok_button.click()
                print("Botão Ok clicado com sucesso!")
                time.sleep(1)
            except Exception as e:
                print(f"Erro ao clicar no botão Ok: {e}")
                # Tentar método alternativo se o XPath específico falhar
                try:
                    ok_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ok') or contains(text(), 'OK')]")
                    ok_button.click()
                    print("Botão Ok clicado usando método alternativo!")
                    time.sleep(1)
                except:
                    print("Não foi possível encontrar o botão Ok")
                
        except Exception as e:
            print(f"Erro ao lidar com popup: {e}")

        # Aguardar um pouco para a ação ser processada
        time.sleep(2)
        
        # Clicar no seletor de contrato
        clicar_seletor_contrato(driver, wait)
        
        # Clicar na opção de contrato da lista
        clicar_opcao_contrato(driver, wait)
        
        # Buscar dados da API e preencher formulário dinamicamente
        dados_formulario = buscar_dados_formulario()
        if dados_formulario:
            # Capturar screenshot para debug
            try:
                screenshot_path = f"screenshots/formulario_amil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot salvo: {screenshot_path}")
            except Exception as e:
                print(f"❌ Erro ao salvar screenshot: {e}")
            
            # Debug: listar todos os campos de input
            try:
                print("🔍 Listando campos de input encontrados:")
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for i, input_field in enumerate(inputs):
                    if input_field.is_displayed():
                        placeholder = input_field.get_attribute('placeholder') or 'Sem placeholder'
                        name = input_field.get_attribute('name') or 'Sem name'
                        id_attr = input_field.get_attribute('id') or 'Sem id'
                        type_attr = input_field.get_attribute('type') or 'Sem type'
                        print(f"  Campo {i+1}: type='{type_attr}', placeholder='{placeholder}', name='{name}', id='{id_attr}'")
                
                # Listar também labels para identificar campos
                print("🔍 Listando labels encontrados:")
                labels = driver.find_elements(By.TAG_NAME, "label")
                for i, label in enumerate(labels):
                    if label.is_displayed():
                        text = label.text.strip()
                        if text:
                            print(f"  Label {i+1}: '{text}'")
            except Exception as e:
                print(f"❌ Erro ao listar campos: {e}")
            
            preencher_formulario_dinamico(driver, wait, dados_formulario)
        else:
            print("❌ Nenhum dado encontrado na API para preencher o formulário")
            print("❌ Automação cancelada - sem dados disponíveis")
        
    except Exception as e:
        print(f"Erro ao clicar no elemento do menu: {e}")
        print("Tentando métodos alternativos...")
        
        try:
            # Tentar encontrar por outros seletores
            menu_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'nav')]//div")
            for element in menu_elements:
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print("Elemento clicado usando método alternativo!")
                    break
        except Exception as e2:
            print(f"Erro ao tentar métodos alternativos: {e2}")

def handle_popups(driver):
    """
    Função para lidar com popups que podem aparecer
    """
    try:
        # Aguardar um pouco para popups aparecerem
        time.sleep(2)
        
        # Tentar aceitar cookies se aparecer
        try:
            cookie_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Aceitar') or contains(text(), 'Accept') or contains(text(), 'OK') or contains(text(), 'Entendi')]")
            cookie_button.click()
            print("Popup de cookies aceito!")
            time.sleep(1)
        except:
            pass
        
        # Tentar fechar popups de notificação
        try:
            close_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='Close'] | //button[contains(@class, 'close')] | //span[contains(@class, 'close')] | //div[contains(@class, 'close')]")
            for button in close_buttons:
                if button.is_displayed():
                    button.click()
                    print("Popup fechado!")
                    time.sleep(1)
        except:
            pass
        
        # Tentar aceitar termos se aparecer
        try:
            terms_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Concordo') or contains(text(), 'Aceito') or contains(text(), 'Continuar')]")
            terms_button.click()
            print("Termos aceitos!")
            time.sleep(1)
        except:
            pass
            
    except Exception as e:
        print(f"Erro ao lidar com popups: {e}")

def clicar_seletor_contrato(driver, wait):
    """
    Clica no seletor de contrato
    """
    try:
        print("Procurando seletor de contrato...")
        seletor_contrato = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rw_8_input"]/div[1]/div')))
        print("Seletor de contrato encontrado!")
        
        # Clicar no elemento
        
        seletor_contrato.click()
        print("Seletor de contrato clicado com sucesso!")
        
        # Aguardar um pouco para a ação ser processada
        time.sleep(2)
        
    except Exception as e:
        print(f"Erro ao clicar no seletor de contrato: {e}")
        print("Tentando métodos alternativos...")
        
        try:
            # Tentar encontrar por outros seletores
            seletor_alternativo = driver.find_element(By.XPATH, "//div[contains(@id, 'rw_8_input')]//div")
            seletor_alternativo.click()
            print("Seletor clicado usando método alternativo!")
            time.sleep(2)
        except Exception as e2:
            print(f"Erro ao tentar métodos alternativos: {e2}")

def clicar_opcao_contrato(driver, wait):
    """
    Clica na opção de contrato da lista
    """
    try:
        print("Procurando opção de contrato na lista...")
        opcao_contrato = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rw_8_listbox_active_option"]')))
        print("Opção de contrato encontrada!")
        
        # Clicar no elemento
        opcao_contrato.click()
        print("Opção de contrato clicada com sucesso!")
        
        # Aguardar um pouco para a ação ser processada
        time.sleep(2)
        
    except Exception as e:
        print(f"Erro ao clicar na opção de contrato: {e}")
        print("Tentando métodos alternativos...")
        
        try:
            # Tentar encontrar por outros seletores
            opcao_alternativa = driver.find_element(By.XPATH, "//div[contains(@id, 'rw_8_listbox')]//div[contains(@class, 'active')]")
            opcao_alternativa.click()
            print("Opção clicada usando método alternativo!")
            time.sleep(2)
        except Exception as e2:
            print(f"Erro ao tentar métodos alternativos: {e2}")

def open_amil_website():
    """
    Abre o site da Amil no navegador, clica no campo de login e insere o código
    """
    try:
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Maximizar janela
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Evitar detecção
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Configurar o driver com webdriver-manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Executar script para evitar detecção
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navegar para o site da Amil
        print("Abrindo site da Amil...")
        driver.get("https://www.amil.com.br/empresa/#/login")
        
        # Aguardar a página carregar
        wait = WebDriverWait(driver, 15)
        
        try:
            # Aguardar até que a página esteja carregada
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("Site da Amil aberto com sucesso!")
            
            # Aguardar um pouco para a página carregar completamente
            time.sleep(3)
            
            #aqui <<<
            # Lidar com popups que podem aparecer
            handle_popups(driver)
            
            # Tentar encontrar o campo de login usando o XPath fornecido
            try:
                login_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]/div/div/section/section/form/div/div[1]/div/div/div/div/input')))
                print("Campo de login encontrado!")
                
                # Clicar no campo
                login_field.click()
                time.sleep(1)
                
                # Limpar o campo e inserir o código
                login_field.clear()
                login_field.send_keys("G2517723")
                print("Código G2517723 inserido com sucesso!")
                
                # Aguardar um pouco para visualizar
                time.sleep(2)
                
                senha_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]/div/div/section/section/form/div/div[2]/div[1]/div/div/div/div/input')))
                senha_field.click()
                senha_field.send_keys('Netza240@')
                
                entrar_buton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]/div/div/section/section/form/div/div[3]/div[1]/div/div/button')))
                entrar_buton.click()
                print("Login realizado com sucesso!")
                time.sleep(5)  # Aguardar mais tempo para a página carregar após login
                
                # Lidar com popups após login
                handle_popups(driver)
                
                # Após o login, clicar no elemento do menu
                click_menu_element(driver, wait)
                
            except Exception as e:
                print(f"Erro ao encontrar ou preencher o campo de login: {e}")
                print("Tentando métodos alternativos...")
                
                # Tentar encontrar por outros seletores
                try:
                    # Tentar por ID
                    login_field = driver.find_element(By.ID, "login")
                    login_field.click()
                    login_field.send_keys("G2517723")
                    print("Código inserido usando método alternativo!")
                except:
                    try:
                        # Tentar por input genérico
                        inputs = driver.find_elements(By.TAG_NAME, "input")
                        for input_field in inputs:
                            if input_field.is_displayed() and input_field.is_enabled():
                                input_field.click()
                                input_field.send_keys("G2517723")
                                print("Código inserido usando input genérico!")
                                break
                    except Exception as e2:
                        print(f"Erro ao tentar métodos alternativos: {e2}")
            
            # Manter o navegador aberto
            print("Navegador será mantido aberto. Feche manualmente quando necessário.")
            print("🛑 Automação finalizada - aguardando fechamento manual do navegador...")
            while True:
                try:
                    # Verificar se o navegador ainda está aberto
                    driver.current_url
                    time.sleep(10)  # Verificar a cada 10 segundos
                except:
                    print("Navegador foi fechado.")
                    break
                    
        except Exception as e:
            print(f"Erro ao carregar a página: {e}")
            driver.quit()
            
    except Exception as e:
        print(f"Erro ao abrir o navegador: {e}")

def start_amil_automation():
    """
    Inicia a automação em uma thread separada para não bloquear o Django
    """
    thread = threading.Thread(target=open_amil_website, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # Teste direto
    start_amil_automation() 