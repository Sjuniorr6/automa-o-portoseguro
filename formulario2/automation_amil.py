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
        
        if response.status_code == 200:
            data = response.json()
            if data['success'] and data['count'] > 0:
                # Pega o último registro (mais recente) - último da lista
                formulario = data['data'][-1]  # Mudança aqui: [-1] pega o último elemento
                print(f"Dados encontrados para: {formulario['nome']}")
                print(f"ID do registro: {formulario['id']}")
                return formulario
            else:
                print("Nenhum formulário encontrado na API")
                return None
        else:
            print(f"Erro ao buscar dados: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")
        print("Usando dados de teste...")
        
        # Dados de teste baseados no JSON fornecido
        dados_teste = {
            'id': 1,
            'nome': 'SIDNEI APARECIDO DOS SANTOS JUNIOR',
            'cpf': '422.357.688-73',
            'nome_cartao': 'SIDNEI APARECIDO DOS SANTOS JUNIOR',
            'data_inclusao': '1993-06-12',
            'data_registro': '1993-06-12',
            'data_nascimento': '1993-06-12',
            'sexo': 'M',
            'nacionalidade': 'B',
            'nome_mae': 'ana caroline alves',
            'nome_pai': 'ana caroline alves',
            'estado_civil': 'C',
            'plano': 'TESTE',
            'contrato_dental': 'TESTE',
            'plano_dental': 'TESTE',
            'created_at': '2025-08-05 16:00:13',
            'updated_at': '2025-08-05 16:00:13'
        }
        
        print(f"Dados de teste carregados para: {dados_teste['nome']}")
        return dados_teste

