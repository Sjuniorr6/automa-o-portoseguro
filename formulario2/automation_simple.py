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
            # NÃO FECHAR O NAVEGADOR - SEMPRE MANTER ABERTO
            if self.driver:
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
            
            # Verificar se o servidor Django está rodando
            try:
                response = requests.get(URLS['api_endpoint'], timeout=10)
                
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
                    
            except requests.exceptions.ConnectionError:
                logger.warning("⚠️ Não foi possível conectar à API - servidor Django pode não estar rodando")
                print("\n" + "="*80)
                print("⚠️ SERVIDOR DJANGO NÃO ESTÁ RODANDO")
                print("💡 Para iniciar o servidor, execute: python manage.py runserver")
                print("="*80 + "\n")
                
            except requests.exceptions.Timeout:
                logger.warning("⚠️ Timeout ao acessar API")
                print("\n" + "="*80)
                print("⚠️ TIMEOUT AO ACESSAR API")
                print("="*80 + "\n")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Erro de requisição: {e}")
                print(f"\n❌ Erro de requisição: {e}\n")
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar último objeto da API: {e}")
            print(f"\n❌ Erro ao buscar último objeto da API: {e}\n")
    
    def redirect_to_gestao_apolice(self):
        """Redireciona diretamente para a página de Gestão de Apólice"""
        try:
            logger.info("🔗 REDIRECIONANDO DIRETAMENTE PARA A PÁGINA DE GESTÃO DE APÓLICE...")
            
            # REDIRECIONAR DIRETAMENTE PARA O LINK ESPECÍFICO QUE O USUÁRIO PASSOU
            direct_url = "https://corretor.portoseguro.com.br/corretoronline/iframe?javax.portlet.ctx_iframe=url=https://wwws.portoseguro.com.br/react-spa-saud-pbko-administracao-de-apolices/?source=col%23%23document=BA6QXJ%23%23smsession=GRqo0%2B6TePp7GKzz%2BQqJzlawkxRupIzg4rbQwGwpWTgLObFLc9NzLz%2FjZtqD1rUDkKNWxp9dRoFe3%2FETaEzxrfwTsgr2JXv1WoaAJ6E4rbIVxQ8MZ4a8Rq6ObmxhNSTBvucqDpN8rMiHQ%2F0X1iNvv92vliirWJMv%2FYcpjThzSzPHVquikud7kJLKD8gR3DmLFRAgF4%2BIrxSeT%2BpEPPGagudjqFuCNOvpwVmv34NuT5dgSf02YdEppkofCqHF1hLP%2F11F0X%2FrJ8iVPL0vkCOM1vg25MjFUVmZrBCJHHRl2VD4opNTdHVeWa2MtH2jKvCo4x%2Bzoh6cZZzgTeyjsTUbjqYCEz6bRPL64P1vDsrYud2u4V6ajDHkBO4sjZHaoKNZ5UwGMbSaXGGYsmQRA19ViQobTe6gjwrtbhmfU038mXtBqmRATLG5IwzDPBW2GDshprnfcTmmuCmsiGhWpLOpMZ5Ibg1lOU2CaczZ6qirYX63rEi3PZWVnUCfwLtGORu2BnAv1tzU2mCymWNu0%2Bwcj69uAaRfksJyabDvvo4W7hYmHgytR4Mw5HeCcxiRx4bJnJdsDzePtczWdkxkaBmG%2Fyt0xZyAdV6S%2FYKEZLOdtXRFkmP4fTl4V9aVGiQ558Xj8dl12G8%2BMliYD6XqFMVXBuxjTtOGF8GvMZrWnnSFTPBBpqi1BWm2pI28nfr8%2Blj2obsULSMDBLglR2DC0bLFGChM8XC%2FUDQ2xbvjjIOIqWbtjm0jOTNk8LAH5J9OIgHF0eQtrT%2BEa0eLg6zaUWcX%2BV80xJU%2BZ4nuqdFSSlqIAJz1SbJWibukAp2Sb2L9Pcy3hsaD8qHtpbH0NM%2B9wqzbSEVzDi9V2zhb9jojJ7C9hTsQGKCujYpk0v1xRinVVVmb9H1iq40p3LHf5JU7LEUdWpxKihD3lpChfX1bjQheduSe6EULkKnT%2BOtkRMxZ%2BaDw42TS6ouFMH4%2FPqMIxtbDp83JpIybrVBal%2FDK5tSRVIADQvoUEZPpeMho9tb9fyHmfjn0Jp3s70TYrpBMPgtXHbhOMmpjrNyY4tYhAuoC8NZ9phaDDywW8bc%2BM5J%2F9SGjUXC1p7G9wqVq8AJe66QcOhgPhF3ZPwdzGEbINvm193YQ4%2B53O4O1W%2BNo3r3XfOLLrtYVOTUApiLwuAMmbxaUtrNRScHdXOk"
            
            logger.info("🔗 NAVEGANDO DIRETAMENTE PARA O LINK ESPECÍFICO DO USUÁRIO...")
            self.driver.get(direct_url)
            
            # ESPERAR MUITO TEMPO PARA A PÁGINA CARREGAR COMPLETAMENTE
            logger.info("⏳ ESPERANDO A PÁGINA CARREGAR COMPLETAMENTE...")
            time.sleep(30)  # ESPERAR 30 SEGUNDOS
            
            # VERIFICAR SE CHEGOU NA PÁGINA CORRETA
            current_url = self.driver.current_url
            logger.info(f"🌐 URL atual: {current_url}")
            
            if "administracao-de-apolices" in current_url or "corretoronline" in current_url:
                logger.info("🎉 CHEGOU NA PÁGINA CORRETA! AGORA VOU CLICAR ONDE VOCÊ PEDIU!")
                
                # ESPERAR MAIS UM POUCO PARA GARANTIR QUE TUDO CARREGOU
                logger.info("⏳ ESPERANDO MAIS 10 SEGUNDOS PARA GARANTIR...")
                time.sleep(10)
                
                # CLICAR E COLAR NO CAMPO ESPECÍFICO
                logger.info("🎯 CLICANDO E COLANDO NO CAMPO ESPECÍFICO...")
                
                try:
                    # CLICAR NO CAMPO ESPECÍFICO
                    logger.info("🎯 CLICANDO NO CAMPO: //*[@id='container_page_mov']/div/div/div[1]/div/div/label/input")
                    campo_element = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='container_page_mov']/div/div/div[1]/div/div/label/input"))
                    )
                    
                    # Clicar no campo
                    campo_element.click()
                    logger.info("✅ CAMPO CLICADO COM SUCESSO!")
                    time.sleep(2)
                    
                    # COLAR O VALOR
                    logger.info("📋 COLANDO VALOR: 60146757")
                    campo_element.send_keys("60146757")
                    logger.info("✅ VALOR COLADO COM SUCESSO: 60146757")
                    
                except Exception as click_error:
                    logger.error(f"❌ ERRO AO CLICAR/COLAR: {click_error}")
                    
                    # Tentar com JavaScript como fallback
                    try:
                        logger.info("⚡ TENTANDO COM JAVASCRIPT...")
                        self.driver.execute_script("""
                            var campo = document.querySelector('#container_page_mov div div div:nth-child(1) div div label input');
                            if (campo) {
                                campo.click();
                                campo.value = '60146757';
                                campo.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        """)
                        logger.info("✅ VALOR DEFINIDO VIA JAVASCRIPT: 60146757")
                    except Exception as js_error:
                        logger.error(f"❌ ERRO COM JAVASCRIPT: {js_error}")
            else:
                logger.warning("⚠️ NÃO CHEGOU NA PÁGINA CORRETA, MAS VOU TENTAR CLICAR MESMO ASSIM...")
                
                # Tentar clicar mesmo assim
                try:
                    logger.info("🎯 TENTANDO CLICAR MESMO ASSIM...")
                    campo_element = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='container_page_mov']/div/div/div[1]/div/div/label/input"))
                    )
                    campo_element.click()
                    campo_element.send_keys("60146757")
                    logger.info("✅ CLICOU E COLOU MESMO ASSIM!")
                except Exception as final_error:
                    logger.error(f"❌ ERRO FINAL: {final_error}")
            
            return True
                
        except Exception as redirect_error:
            logger.error(f"❌ Erro no redirecionamento direto: {redirect_error}")
            return False
    
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
                                
                                # Aguardar um pouco antes de clicar no menu
                                logger.info("⏳ Aguardando carregamento da página antes de clicar no menu...")
                                time.sleep(10)
                                
                                # Agora clicar nos elementos adicionais
                                logger.info("🔍 Clicando em elementos adicionais...")
                                
                                try:
                                    # Clicar no primeiro elemento
                                    logger.info("🔍 Aguardando elemento favorites...")
                                    WebDriverWait(self.driver, 20).until(
                                        EC.element_to_be_clickable((By.XPATH, '//*[@id="favorites"]/div/div/div/div/span/i'))
                                    )
                                    
                                    favorites_element = self.driver.find_element(By.XPATH, '//*[@id="favorites"]/div/div/div/div/span/i')
                                    favorites_element.click()
                                    logger.info("✅ Elemento favorites clicado!")
                                    time.sleep(2)
                                    
                                    # Clicar no segundo elemento
                                    logger.info("🔍 Aguardando elemento COL-02TS6...")
                                    WebDriverWait(self.driver, 15).until(
                                        EC.element_to_be_clickable((By.XPATH, '//*[@id="COL-02TS6"]'))
                                    )
                                    col_element = self.driver.find_element(By.XPATH, '//*[@id="COL-02TS6"]')
                                    col_element.click()
                                    logger.info("✅ Elemento COL-02TS6 clicado!")
                                    time.sleep(2)

                                    # Clicar no terceiro elemento
                                    logger.info("🔍 Aguardando elemento 9982...")
                                    WebDriverWait(self.driver, 15).until(
                                        EC.element_to_be_clickable((By.XPATH, '//*[@id="9982"]'))
                                    )
                                    element_9982 = self.driver.find_element(By.XPATH, '//*[@id="9982"]')
                                    element_9982.click()
                                    logger.info("✅ Elemento 9982 clicado!")
                                    time.sleep(2)

                                    # Clicar no quarto elemento
                                    logger.info("🔍 Aguardando elemento COL-02X27...")
                                    WebDriverWait(self.driver, 15).until(
                                        EC.element_to_be_clickable((By.XPATH, '//*[@id="COL-02X27"]'))
                                    )
                                    col_x27_element = self.driver.find_element(By.XPATH, '//*[@id="COL-02X27"]')
                                    col_x27_element.click()
                                    logger.info("✅ Elemento COL-02X27 clicado!")
                                    time.sleep(3)

                                    # Clicar no quinto elemento (single-spa-application)
                                    logger.info("🔍 Aguardando elemento single-spa-application...")
                                    WebDriverWait(self.driver, 15).until(
                                        EC.element_to_be_clickable((By.XPATH, '//*[@id="single-spa-application:@porto-seguro/ssmr-corp-ncol-mfe-products"]/div/div/div/div[2]/div[3]/div/a[2]/button'))
                                    )
                                    single_spa_element = self.driver.find_element(By.XPATH, '//*[@id="single-spa-application:@porto-seguro/ssmr-corp-ncol-mfe-products"]/div/div/div/div[2]/div[3]/div/a[2]/button')
                                    single_spa_element.click()
                                    logger.info("✅ Elemento single-spa-application clicado!")
                                    time.sleep(3)

                                    logger.info("🎉 Todos os elementos adicionais clicados com sucesso!")
                                    
                                    # Aguardar carregamento da página após cliques
                                    logger.info("⏳ Aguardando carregamento da página após cliques...")
                                    time.sleep(10)
                                    
                                    # Tentar encontrar e clicar no card "Gestão de Apólice"
                                    logger.info("🎯 Tentando encontrar card 'Gestão de Apólice'...")
                                    try:
                                        # Aguardar elemento ficar clicável
                                        gestao_element = WebDriverWait(self.driver, 15).until(
                                            EC.element_to_be_clickable((By.XPATH, "//a[.//h2[contains(text(), 'Gestão de Apólice')]]"))
                                        )
                                        gestao_element.click()
                                        logger.info("✅ Card 'Gestão de Apólice' clicado com sucesso!")
                                        time.sleep(5)
                                        
                                        # Verificar se chegou na página correta
                                        current_url = self.driver.current_url
                                        if "administracao-de-apolices" in current_url:
                                            logger.info("🎉 SUCESSO! Página de Gestão de Apólice carregada!")
                                            
                                            # Aguardar carregamento completo da página
                                            logger.info("⏳ Aguardando carregamento completo da página...")
                                            time.sleep(15)
                                            
                                            # CLICAR E COLAR NO CAMPO ESPECÍFICO
                                            logger.info("🎯 CLICANDO E COLANDO NO CAMPO ESPECÍFICO...")
                                            
                                            try:
                                                # 1. CLICAR NO CAMPO ESPECÍFICO
                                                logger.info("🎯 CLICANDO NO CAMPO: //*[@id='container_page_mov']/div/div/div[1]/div/div/label/input")
                                                campo_element = WebDriverWait(self.driver, 15).until(
                                                    EC.element_to_be_clickable((By.XPATH, "//*[@id='container_page_mov']/div/div/div[1]/div/div/label/input"))
                                                )
                                                
                                                # Clicar no campo
                                                campo_element.click()
                                                logger.info("✅ CAMPO CLICADO COM SUCESSO!")
                                                time.sleep(1)
                                                
                                                # 2. COLAR O VALOR
                                                logger.info("📋 COLANDO VALOR: 60146757")
                                                campo_element.send_keys("60146757")
                                                logger.info("✅ VALOR COLADO COM SUCESSO: 60146757")
                                                
                                            except Exception as click_error:
                                                logger.error(f"❌ ERRO AO CLICAR/COLAR: {click_error}")
                                                
                                                # Tentar com JavaScript como fallback
                                                try:
                                                    logger.info("⚡ TENTANDO COM JAVASCRIPT...")
                                                    self.driver.execute_script("""
                                                        var campo = document.querySelector('#container_page_mov div div div:nth-child(1) div div label input');
                                                        if (campo) {
                                                            campo.click();
                                                            campo.value = '60146757';
                                                            campo.dispatchEvent(new Event('input', { bubbles: true }));
                                                        }
                                                    """)
                                                    logger.info("✅ VALOR DEFINIDO VIA JAVASCRIPT: 60146757")
                                                except Exception as js_error:
                                                    logger.error(f"❌ ERRO COM JAVASCRIPT: {js_error}")
                                        else:
                                            logger.info("⚠️ Clique não levou à página esperada - redirecionando diretamente...")
                                            self.redirect_to_gestao_apolice()
                                            
                                    except Exception as gestao_error:
                                        logger.warning(f"⚠️ Erro ao clicar no card 'Gestão de Apólice': {gestao_error}")
                                        self.redirect_to_gestao_apolice()
                                    
                                except Exception as additional_click_error:
                                    logger.warning(f"⚠️ Erro durante cliques adicionais: {additional_click_error}")
                                    self.redirect_to_gestao_apolice()
                                    
                            except Exception as susep_error:
                                logger.warning(f"⚠️ Erro durante o preenchimento SUSEP: {susep_error}")
                                self.redirect_to_gestao_apolice()
                        
                        except Exception as login_error:
                            logger.warning(f"⚠️ Erro durante o login: {login_error}")
                            self.redirect_to_gestao_apolice()
                
                except Exception as click_error:
                    logger.warning(f"⚠️ Não foi possível clicar no botão: {click_error}")
                    self.redirect_to_gestao_apolice()
            
            logger.info("⚠️ Navegador será mantido aberto até você mandar fechar")
            
        except Exception as e:
            logger.error(f"Erro ao abrir Corretor Online da Porto Seguro: {e}")
            self.redirect_to_gestao_apolice()
    
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