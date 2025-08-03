import json
import time
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
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
        """Configura o driver do Chrome com configurações anti-detecção"""
        try:
            chrome_options = Options()
            
            # Configurações anti-detecção
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Configurações de performance
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
            
            # Configurações adicionais anti-detecção
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Executar script para remover propriedades de automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(TIMING.get('element_wait', 10))
            logger.info("Driver do Chrome configurado com sucesso (anti-detecção ativado)")
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
            data = {
                'timestamp': datetime.now().isoformat(),
                'form_data': self.form_data,
                'automation_status': 'started',
                'config_used': {'urls': URLS, 'behavior': BEHAVIOR, 'timing': TIMING}
            }
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Dados do formulário salvos em: {log_path}")
            return log_path
        except Exception as e:
            logger.error(f"Erro ao salvar dados em JSON: {e}")
            return None
    
    def execute_automation(self):
        """Executa a automação principal"""
        try:
            logger.info("🚀 INICIANDO AUTOMAÇÃO DO PORTO SEGURO...")
            if self.automation_log:
                self.automation_log.status = 'running'
                self.automation_log.save()
            json_path = self.save_form_data_to_json()
            if not json_path or not self.setup_driver():
                return False
            success = self.run_porto_seguro_automation()
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
            if self.driver:
                logger.info("🔄 Navegador mantido aberto")
                # GARANTIR que o navegador NUNCA seja fechado
                # Não chamar self.driver.quit() ou self.driver.close()
                
                # PROTEÇÃO EXTRA: Manter o driver vivo
                try:
                    # Verificar se o driver ainda está ativo
                    self.driver.current_url
                    logger.info("✅ Driver ainda ativo - navegador permanecerá aberto")
                except:
                    logger.warning("⚠️ Driver pode ter sido fechado automaticamente")

    def run_porto_seguro_automation(self):
        """Automação específica do Porto Seguro - APENAS LOGIN"""
        try:
            # 1. Acessa página de login
            porto_url = "https://corretor.portoseguro.com.br/portal/site/corretoronline/template.LOGIN/"
            logger.info("🌐 ABRINDO PORTO SEGURO CORRETOR ONLINE...")
            self.driver.get(porto_url)
            logger.info(f"✅ Página aberta: {porto_url}")
            time.sleep(10)
            
            # Aguardar carregamento da página
            logger.info("⏳ Aguardando carregamento da página...")
            time.sleep(5)
            
            # 2. Clicar no botão específico
            logger.info("🔍 Procurando botão para clicar...")
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div/div[2]/ul/li/button"))
                )
                
                button = self.driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div/div[2]/ul/li/button")
                button.click()
                
                logger.info("✅ Botão clicado com sucesso!")
                time.sleep(3)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao clicar no botão: {e}")
                # Continuar mesmo se não conseguir clicar no botão
            
            # Tirar screenshot de debug
            if BEHAVIOR.get('take_screenshots', True):
                screenshot_path = self.take_screenshot()
                if screenshot_path:
                    logger.info(f"📸 Screenshot de debug salvo em: {screenshot_path}")
            
            # 3. Aguardar página carregar completamente antes do login
            logger.info("⏳ Aguardando carregamento completo da página...")
            try:
                WebDriverWait(self.driver, 20).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logger.info("✅ Página carregada completamente")
                time.sleep(2)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao aguardar carregamento: {e}")
            
            # 4. Processo de login
            logger.info("🔐 INICIANDO PROCESSO DE LOGIN...")
            
            # Preencher CPF
            logger.info("📝 Preenchendo CPF...")
            try:
                # Tentar diferentes seletores para o campo CPF
                cpf_selectors = [
                    '//*[@id="logonPrincipal"]',
                    '//input[@id="logonPrincipal"]',
                    '//input[@name="logonPrincipal"]',
                    '//input[@type="text"]',
                    '//input[contains(@class, "login")]'
                ]
                
                cpf_field = None
                for selector in cpf_selectors:
                    try:
                        cpf_field = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logger.info(f"✅ Campo CPF encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                if not cpf_field:
                    raise Exception("Campo CPF não encontrado")
                
                cpf_field.clear()
                cpf_field.send_keys('140.552.248-85')
                logger.info("✅ CPF preenchido: 140.552.248-85")
                
            except Exception as e:
                logger.error(f"❌ Erro ao preencher CPF: {e}")
                self.take_screenshot()
                raise e
            
            # Preencher senha
            logger.info("🔒 Preenchendo senha...")
            try:
                # Tentar diferentes seletores para o campo senha
                password_selectors = [
                    '//*[@id="liSenha"]/div/input',
                    '//input[@id="liSenha"]',
                    '//input[@type="password"]',
                    '//input[contains(@name, "senha")]',
                    '//input[contains(@name, "password")]'
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logger.info(f"✅ Campo senha encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                if not password_field:
                    raise Exception("Campo senha não encontrado")
                
                password_field.clear()
                password_field.send_keys('Shaddai2025!')
                logger.info("✅ Senha preenchida")
                
            except Exception as e:
                logger.error(f"❌ Erro ao preencher senha: {e}")
                self.take_screenshot()
                raise e
            
            # Clicar no botão de login
            logger.info("🚀 Clicando no botão de login...")
            try:
                # Tentar diferentes seletores para o botão de login
                login_selectors = [
                    '//*[@id="inputLogin"]',
                    '//button[@id="inputLogin"]',
                    '//input[@id="inputLogin"]',
                    '//button[contains(text(), "Login")]',
                    '//button[contains(text(), "Entrar")]',
                    '//input[@type="submit"]',
                    '//button[@type="submit"]'
                ]
                
                login_button = None
                for selector in login_selectors:
                    try:
                        login_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logger.info(f"✅ Botão de login encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                if not login_button:
                    raise Exception("Botão de login não encontrado")
                
                login_button.click()
                logger.info("✅ Botão de login clicado!")
                
            except Exception as e:
                logger.error(f"❌ Erro ao clicar no botão de login: {e}")
                self.take_screenshot()
                raise e
            
            # Aguardar processamento do login
            logger.info("⏳ Aguardando processamento do login...")
            time.sleep(10)
            codigo1 = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="susepsAutocomplete"]'))
            )
            codigo1.click()
            codigo1.send_keys('BA6QXJ (P)')
            logger.info("✅ codigo passado")
            time.sleep(10)
            enter = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="btnAvancarSusep"]'))
            )
            enter.click()
            logger.info("✅ Botão de login clicado!")
            time.sleep(10)
            
            # 5. VERIFICAR SE O LOGIN FOI BEM-SUCEDIDO
            logger.info("🔍 VERIFICANDO SE O LOGIN FOI BEM-SUCEDIDO...")
            try:
                # Verificar se ainda está na página de login
                login_elements = self.driver.find_elements(By.XPATH, '//*[@id="logonPrincipal"]')
                if login_elements:
                    logger.error("❌ LOGIN FALHOU - Ainda na página de login!")
                    return False
                else:
                    logger.info("✅ LOGIN REALIZADO COM SUCESSO!")
                    logger.info("🎉 AUTOMAÇÃO PARADA APÓS LOGIN - Navegador permanecerá aberto!")
                    
                    # Tirar screenshot do sucesso
                    if BEHAVIOR.get('take_screenshots', True):
                        self.take_screenshot()
                    
                    return True
            except Exception as e:
                logger.error(f"❌ Erro ao verificar login: {e}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro na automação: {e}")
            logger.info("🔄 NAVEGADOR PERMANECERÁ ABERTO MESMO COM ERRO!")
            return False
    
    def take_screenshot(self):
        try:
            dirpath = os.path.join(settings.BASE_DIR, SCREENSHOT.get('directory','screenshots'))
            os.makedirs(dirpath, exist_ok=True)
            name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(dirpath, name)
            self.driver.save_screenshot(path)
            return path
        except Exception as e:
            logger.error(f"Erro ao tirar screenshot: {e}")
            return None
    
    def update_log_with_result(self, json_path, success):
        try:
            with open(json_path,'r',encoding='utf-8') as f: data = json.load(f)
            data.update({'automation_status': 'completed' if success else 'failed', 'completion_timestamp': datetime.now().isoformat(), 'success': success})
            with open(json_path,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False, indent=2)
            if self.automation_log:
                self.automation_log.status = 'completed' if success else 'failed'
                self.automation_log.completed_at = datetime.now()
                self.automation_log.log_file_path = json_path
                self.automation_log.automation_data = data
                self.automation_log.save()
        except Exception as e:
            logger.error(f"Erro ao atualizar log: {e}")

def run_automation_for_form(form_data, automation_log=None):
    automation = FormularioAutomation(form_data, automation_log)
    return automation.execute_automation()
