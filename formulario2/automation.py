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
        
        # Script para listar opções (definido uma vez para reutilização)
        self.options_script = """
        // PROCURAR POR TODAS AS OPÇÕES POSSÍVEIS NA PÁGINA
        var options = [];
        
        // Método 1: Procurar por options com data-testid
        var optionElements = document.querySelectorAll('option[data-testid="input-select-search-options-item"]');
        for (var i = 0; i < optionElements.length; i++) {
            var option = optionElements[i];
            options.push({
                text: option.textContent,
                value: option.value,
                index: i
            });
        }
        
        // Método 2: Procurar por TODAS as options na página
        var allOptions = document.querySelectorAll('option');
        for (var i = 0; i < allOptions.length; i++) {
            var option = allOptions[i];
            options.push({
                text: option.textContent,
                value: option.value,
                index: i
            });
        }
        
        // Método 3: Procurar por elementos que parecem opções em divs
        var divOptions = document.querySelectorAll('[data-testid="input-select-search-options-box"] option');
        for (var i = 0; i < divOptions.length; i++) {
            var option = divOptions[i];
            options.push({
                text: option.textContent,
                value: option.value,
                index: i
            });
        }
        
        // Método 4: Procurar por elementos li que podem ser opções
        var liOptions = document.querySelectorAll('li[role="option"], li[data-value], li.select-option');
        for (var i = 0; i < liOptions.length; i++) {
            var li = liOptions[i];
            options.push({
                text: li.textContent,
                value: li.getAttribute('data-value') || li.textContent,
                index: i
            });
        }
        
        // Método 5: Procurar por elementos div que podem ser opções
        var divOptionElements = document.querySelectorAll('div[role="option"], div.select-option, div[data-value]');
        for (var i = 0; i < divOptionElements.length; i++) {
            var div = divOptionElements[i];
            options.push({
                text: div.textContent,
                value: div.getAttribute('data-value') || div.textContent,
                index: i
            });
        }
        
        // Método 6: Procurar por elementos span que podem ser opções
        var spanOptions = document.querySelectorAll('span[role="option"], span.select-option, span[data-value]');
        for (var i = 0; i < spanOptions.length; i++) {
            var span = spanOptions[i];
            options.push({
                text: span.textContent,
                value: span.getAttribute('data-value') || span.textContent,
                index: i
            });
        }
        
        // Método 7: Procurar por qualquer elemento com texto que pode ser opção
        var allElements = document.querySelectorAll('*');
        for (var i = 0; i < allElements.length; i++) {
            var element = allElements[i];
            var text = element.textContent || element.innerText || '';
            
            // Se tem texto e parece ser uma opção (não é muito longo)
            if (text && text.length > 0 && text.length < 100 && 
                !element.querySelector('*') && // Não tem filhos
                (element.tagName === 'DIV' || element.tagName === 'SPAN' || element.tagName === 'LI')) {
                
                options.push({
                    text: text.trim(),
                    value: element.getAttribute('data-value') || text.trim(),
                    index: i
                });
            }
        }
        
        return options;
        """
    
    def is_navigation_field(self, campo_info):
        """Verifica se o campo é uma barra de navegação do navegador"""
        try:
            # Verificar se é um campo de navegação do navegador
            name = campo_info.get('name', '').lower()
            id = campo_info.get('id', '').lower()
            className = campo_info.get('className', '').lower()
            placeholder = campo_info.get('placeholder', '').lower()
            
            # Palavras-chave que indicam campos de navegação
            nav_keywords = [
                'nav', 'navigation', 'search', 'url', 'address', 'omnibox', 
                'location', 'chrome', 'browser', 'toolbar', 'menubar'
            ]
            
            # Verificar se contém palavras-chave de navegação
            for keyword in nav_keywords:
                if (keyword in name or keyword in id or keyword in className or keyword in placeholder):
                    return True
            
            # Verificar se está em uma área específica do navegador
            if 'chrome' in className or 'browser' in className:
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar se é campo de navegação: {e}")
            return False
    
    def print_options(self, options):
        """Imprime as opções encontradas no terminal"""
        print("\n" + "="*80)
        print("📋 TODAS AS OPÇÕES ENCONTRADAS NA PÁGINA:")
        print("="*80)
        
        if len(options) > 0:
            for i, option in enumerate(options):
                print(f"{i+1}. {option['text']} (value: {option['value']})")
        else:
            print("⚠️ NENHUMA OPÇÃO ENCONTRADA!")
            print("🔍 Tentando método alternativo para encontrar opções...")
            
            # Método alternativo: procurar por elementos que apareceram após o clique
            alt_options_script = """
            // Procurar por elementos que podem ter aparecido após o clique
            var altOptions = [];
            
            // Procurar por elementos com texto que podem ser opções
            var allElements = document.querySelectorAll('*');
            for (var i = 0; i < allElements.length; i++) {
                var element = allElements[i];
                var text = element.textContent || element.innerText || '';
                
                // Se tem texto e não é muito longo
                if (text && text.length > 0 && text.length < 200 && 
                    !element.querySelector('*') && // Não tem filhos
                    element.offsetParent !== null && // Está visível
                    element.style.display !== 'none') {
                    
                    altOptions.push({
                        text: text.trim(),
                        value: element.getAttribute('data-value') || text.trim(),
                        index: i,
                        tag: element.tagName,
                        className: element.className
                    });
                }
            }
            
            return altOptions;
            """
            
            alt_options = self.driver.execute_script(alt_options_script)
            
            if len(alt_options) > 0:
                print(f"✅ Encontradas {len(alt_options)} opções alternativas:")
                for i, option in enumerate(alt_options[:20]):  # Mostrar apenas as primeiras 20
                    print(f"{i+1}. {option['text']} (tag: {option['tag']}, class: {option['className']})")
            else:
                print("❌ NENHUMA OPÇÃO ALTERNATIVA ENCONTRADA!")
        
        print("="*80)
        print(f"Total de opções encontradas: {len(options)}")
        print("="*80 + "\n")
        
        logger.info(f"✅ Encontradas {len(options)} opções no dropdown")
        
        # Tentar selecionar a opção "60146757" se encontrada
        selected = False
        for option in options:
            if "60146757" in option['text'] or "60146757" in option['value']:
                logger.info(f"🎯 Encontrada opção com '60146757': {option['text']}")
                
                try:
                    select_script = """
                    var optionElement = arguments[0];
                    optionElement.click();
                    optionElement.dispatchEvent(new Event('click', { bubbles: true }));
                    optionElement.dispatchEvent(new Event('mousedown', { bubbles: true }));
                    optionElement.dispatchEvent(new Event('mouseup', { bubbles: true }));
                    """
                    self.driver.execute_script(select_script, option)
                    logger.info(f"✅ Opção selecionada: {option['text']}")
                    selected = True
                    break
                except Exception as click_error:
                    logger.warning(f"⚠️ Erro ao clicar na opção: {click_error}")
        
        if not selected:
            logger.info("⚠️ Opção '60146757' não encontrada ou não foi possível selecionar")
        
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
            direct_url = "https://corretor.portoseguro.com.br/corretoronline/iframe?javax.portlet.ctx_iframe=url=https://wwws.portoseguro.com.br/react-spa-saud-pbko-administracao-de-apolices/?source=col%23%23document=BA6QXJ%23%23smsession=Vxx%2FB1ekUiER1f3pzT86I0rumx6Yi3ZOthEFk74STFIwbKfiUnsLnZ5iBh71DnRLkoXHkMT4oJvaLwHNWvg2YB%2Bm2WRADW4X3u1VYCvgXVKtQl7iO5S9uQfZxKs04G8Q9zQhAfgHTA2aLQRwRMQcZOAFzqZOmGADu6j0PLW2SaUOAP%2FYEhASuSlrDikYVtWFCXHnXZkM0DHBhwnjfpzjsXbbuUFoa3p2pwi%2B8fJW3415xFk8CEdjOo%2BVl2rowkuWLWBNH6vroNZIUsP%2BgD5a0GDNp4ffWgtftYPoiM5sYdVXonXc4Tc0D4r7JRPmf3b6ZysOwfrVkh%2BqA8FSfhrKdzGihpV8apNi8Z1EEqg6kZxObGZ5o25R%2Fja8q8klvsWJUJa5JXyu8kRKIXOAI88SrMGtvtbB3MTpIrIsR6dZqB4U4gb7kzt89N1U1M92QHLKjsegQnAH5Z99W5UG009GRQ35vk7jymU9B6IK4ATFoxzbkGc8ugAdoCTu%2F2orglxNBpotw0PEo1wPXBegpxkur%2FIPd5e%2FyCRjez0uOG%2F9xI4dvUv%2BhroeNkj4ftqEL930F0fUsRdFMLN0%2Bbo2SSRCfV7PCXv17%2FZbCqg2Ftf9bDSSWJ%2BQYEmvfFr1sUJoKTLnnZYVHnwsbhxqysl1pYxDk85kGEZPu%2B3Onjdg0yP60YUm0Id6OttCCUUoD9v5Mn0cPz32kIwlXwwSA6TpPXcrm0N7mNHXXWlzmsqOZ6FX7ucDwzcCCZ49c9HJFLLOkBUcB0oGF7BPJqaxs4oBDLEao4aZcGrwXs4ATlA63Xn1Z9%2B7uk26k8shmmwnBw0kbdEQUDnoT0mwhhv1HJsSpvclAcyE1TKOJ4GvkjZ7dXR4YVwH0mirN%2BCzjPKWhgWpHOfWoF6uUmZkMWleoOu8lcMTl1UY6ldRlaMgrl2GJfsryUntD97K0q28w%2FhZy7ztMiWQ94C9oyStqIbCkyjAo6S1vgLm0Tfg%2F87WPpRh5Z%2FcodPLfgOiKhcIx1l73PKPgPD3gWxV5YDbDvk3HvIGyWSZtJPwSO6zIIcfuC8AZCoRUbAzp2DINRQNbm%2F33kNz%2F8Swcaf0XtQZv7%2Bo73LQiKOgrSuurKa5w%2BPIIOkwTHZxIqQj6s7sJPU1U7o6QIfqfhuhEKN951tkhqgU3JWdl8Qp1Ub%2FT6gevlb5"
            
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
                    # ESTRATÉGIA PRECISA: Usar o XPath e data-testid específicos que o usuário forneceu
                    logger.info("🎯 ESTRATÉGIA PRECISA: Procurando campo específico via XPath e data-testid...")
                    
                    # PRIMEIRO: Tentar via XPath específico fornecido pelo usuário
                    try:
                        logger.info("🔍 Tentando via XPath específico: //*[@id=\"container_page_mov\"]/div/div/div[1]/div/div/label/input")
                        
                        # ESPERAR A PÁGINA CARREGAR COMPLETAMENTE
                        logger.info("⏳ Aguardando página carregar completamente...")
                        time.sleep(10)
                        
                        # VERIFICAR SE O CAMPO EXISTE ANTES DE TENTAR CLICAR
                        campo_element = WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//*[@id=\"container_page_mov\"]/div/div/div[1]/div/div/label/input"))
                        )
                        
                        # VERIFICAR SE É O CAMPO CORRETO COM TODAS AS INFORMAÇÕES
                        campo_info = self.driver.execute_script("""
                            var campo = arguments[0];
                            return {
                                placeholder: campo.placeholder,
                                name: campo.name,
                                id: campo.id,
                                dataTestId: campo.getAttribute('data-testid'),
                                className: campo.className,
                                type: campo.type,
                                value: campo.value,
                                isVisible: campo.offsetParent !== null,
                                isDisplayed: campo.style.display !== 'none',
                                tagName: campo.tagName
                            };
                        """, campo_element)
                        
                        logger.info(f"🔍 Informações detalhadas do campo: {campo_info}")
                        
                        # VERIFICAR SE É O CAMPO CORRETO
                        if campo_info['dataTestId'] != 'input-select-search' and campo_info['name'] != 'stipulatorData.stipulator.label':
                            logger.error(f"❌ CAMPO ERRADO ENCONTRADO! data-testid: {campo_info['dataTestId']}, name: {campo_info['name']}")
                            raise Exception("Campo incorreto encontrado")
                        
                        # VERIFICAR SE NÃO É UM CAMPO DE NAVEGAÇÃO
                        if self.is_navigation_field(campo_info):
                            logger.error(f"❌ CAMPO DE NAVEGAÇÃO DETECTADO! {campo_info}")
                            raise Exception("Campo de navegação detectado")
                        
                        logger.info("✅ Campo correto encontrado via XPath específico do usuário!")
                        
                        # GARANTIR QUE O CAMPO ESTÁ VISÍVEL E CLICÁVEL
                        if not campo_info['isVisible'] or not campo_info['isDisplayed']:
                            logger.error("❌ Campo não está visível!")
                            raise Exception("Campo não visível")
                        
                        # ROLAR ATÉ O CAMPO PARA GARANTIR QUE ESTÁ VISÍVEL
                        logger.info("🎯 Rolando até o campo...")
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", campo_element)
                        time.sleep(2)
                        
                        # CLICAR NO CAMPO USANDO JAVASCRIPT PARA GARANTIR
                        logger.info("🎯 CLICANDO NO CAMPO ESPECÍFICO VIA JAVASCRIPT...")
                        self.driver.execute_script("""
                            var campo = arguments[0];
                            campo.focus();
                            campo.click();
                            campo.dispatchEvent(new Event('mousedown', { bubbles: true }));
                            campo.dispatchEvent(new Event('mouseup', { bubbles: true }));
                            campo.dispatchEvent(new Event('click', { bubbles: true }));
                        """, campo_element)
                        time.sleep(3)
                        
                        # LIMPAR O CAMPO VIA JAVASCRIPT
                        logger.info("🧹 Limpando campo via JavaScript...")
                        self.driver.execute_script("arguments[0].value = '';", campo_element)
                        time.sleep(1)
                        
                        # VERIFICAR SE O CAMPO ESTÁ REALMENTE FOCADO
                        is_focused = self.driver.execute_script("return document.activeElement === arguments[0];", campo_element)
                        logger.info(f"🔍 Campo está focado: {is_focused}")
                        
                        if not is_focused:
                            logger.warning("⚠️ Campo não está focado, tentando focar novamente...")
                            self.driver.execute_script("arguments[0].focus();", campo_element)
                            time.sleep(1)
                            is_focused = self.driver.execute_script("return document.activeElement === arguments[0];", campo_element)
                            logger.info(f"🔍 Campo focado após segunda tentativa: {is_focused}")
                        
                        # PREENCHER O CAMPO VIA JAVASCRIPT COM VERIFICAÇÃO
                        logger.info("🎯 PREENCHENDO CAMPO VIA JAVASCRIPT...")
                        self.driver.execute_script("""
                            var campo = arguments[0];
                            campo.value = '60146757';
                            campo.dispatchEvent(new Event('input', { bubbles: true }));
                            campo.dispatchEvent(new Event('change', { bubbles: true }));
                            campo.dispatchEvent(new Event('keydown', { bubbles: true }));
                            campo.dispatchEvent(new Event('keyup', { bubbles: true }));
                            campo.dispatchEvent(new Event('keypress', { bubbles: true }));
                            console.log('Campo preenchido via JavaScript:', campo.placeholder || campo.name || campo.id);
                        """, campo_element)
                        
                        # VERIFICAR SE O VALOR FOI PREENCHIDO
                        valor_preenchido = self.driver.execute_script("return arguments[0].value;", campo_element)
                        logger.info(f"✅ Valor preenchido no campo: '{valor_preenchido}'")
                        
                        if valor_preenchido != '60146757':
                            logger.error(f"❌ VALOR NÃO FOI PREENCHIDO CORRETAMENTE! Valor atual: '{valor_preenchido}'")
                            raise Exception("Valor não foi preenchido corretamente")
                        
                        logger.info("✅ Valor '60146757' digitado via JavaScript no campo específico!")
                        time.sleep(3)
                        
                        # Agora listar as opções que apareceram
                        logger.info("📋 Listando opções após preenchimento...")
                        
                        # Listar todas as opções do dropdown
                        options = self.driver.execute_script(self.options_script)
                        self.print_options(options)
                        
                    except Exception as xpath_error:
                        logger.warning(f"⚠️ XPath específico falhou: {xpath_error}")
                        
                        # SEGUNDO: Tentar via data-testid específico
                        try:
                            logger.info("🔍 Tentando via data-testid: input-select-search")
                            campo_element = WebDriverWait(self.driver, 15).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[data-testid="input-select-search"]'))
                            )
                            logger.info("✅ Campo encontrado via data-testid!")
                            
                            # VERIFICAR SE É O CAMPO CORRETO
                            campo_info = self.driver.execute_script("""
                                var campo = arguments[0];
                                return {
                                    placeholder: campo.placeholder,
                                    name: campo.name,
                                    id: campo.id,
                                    dataTestId: campo.getAttribute('data-testid'),
                                    className: campo.className,
                                    type: campo.type,
                                    value: campo.value,
                                    isVisible: campo.offsetParent !== null,
                                    isDisplayed: campo.style.display !== 'none',
                                    tagName: campo.tagName
                                };
                            """, campo_element)
                            
                            logger.info(f"🔍 Informações do campo: {campo_info}")
                            
                            # VERIFICAR SE NÃO É UM CAMPO DE NAVEGAÇÃO
                            if self.is_navigation_field(campo_info):
                                logger.error(f"❌ CAMPO DE NAVEGAÇÃO DETECTADO! {campo_info}")
                                raise Exception("Campo de navegação detectado")
                            
                            # Clicar e preencher via Selenium - GARANTIR QUE É O CAMPO CORRETO
                            logger.info("🎯 CLICANDO NO CAMPO ESPECÍFICO DA PÁGINA...")
                            campo_element.click()
                            time.sleep(2)
                            campo_element.clear()
                            time.sleep(1)
                            
                            # Usar JavaScript para garantir que está no campo correto
                            self.driver.execute_script("""
                                var campo = arguments[0];
                                campo.focus();
                                campo.value = '60146757';
                                campo.dispatchEvent(new Event('input', { bubbles: true }));
                                campo.dispatchEvent(new Event('change', { bubbles: true }));
                                campo.dispatchEvent(new Event('keydown', { bubbles: true }));
                                campo.dispatchEvent(new Event('keyup', { bubbles: true }));
                                console.log('Campo preenchido via JavaScript:', campo.placeholder || campo.name || campo.id);
                            """, campo_element)
                            
                            logger.info("✅ Valor '60146757' digitado via JavaScript no campo específico!")
                            time.sleep(3)
                            
                            # Listar opções após preenchimento
                            logger.info("📋 Listando opções após preenchimento via data-testid...")
                            options = self.driver.execute_script(self.options_script)
                            self.print_options(options)
                            
                        except Exception as testid_error:
                            logger.warning(f"⚠️ data-testid falhou: {testid_error}")
                            
                            # TERCEIRO: Tentar via name específico
                            try:
                                logger.info("🔍 Tentando via name: stipulatorData.stipulator.label")
                                campo_element = WebDriverWait(self.driver, 15).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="stipulatorData.stipulator.label"]'))
                                )
                                logger.info("✅ Campo encontrado via name!")
                                
                                # VERIFICAR SE É O CAMPO CORRETO
                                campo_info = self.driver.execute_script("""
                                    var campo = arguments[0];
                                    return {
                                        placeholder: campo.placeholder,
                                        name: campo.name,
                                        id: campo.id,
                                        dataTestId: campo.getAttribute('data-testid'),
                                        className: campo.className,
                                        type: campo.type,
                                        value: campo.value,
                                        isVisible: campo.offsetParent !== null,
                                        isDisplayed: campo.style.display !== 'none',
                                        tagName: campo.tagName
                                    };
                                """, campo_element)
                                
                                logger.info(f"🔍 Informações do campo: {campo_info}")
                                
                                # VERIFICAR SE NÃO É UM CAMPO DE NAVEGAÇÃO
                                if self.is_navigation_field(campo_info):
                                    logger.error(f"❌ CAMPO DE NAVEGAÇÃO DETECTADO! {campo_info}")
                                    raise Exception("Campo de navegação detectado")
                                
                                # Clicar e preencher via Selenium - GARANTIR QUE É O CAMPO CORRETO
                                logger.info("🎯 CLICANDO NO CAMPO ESPECÍFICO DA PÁGINA...")
                                campo_element.click()
                                time.sleep(2)
                                campo_element.clear()
                                time.sleep(1)
                                
                                # Usar JavaScript para garantir que está no campo correto
                                self.driver.execute_script("""
                                    var campo = arguments[0];
                                    campo.focus();
                                    campo.value = '60146757';
                                    campo.dispatchEvent(new Event('input', { bubbles: true }));
                                    campo.dispatchEvent(new Event('change', { bubbles: true }));
                                    campo.dispatchEvent(new Event('keydown', { bubbles: true }));
                                    campo.dispatchEvent(new Event('keyup', { bubbles: true }));
                                    console.log('Campo preenchido via JavaScript:', campo.placeholder || campo.name || campo.id);
                                """, campo_element)
                                
                                logger.info("✅ Valor '60146757' digitado via JavaScript no campo específico!")
                                time.sleep(3)
                                
                                # Listar opções após preenchimento
                                logger.info("📋 Listando opções após preenchimento via name...")
                                options = self.driver.execute_script(self.options_script)
                                self.print_options(options)
                                
                            except Exception as name_error:
                                logger.warning(f"⚠️ name falhou: {name_error}")
                                
                                # QUARTO: JavaScript como último recurso
                                logger.info("🔍 ÚLTIMO RECURSO: JavaScript para encontrar o campo...")
                                
                                find_field_script = """
                                // PROCURAR PELO CAMPO ESPECÍFICO QUE O USUÁRIO QUER
                                var campo = null;
                                
                                // Método 1: Procurar pelo input com data-testid específico
                                campo = document.querySelector('input[data-testid="input-select-search"]');
                                if (campo) {
                                    console.log('Campo encontrado via data-testid:', campo);
                                    return { campo: campo, tipo: 'input-select', method: 'data-testid' };
                                }
                                
                                // Método 2: Procurar pelo input com name específico
                                campo = document.querySelector('input[name="stipulatorData.stipulator.label"]');
                                if (campo) {
                                    console.log('Campo encontrado via name:', campo);
                                    return { campo: campo, tipo: 'input-select', method: 'name' };
                                }
                                
                                // Método 3: Procurar pelo XPath específico via JavaScript
                                try {
                                    var xpath = "/html/body/div/div/div/div[1]/div/div/label/input";
                                    var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                                    campo = result.singleNodeValue;
                                    if (campo) {
                                        console.log('Campo encontrado via XPath JavaScript:', campo);
                                        return { campo: campo, tipo: 'input-select', method: 'xpath-js' };
                                    }
                                } catch (e) {
                                    console.log('Erro ao usar XPath via JavaScript:', e);
                                }
                                
                                // Método 4: Procurar por inputs que parecem ser campos de busca
                                var inputs = document.querySelectorAll('input[type="text"], input[type="search"]');
                                for (var i = 0; i < inputs.length; i++) {
                                    var input = inputs[i];
                                    if (input.offsetParent !== null && input.style.display !== 'none' && input.style.visibility !== 'hidden') {
                                        // Verificar se parece ser um campo de busca
                                        var placeholder = input.placeholder || '';
                                        var name = input.name || '';
                                        var className = input.className || '';
                                        
                                        if (placeholder.toLowerCase().includes('buscar') || 
                                            placeholder.toLowerCase().includes('search') ||
                                            name.toLowerCase().includes('search') ||
                                            className.toLowerCase().includes('search') ||
                                            className.toLowerCase().includes('select')) {
                                            console.log('Campo de busca encontrado:', input);
                                            return { campo: input, tipo: 'input-select', method: 'search-field' };
                                        }
                                    }
                                }
                                
                                // Método 5: Procurar por QUALQUER input visível na página (último recurso)
                                var allInputs = document.querySelectorAll('input');
                                for (var i = 0; i < allInputs.length; i++) {
                                    var input = allInputs[i];
                                    if (input.offsetParent !== null && input.style.display !== 'none' && input.style.visibility !== 'hidden') {
                                        console.log('Campo input visível encontrado:', input);
                                        return { campo: input, tipo: 'input-select', method: 'any-visible' };
                                    }
                                }
                                
                                return null;
                                """
                                
                                field_info = self.driver.execute_script(find_field_script)
                                
                                if field_info:
                                    logger.info(f"✅ Campo encontrado via JavaScript: {field_info['tipo']} (método: {field_info['method']})")
                                    
                                    # VERIFICAR SE É O CAMPO CORRETO
                                    campo_info = self.driver.execute_script("""
                                        var campo = arguments[0];
                                        return {
                                            placeholder: campo.placeholder,
                                            name: campo.name,
                                            id: campo.id,
                                            dataTestId: campo.getAttribute('data-testid'),
                                            className: campo.className,
                                            type: campo.type,
                                            value: campo.value,
                                            isVisible: campo.offsetParent !== null,
                                            isDisplayed: campo.style.display !== 'none',
                                            tagName: campo.tagName
                                        };
                                    """, field_info['campo'])
                                    
                                    logger.info(f"🔍 Informações do campo encontrado: {campo_info}")
                                    
                                    # VERIFICAR SE É O CAMPO CORRETO
                                    if (campo_info['dataTestId'] != 'input-select-search' and 
                                        campo_info['name'] != 'stipulatorData.stipulator.label' and
                                        field_info['method'] != 'xpath-js'):
                                        logger.warning(f"⚠️ Campo pode não ser o correto, mas vou tentar mesmo assim...")
                                    
                                    # VERIFICAR SE NÃO É UM CAMPO DE NAVEGAÇÃO
                                    if self.is_navigation_field(campo_info):
                                        logger.error(f"❌ CAMPO DE NAVEGAÇÃO DETECTADO! {campo_info}")
                                        raise Exception("Campo de navegação detectado")
                                    
                                    # ROLAR ATÉ O CAMPO
                                    logger.info("🎯 Rolando até o campo...")
                                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", field_info['campo'])
                                    time.sleep(2)
                                    
                                    # Clicar e preencher via JavaScript
                                    click_script = """
                                    var campo = arguments[0];
                                    campo.focus();
                                    campo.click();
                                    campo.dispatchEvent(new Event('mousedown', { bubbles: true }));
                                    campo.dispatchEvent(new Event('mouseup', { bubbles: true }));
                                    campo.dispatchEvent(new Event('click', { bubbles: true }));
                                    """
                                    self.driver.execute_script(click_script, field_info['campo'])
                                    logger.info("✅ Campo clicado via JavaScript!")
                                    time.sleep(3)
                                    
                                    # Verificar se o campo está focado
                                    is_focused = self.driver.execute_script("return document.activeElement === arguments[0];", field_info['campo'])
                                    logger.info(f"🔍 Campo está focado: {is_focused}")
                                    
                                    if not is_focused:
                                        logger.warning("⚠️ Campo não está focado, tentando focar novamente...")
                                        self.driver.execute_script("arguments[0].focus();", field_info['campo'])
                                        time.sleep(1)
                                    
                                    # Preencher via JavaScript
                                    type_script = """
                                    var campo = arguments[0];
                                    campo.value = '';
                                    campo.value = '60146757';
                                    campo.dispatchEvent(new Event('input', { bubbles: true }));
                                    campo.dispatchEvent(new Event('change', { bubbles: true }));
                                    campo.dispatchEvent(new Event('keydown', { bubbles: true }));
                                    campo.dispatchEvent(new Event('keyup', { bubbles: true }));
                                    campo.dispatchEvent(new Event('keypress', { bubbles: true }));
                                    campo.dispatchEvent(new Event('blur', { bubbles: true }));
                                    campo.dispatchEvent(new Event('focus', { bubbles: true }));
                                    """
                                    self.driver.execute_script(type_script, field_info['campo'])
                                    logger.info("✅ Valor '60146757' digitado via JavaScript!")
                                    time.sleep(3)
                                    
                                    # Verificar se o valor foi preenchido
                                    valor_preenchido = self.driver.execute_script("return arguments[0].value;", field_info['campo'])
                                    logger.info(f"✅ Valor preenchido no campo: '{valor_preenchido}'")
                                    
                                    if valor_preenchido != '60146757':
                                        logger.error(f"❌ VALOR NÃO FOI PREENCHIDO CORRETAMENTE! Valor atual: '{valor_preenchido}'")
                                        raise Exception("Valor não foi preenchido corretamente")
                                    
                                    # Listar opções após preenchimento via JavaScript
                                    logger.info("📋 Listando opções após preenchimento via JavaScript...")
                                    options = self.driver.execute_script(self.options_script)
                                    self.print_options(options)
                                else:
                                    logger.error("❌ Campo não encontrado por nenhum método!")
                                    return False
                                    
                except Exception as click_error:
                    logger.error(f"❌ ERRO AO CLICAR/COLAR: {click_error}")
                    
                    # Último recurso: JavaScript genérico mais específico
                    try:
                        logger.info("⚡ ÚLTIMO RECURSO: JavaScript genérico mais específico...")
                        result = self.driver.execute_script("""
                            // Procurar por qualquer campo de input visível
                            var inputs = document.querySelectorAll('input');
                            var filled = false;
                            
                            for (var i = 0; i < inputs.length; i++) {
                                var input = inputs[i];
                                if (input.offsetParent !== null && input.style.display !== 'none' && input.style.visibility !== 'hidden') {
                                    // Verificar se não é um campo de navegação
                                    var type = input.type.toLowerCase();
                                    var name = input.name || '';
                                    var id = input.id || '';
                                    var className = input.className || '';
                                    
                                    // Pular campos que parecem ser de navegação
                                    if (type === 'hidden' || type === 'submit' || type === 'button' || 
                                        name.toLowerCase().includes('nav') || 
                                        id.toLowerCase().includes('nav') ||
                                        className.toLowerCase().includes('nav') ||
                                        name.toLowerCase().includes('search') && name.toLowerCase().includes('bar') ||
                                        id.toLowerCase().includes('search') && id.toLowerCase().includes('bar')) {
                                        continue;
                                    }
                                    
                                    // Focar no input
                                    input.focus();
                                    input.click();
                                    
                                    // Limpar e preencher
                                    input.value = '';
                                    input.value = '60146757';
                                    
                                    // Disparar eventos
                                    input.dispatchEvent(new Event('input', { bubbles: true }));
                                    input.dispatchEvent(new Event('change', { bubbles: true }));
                                    input.dispatchEvent(new Event('keydown', { bubbles: true }));
                                    input.dispatchEvent(new Event('keyup', { bubbles: true }));
                                    input.dispatchEvent(new Event('keypress', { bubbles: true }));
                                    
                                    filled = true;
                                    console.log('Campo preenchido:', input.placeholder || input.name || input.id);
                                    break;
                                }
                            }
                            
                            return filled ? 'Campo preenchido com 60146757' : 'Nenhum campo adequado encontrado';
                        """)
                        logger.info(f"✅ JavaScript genérico executado: {result}")
                        
                        if "Nenhum campo adequado encontrado" in result:
                            logger.error("❌ NENHUM CAMPO ADEQUADO ENCONTRADO!")
                            return False
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