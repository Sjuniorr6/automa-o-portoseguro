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
            direct_url = "https://corretor.portoseguro.com.br/corretoronline/iframe?javax.portlet.ctx_iframe=url=https://wwws.portoseguro.com.br/react-spa-saud-pbko-administracao-de-apolices/?source=col%23%23document=BA6QXJ%23%23smsession=p52EF78FvWcgQ89AGUEHJKmBbEB%2FwMBaILoMVlZMNoZvbw5cp2eufXJipoCig4y6vkjz6y6vq8TKI8wLYOv6IaLm5OWN6hinP55gu2zETtrT8GPof9cuDpxnaRWK5zxVmB1hSJMq3R6JF%2F%2BUbhe8OWkgvA8jg2pKt0AXlSsNl%2Bq4cfr%2FZDyxW3I8cI1dS0xEJcMccW6c73hmk3w3FkSeSkuX4KLaG5uaV7OGcZxBO5sw4O2wy%2BjFUSAL1AYrIVzLMsunEtPMYoldyXi8nHrmAE1sDF7INUHgCnrQQ%2BKD1pUTLF4%2B%2BfOZ3zdQKyB%2FU9RBXBaiClGOMSw7mpiyFr%2FBqT3UA8Pyj8%2B972%2FV%2B9gfWvZa4KkfQOVwIJTMvkZJlebHnX6JWUlHdmBZnFtFBN6b%2Fcc%2BxfysmhVJMKAvGVKf%2BNFgXoqExLx8J4ozxKGNFzxHCNm1GX3yTdgbHE0CjPkSUyfwnihUZks2ing9P7FXYNAPayTD692PIXnkj7p7i9XwQ3BqBj1W15g68PcDKMh1Aiktw4VPXfWPNY%2FiRHA4dwkhCSFxYnZcOSMEVWxo6y%2FnSx7BZxmTr2xqrKD9fDM71xFN8EmJoDDnNdPZVIVbF2vCgHs9JPldJrSm8cn5kH42a%2F7NuSldxI3Ez4wzhvOz%2FslHtCstgHtiefqwMdvhVFaFLWZyw3%2BUWZVJuCTZsz8ftdF66zvdsINe1qWuyF2gikeZFLjcf4GioF0zvREQe1rZ3H27BlhjzhECU55WfmxLcQR4n4Uew8h2thHZ7bsKfE07xW7sSAb1y3I4lmCn1TX57I5lxtFR2RSQ0ZCCUWtwNYspFT1bGBAjtA0OQm5glsCVUzrfVaZq5i0wbr9FN05PxVxlrkwSNyJNu7lcBx7NE8jly6wgdx2qftFRVYYz%2F4BZ0rsUsZRa0eOiSKoQJjKsGY8QbO6FjDVWJDXHPMGzqPXaKo1XVvVQvR3DX%2BqjLldbCREbJSlGcwAY4Rc%2BJuIQM2jPp80wN87bpnEX8byOtriFjiWOViAnblZp4DJcZPKNQxFdhAZD37dsam3f%2BwqCRCZmgHrBxRAfr5y0mERTU9aue22FjEBZpsbudufd60R8EqV4Q4zx%2FjZ7RzSOkuw2U1EmGeH2m09eWYciArk587wsDjtUlUfBbGvGTWMAOZ6OOQyOuwZU"
            
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
                    
                    # VERIFICAR SE É UM CAMPO SELECT E ITERAR SOBRE AS OPÇÕES
                    logger.info("🔍 VERIFICANDO SE É UM CAMPO SELECT...")
                    
                    # Tentar encontrar o elemento como select
                    try:
                        from selenium.webdriver.support.ui import Select
                        
                        # Procurar por um select relacionado ao campo
                        select_element = self.driver.find_element(By.XPATH, "//*[@id='container_page_mov']/div/div/div[1]/div/div/label/select")
                        select = Select(select_element)
                        
                        print("\n" + "="*80)
                        print("📋 OPÇÕES DO CAMPO SELECT:")
                        print("="*80)
                        
                        # Listar todas as opções
                        options = select.options
                        for i, option in enumerate(options):
                            print(f"{i+1}. {option.text} (value: {option.get_attribute('value')})")
                        
                        print("="*80)
                        print(f"Total de opções: {len(options)}")
                        print("="*80 + "\n")
                        
                        logger.info(f"✅ Encontradas {len(options)} opções no select")
                        
                        # Tentar selecionar a opção que contém "60146757"
                        for option in options:
                            if "60146757" in option.text or "60146757" in option.get_attribute('value'):
                                select.select_by_visible_text(option.text)
                                logger.info(f"✅ Opção selecionada: {option.text}")
                                break
                        else:
                            # Se não encontrar, tentar digitar o valor
                            logger.info("📝 Digite o valor: 60146757")
                            campo_element.send_keys("60146757")
                            logger.info("✅ VALOR DIGITADO: 60146757")
                            
                    except Exception as select_error:
                        logger.info("⚠️ Não é um select, tratando como input normal")
                        
                        # COLAR O VALOR
                        logger.info("📋 COLANDO VALOR: 60146757")
                        campo_element.send_keys("60146757")
                        logger.info("✅ VALOR COLADO COM SUCESSO: 60146757")
                        
                        # Tentar também com JavaScript para garantir
                        try:
                            self.driver.execute_script("""
                                var campo = document.querySelector('#container_page_mov div div div:nth-child(1) div div label input');
                                if (campo) {
                                    campo.value = '60146757';
                                    campo.dispatchEvent(new Event('input', { bubbles: true }));
                                    campo.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                            """)
                            logger.info("✅ VALOR DEFINIDO VIA JAVASCRIPT: 60146757")
                        except Exception as js_error:
                            logger.error(f"❌ ERRO COM JAVASCRIPT: {js_error}")
                    
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
                                    
                                    # ESTRATÉGIA AGRESSIVA: Clicar no card "Gestão de Apólice" usando JavaScript
                                    logger.info("🎯 ESTRATÉGIA AGRESSIVA: Procurando e clicando no card 'Gestão de Apólice'...")
                                    
                                    # Aguardar um pouco para a página carregar completamente
                                    time.sleep(5)
                                    
                                    try:
                                        # MÉTODO 1: Procurar pelo elemento <a> pai do título "Gestão de Apólice"
                                        logger.info("🔍 MÉTODO 1: Procurando pelo elemento <a> pai do título 'Gestão de Apólice'...")
                                        
                                        # Aguardar o card ficar presente e clicável
                                        gestao_card = WebDriverWait(self.driver, 15).until(
                                            EC.presence_of_element_located(
                                                (By.XPATH, "//h2[text()='Gestão de Apólice']/ancestor::a")
                                            )
                                        )
                                        
                                        logger.info("✅ Card 'Gestão de Apólice' encontrado via XPath!")
                                        
                                        # Usar JavaScript para garantir que o evento onclick seja disparado
                                        self.driver.execute_script("arguments[0].click();", gestao_card)
                                        logger.info("✅ Card 'Gestão de Apólice' clicado via JavaScript!")
                                        time.sleep(10)
                                        
                                    except Exception as method1_error:
                                        logger.warning(f"⚠️ Método 1 falhou: {method1_error}")
                                        
                                        try:
                                            # MÉTODO 2: Procurar por cards usando CSS selector e clicar no segundo
                                            logger.info("🔍 MÉTODO 2: Procurando por cards usando CSS selector...")
                                            
                                            cards = self.driver.find_elements(By.CSS_SELECTOR, ".square-card-button")
                                            if len(cards) >= 2:
                                                # O segundo card (índice 1) é o Gestão de Apólice
                                                logger.info(f"✅ Encontrados {len(cards)} cards, clicando no segundo...")
                                                self.driver.execute_script("arguments[0].click();", cards[1])
                                                logger.info("✅ Segundo card clicado via JavaScript!")
                                                time.sleep(10)
                                            else:
                                                logger.warning(f"⚠️ Apenas {len(cards)} cards encontrados")
                                                raise Exception("Poucos cards encontrados")
                                                
                                        except Exception as method2_error:
                                            logger.warning(f"⚠️ Método 2 falhou: {method2_error}")
                                            
                                            try:
                                                # MÉTODO 3: Procurar por qualquer elemento com "Gestão de Apólice"
                                                logger.info("🔍 MÉTODO 3: Procurando por qualquer elemento com 'Gestão de Apólice'...")
                                                
                                                gestao_script = """
                                                // Procurar por qualquer elemento que contenha "Gestão de Apólice"
                                                var elements = document.querySelectorAll('*');
                                                for (var i = 0; i < elements.length; i++) {
                                                    var element = elements[i];
                                                    var text = element.textContent || element.innerText || '';
                                                    if (text.toLowerCase().includes('gestão de apólice') || 
                                                        text.toLowerCase().includes('gestao de apolice')) {
                                                        console.log('Encontrado elemento com texto:', text);
                                                        return element;
                                                    }
                                                }
                                                return null;
                                                """
                                                
                                                gestao_element = self.driver.execute_script(gestao_script)
                                                
                                                if gestao_element:
                                                    logger.info("✅ Elemento 'Gestão de Apólice' encontrado via JavaScript!")
                                                    # Clicar usando JavaScript
                                                    self.driver.execute_script("arguments[0].click();", gestao_element)
                                                    logger.info("✅ Card 'Gestão de Apólice' clicado via JavaScript!")
                                                    time.sleep(10)
                                                else:
                                                    logger.error("❌ Nenhum elemento encontrado!")
                                                    self.redirect_to_gestao_apolice()
                                                    return
                                                    
                                            except Exception as method3_error:
                                                logger.warning(f"⚠️ Método 3 falhou: {method3_error}")
                                                self.redirect_to_gestao_apolice()
                                                return
                                    
                                    # Verificar se chegou na página correta
                                    current_url = self.driver.current_url
                                    logger.info(f"📍 URL atual após clique: {current_url}")
                                    
                                    if "administracao-de-apolices" in current_url or "corretoronline" in current_url:
                                        logger.info("🎉 SUCESSO! Página de Gestão de Apólice carregada!")
                                        
                                        # Aguardar carregamento completo da página
                                        logger.info("⏳ Aguardando carregamento completo da página...")
                                        time.sleep(15)
                                        
                                        # CLICAR E COLAR NO CAMPO ESPECÍFICO
                                        logger.info("🎯 CLICANDO E COLANDO NO CAMPO ESPECÍFICO...")
                                        
                                        try:
                                            # ESTRATÉGIA AGRESSIVA: Procurar por qualquer campo de input e preencher
                                            logger.info("🎯 ESTRATÉGIA AGRESSIVA: Procurando por qualquer campo de input...")
                                            
                                            # JavaScript para encontrar e preencher qualquer campo de input
                                            fill_script = """
                                            // Procurar por qualquer input na página
                                            var inputs = document.querySelectorAll('input');
                                            var filled = false;
                                            
                                            for (var i = 0; i < inputs.length; i++) {
                                                var input = inputs[i];
                                                var type = input.type.toLowerCase();
                                                
                                                // Pular inputs que não são de texto
                                                if (type === 'hidden' || type === 'submit' || type === 'button' || type === 'checkbox' || type === 'radio') {
                                                    continue;
                                                }
                                                
                                                // Focar no input
                                                input.focus();
                                                
                                                // Limpar o campo
                                                input.value = '';
                                                
                                                // Preencher com o valor
                                                input.value = '60146757';
                                                
                                                // Disparar todos os eventos possíveis
                                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                                input.dispatchEvent(new Event('blur', { bubbles: true }));
                                                input.dispatchEvent(new Event('keydown', { bubbles: true }));
                                                input.dispatchEvent(new Event('keyup', { bubbles: true }));
                                                input.dispatchEvent(new Event('keypress', { bubbles: true }));
                                                
                                                filled = true;
                                                console.log('Campo preenchido:', input.placeholder || input.name || input.id);
                                                break;
                                            }
                                            
                                            if (!filled) {
                                                // Se não encontrou input, tentar textarea
                                                var textareas = document.querySelectorAll('textarea');
                                                for (var i = 0; i < textareas.length; i++) {
                                                    var textarea = textareas[i];
                                                    textarea.focus();
                                                    textarea.value = '';
                                                    textarea.value = '60146757';
                                                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                                                    textarea.dispatchEvent(new Event('change', { bubbles: true }));
                                                    filled = true;
                                                    console.log('Textarea preenchida:', textarea.placeholder || textarea.name || textarea.id);
                                                    break;
                                                }
                                            }
                                            
                                            return filled ? 'Campo preenchido com 60146757' : 'Nenhum campo encontrado';
                                            """
                                            
                                            result = self.driver.execute_script(fill_script)
                                            logger.info(f"✅ JavaScript executado: {result}")
                                            
                                            if "Nenhum campo encontrado" in result:
                                                logger.warning("⚠️ Nenhum campo encontrado, tentando método alternativo...")
                                                
                                                # Método alternativo: procurar por elementos editáveis
                                                alt_script = """
                                                // Procurar por qualquer elemento que aceite texto
                                                var elements = document.querySelectorAll('input, textarea, [contenteditable="true"]');
                                                var filled = false;
                                                
                                                for (var i = 0; i < elements.length; i++) {
                                                    var element = elements[i];
                                                    
                                                    // Focar no elemento
                                                    element.focus();
                                                    
                                                    // Limpar
                                                    element.value = '';
                                                    element.textContent = '';
                                                    
                                                    // Preencher
                                                    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                                                        element.value = '60146757';
                                                    } else {
                                                        element.textContent = '60146757';
                                                    }
                                                    
                                                    // Disparar eventos
                                                    element.dispatchEvent(new Event('input', { bubbles: true }));
                                                    element.dispatchEvent(new Event('change', { bubbles: true }));
                                                    element.dispatchEvent(new Event('blur', { bubbles: true }));
                                                    
                                                    filled = true;
                                                    console.log('Elemento preenchido:', element.tagName, element.placeholder || element.name || element.id);
                                                    break;
                                                }
                                                
                                                return filled ? 'Elemento preenchido com 60146757' : 'Nenhum elemento encontrado';
                                                """
                                                
                                                alt_result = self.driver.execute_script(alt_script)
                                                logger.info(f"✅ Método alternativo: {alt_result}")
                                            
                                        except Exception as fill_error:
                                            logger.error(f"❌ ERRO AO PREENCHER CAMPO: {fill_error}")
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