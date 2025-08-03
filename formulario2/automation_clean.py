import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from django.conf import settings
from .models import AutomationLog
from .automation_config import URLS, CHROME_OPTIONS, TIMING, SCREENSHOT, LOGGING, BEHAVIOR, TEST_DATA
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormularioAutomation:
    def __init__(self, form_data, automation_log=None):
        self.form_data = form_data or TEST_DATA
        self.driver = None
        self.log_file = f"automation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.automation_log = automation_log
        
    def setup_driver(self):
        """Configura o driver do Chrome"""
        try:
            chrome_options = Options()
            
            if CHROME_OPTIONS.get('no_sandbox'):
                chrome_options.add_argument("--no-sandbox")
            if CHROME_OPTIONS.get('disable_dev_shm_usage'):
                chrome_options.add_argument("--disable-dev-shm-usage")
            if CHROME_OPTIONS.get('disable_gpu'):
                chrome_options.add_argument("--disable-gpu")
            if CHROME_OPTIONS.get('window_size'):
                chrome_options.add_argument(f"--window-size={CHROME_OPTIONS['window_size']}")
            if CHROME_OPTIONS.get('headless'):
                chrome_options.add_argument("--headless")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(TIMING.get('element_wait', 10))
            logger.info("Driver do Chrome configurado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {e}")
            return False
    
    def save_form_data_to_json(self):
        """Salva os dados do formulário em JSON"""
        try:
            log_dir = os.path.join(settings.BASE_DIR, LOGGING.get('directory', 'logs'))
            os.makedirs(log_dir, exist_ok=True)
            
            log_path = os.path.join(log_dir, self.log_file)
            
            json_data = {
                'timestamp': datetime.now().isoformat(),
                'form_data': self.form_data,
                'automation_status': 'started',
                'config_used': {
                    'urls': URLS,
                    'behavior': BEHAVIOR,
                    'timing': TIMING
                }
            }
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados do formulário salvos em: {log_path}")
            return log_path
        except Exception as e:
            logger.error(f"Erro ao salvar dados em JSON: {e}")
            return None
    
    def execute_automation(self):
        """Executa a automação principal"""
        try:
            logger.info("Iniciando automação Selenium...")
            
            if self.automation_log:
                self.automation_log.status = 'running'
                self.automation_log.save()
            
            json_path = self.save_form_data_to_json()
            if not json_path:
                return False
            
            if not self.setup_driver():
                return False
            
            success = self.run_automation_steps()
            self.update_log_with_result(json_path, success)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro na execução da automação: {e}")
            if self.automation_log:
                self.automation_log.status = 'failed'
                self.automation_log.error_message = str(e)
                self.automation_log.save()
            return False
        finally:
            if self.driver and BEHAVIOR.get('close_browser', True):
                self.driver.quit()
                logger.info("Navegador fechado")
            elif self.driver:
                logger.info("🔄 Navegador mantido aberto - aguardando instruções para fechar")
                logger.info("💡 Para fechar o navegador, execute: python manage.py close_browser")
    
    def run_automation_steps(self):
        """Executa os passos da automação"""
        try:
            logger.info("Executando passos da automação...")
            
            if BEHAVIOR.get('fetch_last_api_object', True):
                self.fetch_last_api_object()
            
            if BEHAVIOR.get('open_porto_seguro', True):
                self.open_porto_seguro_corretor()
            
            if BEHAVIOR.get('take_screenshots', True):
                screenshot_path = self.take_screenshot()
                logger.info(f"Screenshot salvo em: {screenshot_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro nos passos da automação: {e}")
            return False
    
    def fetch_last_api_object(self):
        """Busca o último objeto da API e imprime no terminal"""
        try:
            logger.info("🔍 Buscando último objeto da API...")
            
            import requests
            
            response = requests.get(URLS['api_endpoint'])
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    last_object = data[-1]
                    
                    print("\n" + "="*80)
                    print("📋 ÚLTIMO OBJETO DA API")
                    print("="*80)
                    print(json.dumps(last_object, indent=2, ensure_ascii=False))
                    print("="*80)
                    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*80 + "\n")
                    
                    logger.info("✅ Último objeto da API encontrado e impresso no terminal")
                    
                    last_object_file = f"last_object_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    last_object_path = os.path.join(settings.BASE_DIR, 'logs', last_object_file)
                    
                    with open(last_object_path, 'w', encoding='utf-8') as f:
                        json.dump(last_object, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"💾 Último objeto salvo em: {last_object_path}")
                    
                else:
                    logger.warning("⚠️ Nenhum objeto encontrado na API")
                    print("\n" + "="*80)
                    print("⚠️ NENHUM OBJETO ENCONTRADO NA API")
                    print("="*80 + "\n")
            else:
                logger.error(f"❌ Erro ao acessar API: {response.status_code}")
                print(f"\n❌ Erro ao acessar API: {response.status_code}\n")
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar último objeto da API: {e}")
            print(f"\n❌ Erro ao buscar último objeto da API: {e}\n")
    
    def open_porto_seguro_corretor(self):
        """Abre o Corretor Online da Porto Seguro"""
        try:
            logger.info("Abrindo Corretor Online da Porto Seguro...")
            
            self.driver.get(URLS['porto_seguro_corretor'])
            time.sleep(TIMING.get('page_load_wait', 3))
            
            logger.info("Corretor Online da Porto Seguro aberto com sucesso")
            time.sleep(5)
            
            if BEHAVIOR.get('click_porto_button', True):
                try:
                    logger.info("🔍 Procurando botão para clicar...")
                    
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div/div[2]/ul/li/button"))
                    )
                    
                    button = self.driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div/div[2]/ul/li/button")
                    button.click()
                    
                    logger.info("✅ Botão clicado com sucesso!")
                    time.sleep(3)
                    
                    if BEHAVIOR.get('do_login', True):
                        logger.info("🔐 Iniciando processo de login...")
                        
                        try:
                            # Aguardar e preencher CPF
                            logger.info("🔍 Aguardando campo de CPF...")
                            WebDriverWait(self.driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="logonPrincipal"]'))
                            )
                            
                            cpf_field = self.driver.find_element(By.XPATH, '//*[@id="logonPrincipal"]')
                            cpf_field.clear()
                            cpf_field.send_keys("140.552.248-85")
                            logger.info("✅ CPF preenchido: 140.552.248-85")
                            time.sleep(2)
                            
                            # Aguardar e preencher senha
                            logger.info("🔍 Aguardando campo de senha...")
                            WebDriverWait(self.driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="liSenha"]/div/input'))
                            )
                            
                            senha_field = self.driver.find_element(By.XPATH, '//*[@id="liSenha"]/div/input')
                            senha_field.clear()
                            senha_field.send_keys("Shaddai2025!")
                            logger.info("✅ Senha preenchida")
                            time.sleep(2)
                            
                            # Aguardar e clicar no botão de login
                            logger.info("🔍 Aguardando botão de login...")
                            WebDriverWait(self.driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH, '//*[@id="inputLogin"]'))
                            )
                            
                            login_button = self.driver.find_element(By.XPATH, '//*[@id="inputLogin"]')
                            login_button.click()
                            logger.info("✅ Botão de login clicado!")
                            
                            time.sleep(5)
                            logger.info("🎉 Processo de login concluído!")
                            
                            # Agora preencher o campo SUSEP e avançar
                            logger.info("📋 Preenchendo campo SUSEP...")
                            
                            try:
                                # Aguardar o campo SUSEP ficar clicável
                                logger.info("🔍 Aguardando campo SUSEP...")
                                WebDriverWait(self.driver, 15).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="susepsAutocomplete"]'))
                                )
                                
                                # Preencher SUSEP
                                susep_field = self.driver.find_element(By.XPATH, '//*[@id="susepsAutocomplete"]')
                                susep_field.clear()
                                susep_field.send_keys("BA6QXJ (P)")
                                logger.info("✅ Campo SUSEP preenchido: BA6QXJ (P)")
                                time.sleep(2)
                                
                                # Aguardar o botão avançar ficar clicável
                                logger.info("🔍 Aguardando botão avançar...")
                                WebDriverWait(self.driver, 15).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="btnAvancarSusep"]'))
                                )
                                
                                # Clicar no botão avançar
                                avancar_button = self.driver.find_element(By.XPATH, '//*[@id="btnAvancarSusep"]')
                                avancar_button.click()
                                logger.info("✅ Botão avançar clicado!")
                                
                                time.sleep(3)
                                logger.info("🎉 Processo SUSEP concluído!")
                                
                            except Exception as susep_error:
                                logger.warning(f"⚠️ Erro durante o preenchimento SUSEP: {susep_error}")
                                logger.info("📋 Tentando métodos alternativos para SUSEP...")
                                
                                try:
                                    # Tentar com JavaScript
                                    susep_field = self.driver.find_element(By.XPATH, '//*[@id="susepsAutocomplete"]')
                                    self.driver.execute_script("arguments[0].value = 'BA6QXJ (P)';", susep_field)
                                    logger.info("✅ Campo SUSEP preenchido via JavaScript")
                                    
                                    avancar_button = self.driver.find_element(By.XPATH, '//*[@id="btnAvancarSusep"]')
                                    self.driver.execute_script("arguments[0].click();", avancar_button)
                                    logger.info("✅ Botão avançar clicado via JavaScript!")
                                    
                                except Exception as js_susep_error:
                                    logger.warning(f"⚠️ JavaScript também falhou no SUSEP: {js_susep_error}")
                                    
                                    try:
                                        # Listar elementos SUSEP encontrados
                                        susep_elements = self.driver.find_elements(By.XPATH, "//input[contains(@id, 'susep') or contains(@id, 'Susep')]")
                                        logger.info(f"🔍 Encontrados {len(susep_elements)} campos SUSEP na página")
                                        
                                        for i, elem in enumerate(susep_elements):
                                            try:
                                                elem_id = elem.get_attribute('id')
                                                elem_type = elem.get_attribute('type')
                                                logger.info(f"Campo SUSEP {i+1}: ID='{elem_id}', Type='{elem_type}'")
                                            except:
                                                logger.info(f"Campo SUSEP {i+1}: [sem atributos]")
                                                
                                    except Exception as find_susep_error:
                                        logger.warning(f"⚠️ Erro ao listar campos SUSEP: {find_susep_error}")
                            
                        except Exception as login_error:
                            logger.warning(f"⚠️ Erro durante o login: {login_error}")
                            logger.info("📋 Tentando métodos alternativos para login...")
                            
                            try:
                                cpf_field = self.driver.find_element(By.XPATH, '//*[@id="logonPrincipal"]')
                                self.driver.execute_script("arguments[0].value = '140.552.248-85';", cpf_field)
                                logger.info("✅ CPF preenchido via JavaScript")
                                
                                senha_field = self.driver.find_element(By.XPATH, '//*[@id="liSenha"]/div/input')
                                self.driver.execute_script("arguments[0].value = 'Shaddai2025!';", senha_field)
                                logger.info("✅ Senha preenchida via JavaScript")
                                
                                login_button = self.driver.find_element(By.XPATH, '//*[@id="inputLogin"]')
                                self.driver.execute_script("arguments[0].click();", login_button)
                                logger.info("✅ Login via JavaScript executado!")
                                
                            except Exception as js_login_error:
                                logger.warning(f"⚠️ JavaScript também falhou no login: {js_login_error}")
                                
                                try:
                                    login_elements = self.driver.find_elements(By.XPATH, "//input[@type='text' or @type='password']")
                                    logger.info(f"🔍 Encontrados {len(login_elements)} campos de input na página")
                                    
                                    for i, elem in enumerate(login_elements):
                                        try:
                                            elem_id = elem.get_attribute('id')
                                            elem_type = elem.get_attribute('type')
                                            logger.info(f"Campo {i+1}: ID='{elem_id}', Type='{elem_type}'")
                                        except:
                                            logger.info(f"Campo {i+1}: [sem atributos]")
                                            
                                except Exception as find_login_error:
                                    logger.warning(f"⚠️ Erro ao listar campos de login: {find_login_error}")
                    
                except Exception as click_error:
                    logger.warning(f"⚠️ Não foi possível clicar no botão: {click_error}")
                    logger.info("📋 Tentando métodos alternativos...")
                    
                    try:
                        button = self.driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div/div[2]/ul/li/button")
                        self.driver.execute_script("arguments[0].click();", button)
                        logger.info("✅ Botão clicado via JavaScript!")
                    except Exception as js_error:
                        logger.warning(f"⚠️ JavaScript também falhou: {js_error}")
                        
                        try:
                            buttons = self.driver.find_elements(By.TAG_NAME, "button")
                            logger.info(f"🔍 Encontrados {len(buttons)} botões na página")
                            
                            for i, btn in enumerate(buttons):
                                try:
                                    text = btn.text
                                    logger.info(f"Botão {i+1}: '{text}'")
                                except:
                                    logger.info(f"Botão {i+1}: [sem texto]")
                                    
                        except Exception as find_error:
                            logger.warning(f"⚠️ Erro ao listar botões: {find_error}")
            
            logger.info("⚠️ Navegador será mantido aberto até você mandar fechar")
            
        except Exception as e:
            logger.error(f"Erro ao abrir Corretor Online da Porto Seguro: {e}")
    
    def take_screenshot(self):
        """Tira um screenshot da página atual"""
        try:
            screenshot_dir = os.path.join(settings.BASE_DIR, SCREENSHOT.get('directory', 'screenshots'))
            os.makedirs(screenshot_dir, exist_ok=True)
            
            screenshot_name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{SCREENSHOT.get('format', 'png')}"
            screenshot_path = os.path.join(screenshot_dir, screenshot_name)
            
            self.driver.save_screenshot(screenshot_path)
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Erro ao tirar screenshot: {e}")
            return None
    
    def update_log_with_result(self, json_path, success):
        """Atualiza o log com o resultado da automação"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['automation_status'] = 'completed' if success else 'failed'
            data['completion_timestamp'] = datetime.now().isoformat()
            data['success'] = success
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if self.automation_log:
                self.automation_log.status = 'completed' if success else 'failed'
                self.automation_log.completed_at = datetime.now()
                self.automation_log.log_file_path = json_path
                self.automation_log.automation_data = data
                self.automation_log.save()
            
            logger.info(f"Log atualizado com resultado: {'sucesso' if success else 'falha'}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar log: {e}")

def run_automation_for_form(form_data, automation_log=None):
    """Função principal para executar automação para um formulário"""
    try:
        automation = FormularioAutomation(form_data, automation_log)
        success = automation.execute_automation()
        
        if success:
            logger.info("✅ Automação executada com sucesso!")
        else:
            logger.error("❌ Falha na execução da automação")
        
        return success
        
    except Exception as e:
        logger.error(f"Erro ao executar automação: {e}")
        return False 