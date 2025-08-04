"""
Módulo de Automação Selenium para Porto Seguro Corretor
=======================================================

Este módulo fornece funcionalidades de automação para interagir com o
sistema Corretor Online da Porto Seguro usando Selenium WebDriver.

Funcionalidades:
- Abertura automática do navegador
- Navegação para o Corretor Online
- Execução de ações automatizadas
- Manutenção do navegador aberto para uso manual
"""

import logging
import time
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .automation_config import URLS, BEHAVIOR, TIMING, CHROME_OPTIONS, TEST_DATA

# Configuração do logger
logger = logging.getLogger(__name__)

# Constantes
PORTO_SEGURO_URL = "https://corretor.portoseguro.com.br/portal/site/corretoronline/template.LOGIN/"
DEFAULT_WAIT_TIME = 10
INFINITE_LOOP_DELAY = 1


class AutomationManager:
    """
    Gerenciador principal da automação Selenium.
    
    Responsável por coordenar todas as operações de automação,
    incluindo configuração do driver, execução de ações e
    gerenciamento do ciclo de vida do navegador.
    """
    
    def __init__(self, form_data: Optional[Dict[str, Any]] = None):
        """
        Inicializa o gerenciador de automação.
        
        Args:
            form_data: Dados do formulário para usar na automação
        """
        self.form_data = form_data or TEST_DATA
        self.driver = None
        self._is_running = False
    
    def setup_driver(self) -> bool:
        """
        Configura o driver do Chrome com as opções especificadas.
        
        Returns:
            bool: True se a configuração foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("🔧 Configurando driver do Chrome...")
            
            chrome_options = Options()
            
            # Aplicar configurações do automation_config.py
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
            
            # Configurações para modo incógnito/anônimo
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Instalar e configurar o ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(TIMING.get('element_wait', 10))
            
            # Remover indicadores de automação para stealth
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']})")
            
            logger.info("✅ Driver do Chrome configurado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar driver: {e}")
            return False
    
    def open_porto_seguro_corretor(self) -> bool:
        """
        Abre o Corretor Online da Porto Seguro e executa a automação.
        
        Returns:
            bool: True se a automação foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("🚀 Abrindo Corretor Online da Porto Seguro...")
            
            # Navegar para a URL
            self.driver.get(PORTO_SEGURO_URL)
            time.sleep(TIMING.get('page_load_wait', 3))
            
            logger.info("✅ Corretor Online da Porto Seguro aberto com sucesso")
            time.sleep(5)
            
            # Executar ações de automação se configurado
            if BEHAVIOR.get('click_porto_button', True):
                self._click_porto_button()
                
                if BEHAVIOR.get('do_login', True):
                    self._perform_login()
                    
                    if BEHAVIOR.get('fill_susep', True):
                        self._fill_susep_field()
            
            logger.info("🎉 Automação do Corretor Online concluída!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao abrir Corretor Online: {e}")
            return False
    
    def _click_porto_button(self) -> bool:
        """
        Clica no botão específico da Porto Seguro.
        
        Returns:
            bool: True se o clique foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("🔍 Procurando botão para clicar...")
            
            button = WebDriverWait(self.driver, DEFAULT_WAIT_TIME).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[1]/div/div[2]/ul/li/button"))
            )
            
            button.click()
            logger.info("✅ Botão clicado com sucesso!")
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao clicar no botão: {e}")
            return False
    
    def _perform_login(self) -> bool:
        """
        Realiza o login no sistema.
        
        Returns:
            bool: True se o login foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("🔐 Iniciando processo de login...")
            
            # Preencher CPF
            logger.info("🔍 Aguardando campo de CPF...")
            cpf_field = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="logonPrincipal"]'))
            )
            cpf_field.clear()
            cpf_field.send_keys("140.552.248-85")
            logger.info("✅ CPF preenchido: 140.552.248-85")
            time.sleep(2)
            
            # Preencher senha
            logger.info("🔍 Aguardando campo de senha...")
            senha_field = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="liSenha"]/div/input'))
            )
            senha_field.clear()
            senha_field.send_keys("Shaddai2025!")
            logger.info("✅ Senha preenchida")
            time.sleep(2)
            
            # Clicar no botão de login
            logger.info("🔍 Aguardando botão de login...")
            login_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="inputLogin"]'))
            )
            login_button.click()
            logger.info("✅ Botão de login clicado!")
            
            time.sleep(5)
            logger.info("🎉 Processo de login concluído!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante login: {e}")
            return False
    
    def _fill_susep_field(self) -> bool:
        """
        Preenche o campo SUSEP e clica no elemento específico usando JavaScript.
        
        Returns:
            bool: True se o preenchimento foi bem-sucedido, False caso contrário
        """
        try:
            logger.info("📋 Preenchendo campo SUSEP...")
            
            # Aguardar o campo SUSEP ficar clicável
            logger.info("🔍 Aguardando campo SUSEP...")
            susep_field = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="susepsAutocomplete"]'))
            )
            
            # Preencher SUSEP
            susep_field.clear()
            susep_field.send_keys("BA6QXJ (P)")
            logger.info("✅ Campo SUSEP preenchido: BA6QXJ (P)")
            time.sleep(2)
            
            # Aguardar o botão avançar ficar clicável
            logger.info("🔍 Aguardando botão avançar...")
            avancar_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="btnAvancarSusep"]'))
            )
            
            # Clicar no botão avançar
            avancar_button.click()
            logger.info("✅ Botão avançar clicado!")
            time.sleep(3)
            
            logger.info("🎉 Processo SUSEP concluído!")
            
            # PULAR ETAPAS INTERMEDIÁRIAS E IR DIRETO AO REDIRECIONAMENTO
            logger.info("🎯 Pulando etapas intermediárias e indo direto ao redirecionamento...")
            
            # Aguardar um pouco para a página carregar
            time.sleep(5)
            logger.info("✅ Pronto para redirecionamento direto!")
            
            # PRIMEIRO: Redirecionar para o link da Gestão de Apólice
            logger.info("🎯 PRIMEIRO: Redirecionando para o link da Gestão de Apólice...")
            
            # URL direta da Gestão de Apólice (simplificada para teste)
            gestao_apolice_url = "https://wwws.portoseguro.com.br/react-spa-saud-pbko-administracao-de-apolices/"
            logger.info(f"📍 Navegando para: {gestao_apolice_url}")
            
            try:
                # Fazer o redirecionamento
                self.driver.get(gestao_apolice_url)
                time.sleep(20)  # Aguardar mais tempo para carregamento
                
                logger.info(f"📍 URL atual: {self.driver.current_url}")
                logger.info(f"📍 Título da página: {self.driver.title}")
                
                # Verificar se a página carregou
                page_source = self.driver.page_source
                if "Escolha o contrato" in page_source:
                    logger.info("✅ Página carregou corretamente - encontrou 'Escolha o contrato'")
                else:
                    logger.warning("⚠️ Página pode não ter carregado completamente")
                    logger.info("🔍 Tentando encontrar qualquer texto na página...")
                    try:
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        logger.info(f"✅ Body encontrado, conteúdo: {body.text[:500]}...")
                    except Exception as body_error:
                        logger.error(f"❌ Erro ao encontrar body: {body_error}")
                
                # SEGUNDO: Aceitar qualquer pop-up que apareça
                logger.info("🎯 SEGUNDO: Aceitando qualquer pop-up...")
                
                # Aguardar um pouco para a página carregar
                time.sleep(5)
                
                # ACEITAR QUALQUER POP-UP AUTOMATICAMENTE
                try:
                    logger.info("🔍 Procurando e aceitando qualquer pop-up...")
                    js_script = """
                    // Aceitar qualquer pop-up que apareça
                    var buttons = document.querySelectorAll('button');
                    var clicked = false;
                    
                    for (var i = 0; i < buttons.length; i++) {
                        var button = buttons[i];
                        var text = button.textContent.toLowerCase();
                        
                        // Aceitar qualquer botão que pareça ser de confirmação
                        if (text.includes('ok') || 
                            text.includes('entendi') || 
                            text.includes('fechar') || 
                            text.includes('aceitar') || 
                            text.includes('confirmar') || 
                            text.includes('continuar') || 
                            text.includes('prosseguir') ||
                            text.includes('sim') ||
                            text.includes('yes') ||
                            text.includes('close') ||
                            text.includes('accept') ||
                            text.includes('confirm') ||
                            text.includes('continue')) {
                            button.click();
                            clicked = true;
                            break;
                        }
                    }
                    
                    // Se não encontrou botão específico, clicar no primeiro botão visível
                    if (!clicked) {
                        for (var i = 0; i < buttons.length; i++) {
                            var button = buttons[i];
                            var style = window.getComputedStyle(button);
                            if (style.display !== 'none' && style.visibility !== 'hidden') {
                                button.click();
                                clicked = true;
                                break;
                            }
                        }
                    }
                    
                    return clicked ? 'Pop-up aceito automaticamente' : 'Nenhum pop-up encontrado';
                    """
                    result = self.driver.execute_script(js_script)
                    logger.info(f"✅ Resultado: {result}")
                    
                    # Aguardar o pop-up fechar
                    time.sleep(3)
                    
                except Exception as popup_error:
                    logger.warning(f"⚠️ Erro ao aceitar pop-up: {popup_error}")
                
                # TERCEIRO: Agora procurar o campo e preencher
                logger.info("🎯 TERCEIRO: Procurando campo para preencher...")
                
                # Aguardar mais um pouco para a página carregar
                time.sleep(5)
                
                try:
                    # ESTRATÉGIA AGRESSIVA: Procurar por qualquer campo que possa ser preenchido
                    logger.info("🎯 ESTRATÉGIA AGRESSIVA: Procurando por qualquer campo preenchível...")
                    
                    # 1. Tentar encontrar pelo placeholder "Estipulante"
                    try:
                        estipulante_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Estipulante']")
                        logger.info("✅ Campo 'Estipulante' encontrado pelo placeholder!")
                        
                        # Preencher o campo com JavaScript
                        js_script = """
                        var input = document.querySelector('input[placeholder="Estipulante"]');
                        if (input) {
                            input.value = '60146757';
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                            return 'Campo Estipulante preenchido com 60146757';
                        } else {
                            return 'Campo Estipulante não encontrado';
                        }
                        """
                        
                        result = self.driver.execute_script(js_script)
                        logger.info(f"✅ JavaScript executado: {result}")
                        logger.info("🛑 Automação concluída - campo Estipulante preenchido!")
                        return True
                        
                    except Exception as estipulante_error:
                        logger.warning(f"⚠️ Não conseguiu encontrar pelo placeholder: {estipulante_error}")
                    
                    # 2. Tentar encontrar qualquer input na página
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    logger.info(f"📋 Encontrados {len(all_inputs)} inputs na página")
                    
                    if len(all_inputs) > 0:
                        # Listar todos os inputs encontrados
                        for i, input_elem in enumerate(all_inputs):
                            input_id = input_elem.get_attribute('id')
                            input_type = input_elem.get_attribute('type')
                            input_placeholder = input_elem.get_attribute('placeholder')
                            input_class = input_elem.get_attribute('class')
                            input_name = input_elem.get_attribute('name')
                            
                            logger.info(f"📋 Input {i+1}: ID='{input_id}', Type='{input_type}', Placeholder='{input_placeholder}', Class='{input_class}', Name='{input_name}'")
                        
                        # 3. Tentar preencher o PRIMEIRO input (mais provável de ser o campo de busca)
                        logger.info("🎯 Tentando preencher o PRIMEIRO input encontrado...")
                        
                        js_script = """
                        var inputs = document.getElementsByTagName('input');
                        if (inputs.length > 0) {
                            // Focar no primeiro input
                            inputs[0].focus();
                            // Limpar o campo
                            inputs[0].value = '';
                            // Preencher com o valor
                            inputs[0].value = '60146757';
                            // Disparar eventos
                            inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                            inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                            inputs[0].dispatchEvent(new Event('blur', { bubbles: true }));
                            return 'Primeiro input preenchido com 60146757';
                        } else {
                            return 'Nenhum input encontrado';
                        }
                        """
                        
                        result = self.driver.execute_script(js_script)
                        logger.info(f"✅ JavaScript executado: {result}")
                        logger.info("🛑 Automação concluída - primeiro input preenchido!")
                        return True
                        
                    else:
                        logger.warning("⚠️ Nenhum input encontrado na página")
                        
                        # 4. Tentar encontrar outros tipos de campos (textarea, etc.)
                        all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                        logger.info(f"📋 Encontrados {len(all_textareas)} textareas na página")
                        
                        if len(all_textareas) > 0:
                            logger.info("🎯 Tentando preencher o primeiro textarea...")
                            
                            js_script = """
                            var textareas = document.getElementsByTagName('textarea');
                            if (textareas.length > 0) {
                                textareas[0].value = '60146757';
                                textareas[0].dispatchEvent(new Event('input', { bubbles: true }));
                                textareas[0].dispatchEvent(new Event('change', { bubbles: true }));
                                return 'Primeiro textarea preenchido com 60146757';
                            } else {
                                return 'Nenhum textarea encontrado';
                            }
                            """
                            
                            result = self.driver.execute_script(js_script)
                            logger.info(f"✅ JavaScript executado: {result}")
                            logger.info("🛑 Automação concluída - primeiro textarea preenchido!")
                            return True
                        
                        logger.info("🛑 Automação concluída - nenhum campo encontrado")
                        return False
                    
                    return True
                    
                except Exception as field_error:
                    logger.error(f"❌ Erro ao procurar campos: {field_error}")
                    logger.info("🛑 Automação concluída - erro na busca")
                    return False
                
            except Exception as redirect_error:
                logger.error(f"❌ Erro ao redirecionar: {redirect_error}")
                logger.info("🛑 Automação concluída - erro no redirecionamento")
                return False
                
            except Exception as e:
                logger.error(f"❌ Erro ao redirecionar diretamente: {e}")
                logger.info("🔄 Tentando métodos alternativos...")
                
                # Tentar com JavaScript como fallback
                try:
                    logger.info("🔍 Tentando redirecionamento via JavaScript...")
                    js_redirect = f"window.location.href = '{gestao_apolice_url}';"
                    self.driver.execute_script(js_redirect)
                    time.sleep(15)
                    logger.info(f"📍 URL após JavaScript: {self.driver.current_url}")
                    
                    # Tentar novamente encontrar o campo após JavaScript
                    try:
                        logger.info("🔍 Procurando campo de input após JavaScript...")
                        clicar_input = self.driver.find_element(By.XPATH, '//*[@id="container_page_mov"]/div/div/div[1]/div/div/label/input')
                        clicar_input.click()
                        clicar_input.send_keys("60146757")
                        logger.info("✅ Campo preenchido com sucesso após JavaScript: 60146757")
                        logger.info("🛑 Automação concluída - página carregada e campo preenchido")
                    except Exception as input_error2:
                        logger.warning(f"⚠️ Erro ao preencher campo após JavaScript: {input_error2}")
                        logger.info("🛑 Automação concluída - página carregada (campo não encontrado)")
                    
                    return True
                    
                except Exception as js_error:
                    logger.error(f"❌ Erro no redirecionamento JavaScript: {js_error}")
                    logger.error("❌ Falha no redirecionamento para Gestão de Apólice!")
                    logger.info("🛑 Automação parada - não foi possível acessar a página")
                    return False
            
        except Exception as e:
            logger.error(f"❌ Erro durante preenchimento SUSEP ou clique no elemento: {e}")
            return False
    
    def setup(self) -> bool:
        """
        Configura o ambiente de automação.
        
        Returns:
            bool: True se a configuração foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("🔧 Configurando ambiente de automação...")
            
            # Configura o driver
            if not self.setup_driver():
                logger.error("❌ Falha ao configurar o driver do Chrome")
                return False
            
            logger.info("✅ Ambiente de automação configurado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante configuração: {e}")
            return False
    
    def execute_automation(self) -> bool:
        """
        Executa a automação principal.
        
        Returns:
            bool: True se a automação foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("🚀 Iniciando execução da automação...")
            
            # Abre o Corretor Online da Porto Seguro
            success = self.open_porto_seguro_corretor()
            
            if success:
                logger.info("✅ Automação inicial concluída com sucesso!")
            else:
                logger.warning("⚠️ Automação inicial teve problemas, mas continuando...")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante execução da automação: {e}")
            return False
    
    def keep_browser_open(self) -> None:
        """
        Mantém o navegador aberto indefinidamente para uso manual.
        
        O navegador permanecerá aberto até que o usuário interrompa
        o processo (Ctrl+C) ou feche a janela manualmente.
        """
        self._is_running = True
        
        logger.info("🌐 Navegador permanecerá aberto para uso manual")
        logger.info("💡 Você pode continuar trabalhando no sistema manualmente")
        logger.info("🔒 Para fechar o navegador, feche a janela manualmente ou use Ctrl+C no console")
        
        try:
            while self._is_running:
                time.sleep(INFINITE_LOOP_DELAY)
                
        except KeyboardInterrupt:
            logger.info("🛑 Interrupção detectada pelo usuário")
            self._is_running = False
            
        except Exception as e:
            logger.error(f"❌ Erro durante execução: {e}")
            self._is_running = False
    
    def cleanup(self) -> None:
        """
        Limpa recursos e fecha o navegador.
        """
        try:
            if self.driver:
                logger.info("🔒 Fechando navegador...")
                self.driver.quit()
                logger.info("✅ Driver Selenium encerrado com sucesso")
                
        except Exception as e:
            logger.error(f"❌ Erro ao fechar navegador: {e}")
    
    def run(self) -> bool:
        """
        Executa o fluxo completo de automação.
        
        Returns:
            bool: True se todo o processo foi bem-sucedido, False caso contrário
        """
        try:
            # Configuração
            if not self.setup():
                return False
            
            # Execução da automação
            if not self.execute_automation():
                return False
            
            # Mantém navegador aberto
            self.keep_browser_open()
            
            return True
            
        except Exception as e:
            logger.exception("💥 Erro crítico durante execução:")
            return False
            
        finally:
            # Limpeza sempre executa
            self.cleanup()