def preencher_formulario_dinamico(driver, wait, dados):
    """
    Preenche o formulário com os dados da API
    """
    try:
        print("Preenchendo formulário com dados da API...")
        print(f"Dados recebidos: {dados}")
        
        # Aguardar mais tempo para o formulário carregar completamente
        time.sleep(5)
        
        # Função auxiliar para tentar diferentes métodos de localização
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
        
        # 1. NOME
        if dados.get('nome'):
            try:
                print("🔍 Procurando campo Nome...")
                nome_field = encontrar_campo_texto(['Nome completo', 'Nome', 'Nome do titular'])
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
        
        # 2. CPF
        if dados.get('cpf'):
            try:
                print("🔍 Procurando campo CPF...")
                cpf_field = encontrar_campo_texto(['999.999.999-99', 'CPF', 'cpf'])
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
        
        # 3. NOME NO CARTÃO
        if dados.get('nome_cartao'):
            try:
                print("🔍 Procurando campo Nome no cartão...")
                cartao_field = encontrar_campo_texto(['Nome no cartão', 'cartão', 'Nome cartão'])
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
        
        # 4. DATA DE INCLUSÃO
        if dados.get('data_inclusao'):
            try:
                print("🔍 Procurando campo Data de inclusão...")
                data_inclusao = datetime.strptime(dados['data_inclusao'], '%Y-%m-%d').strftime('%d/%m/%Y')
                inclusao_field = encontrar_campo_texto(['dd/mm/aaaa'], 'inclusao')
                if inclusao_field:
                    inclusao_field.click()
                    time.sleep(1)
                    inclusao_field.clear()
                    time.sleep(1)
                    inclusao_field.send_keys(data_inclusao)
                    print(f"✅ Data de inclusão preenchida: {data_inclusao}")
                    time.sleep(2)
                else:
                    print("❌ Campo data de inclusão não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher data de inclusão: {e}")
        
        # 5. DATA DE REGISTRO
        if dados.get('data_registro'):
            try:
                print("🔍 Procurando campo Data de registro...")
                data_registro = datetime.strptime(dados['data_registro'], '%Y-%m-%d').strftime('%d/%m/%Y')
                registro_field = encontrar_campo_texto(['dd/mm/aaaa'], 'registro')
                if registro_field:
                    registro_field.click()
                    time.sleep(1)
                    registro_field.clear()
                    time.sleep(1)
                    registro_field.send_keys(data_registro)
                    print(f"✅ Data de registro preenchida: {data_registro}")
                    time.sleep(2)
                else:
                    print("❌ Campo data de registro não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher data de registro: {e}")
        
        # 6. DATA DE NASCIMENTO
        if dados.get('data_nascimento'):
            try:
                print("🔍 Procurando campo Data de nascimento...")
                data_nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').strftime('%d/%m/%Y')
                nascimento_field = encontrar_campo_texto(['dd/mm/aaaa'], 'nascimento')
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
        
        # 7. SEXO
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
        
        # 8. NACIONALIDADE
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
        
        # 9. NOME DA MÃE
        if dados.get('nome_mae'):
            try:
                print("🔍 Procurando campo Nome da mãe...")
                mae_field = encontrar_campo_texto(['Nome da mãe', 'mãe', 'Nome mãe'])
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
        
        # 10. NOME DO PAI (opcional)
        if dados.get('nome_pai'):
            try:
                print("🔍 Procurando campo Nome do pai...")
                pai_field = encontrar_campo_texto(['Nome do pai', 'pai', 'Nome pai'])
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
        
        # 11. ESTADO CIVIL
        if dados.get('estado_civil'):
            try:
                print("🔍 Procurando campo Estado civil...")
                estado_civil_map = {
                    'S': 'Solteiro',
                    'C': 'Casado',
                    'D': 'Divorciado',
                    'V': 'Viúvo',
                    'U': 'União Estável'
                }
                estado_civil_texto = estado_civil_map.get(dados['estado_civil'])
                if estado_civil_texto:
                    estado_civil_select = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[contains(@name, 'estado_civil')]")))
                    from selenium.webdriver.support.ui import Select
                    select = Select(estado_civil_select)
                    select.select_by_visible_text(estado_civil_texto)
                    print(f"✅ Estado civil selecionado: {estado_civil_texto}")
                    time.sleep(2)
            except Exception as e:
                print(f"❌ Erro ao selecionar estado civil: {e}")
        
        # 12. PLANO
        if dados.get('plano'):
            try:
                print("🔍 Procurando campo Plano...")
                plano_field = encontrar_campo_texto(['Plano', 'plano'])
                if plano_field:
                    plano_field.click()
                    time.sleep(1)
                    plano_field.clear()
                    time.sleep(1)
                    plano_field.send_keys(dados['plano'])
                    print(f"✅ Plano preenchido: {dados['plano']}")
                    time.sleep(2)
                else:
                    print("❌ Campo plano não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher plano: {e}")
        
        # 13. CONTRATO DENTAL (opcional)
        if dados.get('contrato_dental'):
            try:
                print("🔍 Procurando campo Contrato Dental...")
                contrato_dental_field = encontrar_campo_texto(['Contrato Dental', 'dental'])
                if contrato_dental_field:
                    contrato_dental_field.click()
                    time.sleep(1)
                    contrato_dental_field.clear()
                    time.sleep(1)
                    contrato_dental_field.send_keys(dados['contrato_dental'])
                    print(f"✅ Contrato dental preenchido: {dados['contrato_dental']}")
                    time.sleep(2)
                else:
                    print("❌ Campo contrato dental não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher contrato dental: {e}")
        
        # 14. PLANO DENTAL (opcional)
        if dados.get('plano_dental'):
            try:
                print("🔍 Procurando campo Plano Dental...")
                plano_dental_field = encontrar_campo_texto(['Plano Dental', 'Plano dental'])
                if plano_dental_field:
                    plano_dental_field.click()
                    time.sleep(1)
                    plano_dental_field.clear()
                    time.sleep(1)
                    plano_dental_field.send_keys(dados['plano_dental'])
                    print(f"✅ Plano dental preenchido: {dados['plano_dental']}")
                    time.sleep(2)
                else:
                    print("❌ Campo plano dental não encontrado")
            except Exception as e:
                print(f"❌ Erro ao preencher plano dental: {e}")
        
        print("🎉 Formulário preenchido com sucesso!")
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
                        print(f"  Campo {i+1}: placeholder='{placeholder}', name='{name}', id='{id_attr}'")
            except Exception as e:
                print(f"❌ Erro ao listar campos: {e}")
            
            preencher_formulario_dinamico(driver, wait, dados_formulario)
        else:
            print("⚠️ Nenhum dado encontrado na API para preencher o formulário")
            print("🔄 Tentando usar dados de teste...")
            
            # Usar dados de teste diretamente
            dados_teste = {
                'id': 1,
                'nome': 'SIDNEI APARECIDO DOS SANTOS JUNIOR',
                'cpf': '422.357.688-73',
                'nome_cartao': 'SIDNEI APARECIDO DOS SANTOS JUNIOR',
                'data_inclusao': '1993-06-12',
                'data_registro': '1993-06-12',
                'data_nascimento': '1993-06-12',
                'sexo': 'M',
                'nacionalidade': 'B',
                'nome_mae': 'ana caroline alves',
                'nome_pai': 'ana caroline alves',
                'estado_civil': 'C',
                'plano': 'TESTE',
                'contrato_dental': 'TESTE',
                'plano_dental': 'TESTE',
                'created_at': '2025-08-05 16:00:13',
                'updated_at': '2025-08-05 16:00:13'
            }
            
            print(f"✅ Dados de teste carregados para: {dados_teste['nome']}")
            
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
                        print(f"  Campo {i+1}: placeholder='{placeholder}', name='{name}', id='{id_attr}'")
            except Exception as e:
                print(f"❌ Erro ao listar campos: {e}")
            
            preencher_formulario_dinamico(driver, wait, dados_teste)
        
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
            while True:
                try:
                    # Verificar se o navegador ainda está aberto
                    driver.current_url
                    time.sleep(5)  # Verificar a cada 5 segundos
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