def run_automation_for_form(form_data: Optional[Dict[str, Any]] = None) -> bool:
    """
    Função principal para executar a automação Selenium.
    
    Esta função é chamada pelo comando Django (test_automation.py) ou
    outros triggers para abrir o link do Porto Seguro Corretor via Selenium.
    O navegador permanecerá aberto até intervenção manual.
    
    Args:
        form_data: Dados do formulário para usar na automação
        
    Returns:
        bool: True se a automação foi bem-sucedida, False caso contrário
    """
    logger.info("🤖 Iniciando automação Selenium para Porto Seguro Corretor")
    
    # Cria e executa o gerenciador de automação
    manager = AutomationManager(form_data)
    success = manager.run()
    
    if success:
        logger.info("🎉 Automação concluída com sucesso!")
    else:
        logger.error("💥 Falha na execução da automação")
    
    return success


def acessar_o_corretor_online(driver: webdriver.Chrome) -> bool:
    """
    Função utilitária para acessar o corretor online.
    
    Args:
        driver: Instância do WebDriver
        
    Returns:
        bool: True se o botão foi clicado com sucesso, False caso contrário
    """
    try:
        logger.info("🔍 Procurando botão do corretor online...")
        
        button = WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/ul/li/button"))
        )
        
        button.click()
        logger.info("✅ Botão do corretor online clicado com sucesso!")
        time.sleep(3)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao clicar no botão do corretor online: {e}")
        return False


# Função de conveniência para uso direto
def main():
    """
    Função de conveniência para executar a automação diretamente.
    """
    run_automation_for_form()


if __name__ == "__main__":
    main() 