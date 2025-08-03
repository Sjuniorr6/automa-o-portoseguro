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
from .ultra_stealth import UltraStealthTechniques
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
        """Configura o driver do Chrome com configurações anti-detecção ultra-avançadas"""
        try:
            chrome_options = Options()
            
            # CONFIGURAÇÕES ANTI-DETECÇÃO ULTRA-AVANÇADAS
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # CONFIGURAÇÃO PARA JANELA ANÔNIMA/PRIVADA
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # User-Agent ultra-realista
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            ]
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            # Viewport aleatório
            viewports = ["1920,1080", "1366,768", "1440,900", "1536,864", "1280,720"]
            chrome_options.add_argument(f"--window-size={random.choice(viewports)}")
            
            # Configurações de performance
            if CHROME_OPTIONS.get('no_sandbox'):
                chrome_options.add_argument("--no-sandbox")
            if CHROME_OPTIONS.get('disable_dev_shm_usage'):
                chrome_options.add_argument("--disable-dev-shm-usage")
            if CHROME_OPTIONS.get('disable_gpu'):
                chrome_options.add_argument("--disable-gpu")
            if CHROME_OPTIONS.get('headless'):
                chrome_options.add_argument("--headless")
            
            # CONFIGURAÇÕES ADICIONAIS PARA MODO ANÔNIMO
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
            
            # CONFIGURAÇÕES ANTI-DETECÇÃO ULTRA-AVANÇADAS
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
            
            # NOVAS CONFIGURAÇÕES ULTRA-AVANÇADAS
            chrome_options.add_argument("--disable-blink-features")
            chrome_options.add_argument("--disable-features=site-per-process")
            chrome_options.add_argument("--disable-site-isolation-trials")
            chrome_options.add_argument("--disable-features=BlinkGenPropertyTrees")
            chrome_options.add_argument("--disable-features=SkiaRenderer")
            chrome_options.add_argument("--disable-features=UseChromeOSDirectVideoDecoder")
            chrome_options.add_argument("--disable-features=VaapiVideoDecoder")
            chrome_options.add_argument("--disable-features=VaapiVideoEncoder")
            chrome_options.add_argument("--disable-features=VaapiVpxDecoder")
            chrome_options.add_argument("--disable-features=VaapiVpxEncoder")
            chrome_options.add_argument("--disable-features=VaapiJpegDecoder")
            chrome_options.add_argument("--disable-features=VaapiJpegEncoder")
            chrome_options.add_argument("--disable-features=VaapiWebPDecoder")
            chrome_options.add_argument("--disable-features=VaapiWebPEncoder")
            chrome_options.add_argument("--disable-features=VaapiAv1Decoder")
            chrome_options.add_argument("--disable-features=VaapiAv1Encoder")
            chrome_options.add_argument("--disable-features=VaapiH264Decoder")
            chrome_options.add_argument("--disable-features=VaapiH264Encoder")
            chrome_options.add_argument("--disable-features=VaapiH265Decoder")
            chrome_options.add_argument("--disable-features=VaapiH265Encoder")
            chrome_options.add_argument("--disable-features=VaapiVp8Decoder")
            chrome_options.add_argument("--disable-features=VaapiVp8Encoder")
            chrome_options.add_argument("--disable-features=VaapiVp9Decoder")
            chrome_options.add_argument("--disable-features=VaapiVp9Encoder")
            chrome_options.add_argument("--disable-features=VaapiHevcDecoder")
            chrome_options.add_argument("--disable-features=VaapiHevcEncoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg2Decoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg4Decoder")
            chrome_options.add_argument("--disable-features=VaapiVc1Decoder")
            chrome_options.add_argument("--disable-features=VaapiWmvDecoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg2Encoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg4Encoder")
            chrome_options.add_argument("--disable-features=VaapiVc1Encoder")
            chrome_options.add_argument("--disable-features=VaapiWmvEncoder")
            
            # Configurações de privacidade ultra-avançadas
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-component-update")
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-prompt-on-repost")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-sync-preferences")
            chrome_options.add_argument("--disable-web-resources")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-pings")
            chrome_options.add_argument("--no-zygote")
            chrome_options.add_argument("--password-store=basic")
            chrome_options.add_argument("--use-mock-keychain")
            
            # Configurações de rede ultra-avançadas
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--metrics-recording-only")
            chrome_options.add_argument("--no-report-upload")
            
            # Configurações adicionais ultra-avançadas
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-features=BlinkGenPropertyTrees")
            chrome_options.add_argument("--disable-features=SkiaRenderer")
            chrome_options.add_argument("--disable-features=UseChromeOSDirectVideoDecoder")
            chrome_options.add_argument("--disable-features=VaapiVideoDecoder")
            chrome_options.add_argument("--disable-features=VaapiVideoEncoder")
            chrome_options.add_argument("--disable-features=VaapiVpxDecoder")
            chrome_options.add_argument("--disable-features=VaapiVpxEncoder")
            chrome_options.add_argument("--disable-features=VaapiJpegDecoder")
            chrome_options.add_argument("--disable-features=VaapiJpegEncoder")
            chrome_options.add_argument("--disable-features=VaapiWebPDecoder")
            chrome_options.add_argument("--disable-features=VaapiWebPEncoder")
            chrome_options.add_argument("--disable-features=VaapiAv1Decoder")
            chrome_options.add_argument("--disable-features=VaapiAv1Encoder")
            chrome_options.add_argument("--disable-features=VaapiH264Decoder")
            chrome_options.add_argument("--disable-features=VaapiH264Encoder")
            chrome_options.add_argument("--disable-features=VaapiH265Decoder")
            chrome_options.add_argument("--disable-features=VaapiH265Encoder")
            chrome_options.add_argument("--disable-features=VaapiVp8Decoder")
            chrome_options.add_argument("--disable-features=VaapiVp8Encoder")
            chrome_options.add_argument("--disable-features=VaapiVp9Decoder")
            chrome_options.add_argument("--disable-features=VaapiVp9Encoder")
            chrome_options.add_argument("--disable-features=VaapiHevcDecoder")
            chrome_options.add_argument("--disable-features=VaapiHevcEncoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg2Decoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg4Decoder")
            chrome_options.add_argument("--disable-features=VaapiVc1Decoder")
            chrome_options.add_argument("--disable-features=VaapiWmvDecoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg2Encoder")
            chrome_options.add_argument("--disable-features=VaapiMpeg4Encoder")
            chrome_options.add_argument("--disable-features=VaapiVc1Encoder")
            chrome_options.add_argument("--disable-features=VaapiWmvEncoder")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # SCRIPTS ANTI-DETECÇÃO ULTRA-AVANÇADOS
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Configurações aleatórias de hardware
            hardware_configs = [
                {"concurrency": 8, "memory": 8, "touch_points": 0},
                {"concurrency": 4, "memory": 4, "touch_points": 0},
                {"concurrency": 16, "memory": 16, "touch_points": 0},
                {"concurrency": 12, "memory": 12, "touch_points": 0},
            ]
            hardware_config = random.choice(hardware_configs)
            self.driver.execute_script(f"Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {hardware_config['concurrency']}}})")
            self.driver.execute_script(f"Object.defineProperty(navigator, 'deviceMemory', {{get: () => {hardware_config['memory']}}})")
            self.driver.execute_script(f"Object.defineProperty(navigator, 'maxTouchPoints', {{get: () => {hardware_config['touch_points']}}})")
            
            # Configurações aleatórias de rede
            network_configs = [
                {"type": "4g", "rtt": 50, "downlink": 10},
                {"type": "wifi", "rtt": 30, "downlink": 25},
                {"type": "3g", "rtt": 100, "downlink": 5},
                {"type": "5g", "rtt": 20, "downlink": 50},
            ]
            network_config = random.choice(network_configs)
            connection_script = "Object.defineProperty(navigator, 'connection', {get: () => ({effectiveType: '" + network_config['type'] + "', rtt: " + str(network_config['rtt']) + ", downlink: " + str(network_config['downlink']) + "})})"
            self.driver.execute_script(connection_script)
            
            # Configurações aleatórias de plugins
            plugin_configs = [
                [1, 2, 3, 4, 5],
                [1, 2, 3],
                [1, 2, 3, 4, 5, 6, 7],
                [1, 2, 3, 4],
            ]
            plugin_config = random.choice(plugin_configs)
            self.driver.execute_script(f"Object.defineProperty(navigator, 'plugins', {{get: () => {plugin_config}}})")
            
            # Configurações aleatórias de linguagem
            languages = ["pt-BR", "pt", "en-US", "en"]
            language_config = random.choice(languages)
            self.driver.execute_script(f"Object.defineProperty(navigator, 'languages', {{get: () => ['{language_config}', 'pt', 'en-US', 'en']}})")
            
            # Outras configurações ultra-avançadas
            self.driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'mediaDevices', {get: () => ({getUserMedia: () => Promise.resolve()})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'})")
            self.driver.execute_script("Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})")
            self.driver.execute_script("Object.defineProperty(navigator, 'cookieEnabled', {get: () => true})")
            self.driver.execute_script("Object.defineProperty(navigator, 'doNotTrack', {get: () => null})")
            self.driver.execute_script("Object.defineProperty(navigator, 'onLine', {get: () => true})")
            self.driver.execute_script("Object.defineProperty(navigator, 'geolocation', {get: () => ({getCurrentPosition: () => Promise.resolve()})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'serviceWorker', {get: () => ({register: () => Promise.resolve()})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'storage', {get: () => ({estimate: () => Promise.resolve({usage: 1000000, quota: 10000000})})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'credentials', {get: () => ({get: () => Promise.resolve(), store: () => Promise.resolve()})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'usb', {get: () => ({getDevices: () => Promise.resolve([])})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'bluetooth', {get: () => ({requestDevice: () => Promise.resolve()})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'hid', {get: () => ({getDevices: () => Promise.resolve([])})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'serial', {get: () => ({getPorts: () => Promise.resolve([])})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'wakeLock', {get: () => ({request: () => Promise.resolve()})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'share', {get: () => ({share: () => Promise.resolve()})})")
            self.driver.execute_script("Object.defineProperty(navigator, 'canShare', {get: () => true})")
            self.driver.execute_script("Object.defineProperty(navigator, 'clearAppBadge', {get: () => () => Promise.resolve()})")
            self.driver.execute_script("Object.defineProperty(navigator, 'setAppBadge', {get: () => () => Promise.resolve()})")
            self.driver.execute_script("Object.defineProperty(navigator, 'getInstalledRelatedApps', {get: () => () => Promise.resolve([])})")
            self.driver.execute_script("Object.defineProperty(navigator, 'getUserMedia', {get: () => () => Promise.resolve()})")
            self.driver.execute_script("Object.defineProperty(navigator, 'webkitGetUserMedia', {get: () => () => Promise.resolve()})")
            self.driver.execute_script("Object.defineProperty(navigator, 'mozGetUserMedia', {get: () => () => Promise.resolve()})")
            self.driver.execute_script("Object.defineProperty(navigator, 'msGetUserMedia', {get: () => () => Promise.resolve()})")
            
            # Remover propriedades de automação do window
            self.driver.execute_script("delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;")
            self.driver.execute_script("delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;")
            self.driver.execute_script("delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;")
            
            # Simular comportamento humano ultra-avançado
            self.driver.execute_script("""
                // Simular movimentos de mouse aleatórios
                const originalMouseEvent = window.MouseEvent;
                window.MouseEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalMouseEvent(type, init);
                };
                
                // Simular eventos de teclado
                const originalKeyboardEvent = window.KeyboardEvent;
                window.KeyboardEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalKeyboardEvent(type, init);
                };
                
                // Simular eventos de foco
                const originalFocusEvent = window.FocusEvent;
                window.FocusEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalFocusEvent(type, init);
                };
                
                // Simular eventos de blur
                const originalBlurEvent = window.BlurEvent;
                window.BlurEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalBlurEvent(type, init);
                };
                
                // Simular eventos de change
                const originalChangeEvent = window.Event;
                window.ChangeEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalChangeEvent(type, init);
                };
                
                // Simular eventos de input
                const originalInputEvent = window.InputEvent;
                window.InputEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalInputEvent(type, init);
                };
                
                // Simular eventos de submit
                const originalSubmitEvent = window.Event;
                window.SubmitEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalSubmitEvent(type, init);
                };
                
                // Simular eventos de resize
                const originalResizeEvent = window.Event;
                window.ResizeEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalResizeEvent(type, init);
                };
                
                // Simular eventos de orientation
                const originalOrientationEvent = window.Event;
                window.OrientationEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalOrientationEvent(type, init);
                };
                
                // Simular eventos de visibility
                const originalVisibilityEvent = window.Event;
                window.VisibilityEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalVisibilityEvent(type, init);
                };
                
                // Simular eventos de online
                const originalOnlineEvent = window.Event;
                window.OnlineEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalOnlineEvent(type, init);
                };
                
                // Simular eventos de offline
                const originalOfflineEvent = window.Event;
                window.OfflineEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalOfflineEvent(type, init);
                };
                
                // Simular eventos de storage
                const originalStorageEvent = window.StorageEvent;
                window.StorageEvent = function(type, init) {
                    if (init && !init.isTrusted) {
                        init.isTrusted = true;
                    }
                    return new originalStorageEvent(type, init);
                };
            """)
            
            self.driver.implicitly_wait(TIMING.get('element_wait', 10))
            logger.info("Driver do Chrome configurado com sucesso (anti-detecção ultra-avançada ativada)")
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

    def human_like_delay(self, min_delay=0.5, max_delay=2.0):
        """Adiciona delay aleatório para simular comportamento humano"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        return delay
    
    def human_like_typing(self, element, text):
        """Simula digitação humana com delays aleatórios entre caracteres"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Delay entre caracteres
    
    def human_like_click(self, element):
        """Simula clique humano com movimento de mouse"""
        try:
            # Mover mouse para o elemento antes de clicar
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
            return True
        except Exception as e:
            logger.warning(f"Erro no clique humano, usando clique normal: {e}")
            element.click()
            return False
    
    def simulate_human_behavior(self):
        """Simula comportamentos humanos aleatórios"""
        try:
            # Rolar a página aleatoriamente
            scroll_amount = random.randint(100, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Rolar de volta
            self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            time.sleep(random.uniform(0.3, 0.8))
            
            # Mover mouse aleatoriamente
            actions = ActionChains(self.driver)
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y)
            actions.pause(random.uniform(0.2, 0.5))
            actions.perform()
            
        except Exception as e:
            logger.warning(f"Erro ao simular comportamento humano: {e}")
    
    def apply_anti_detection_scripts(self):
        """Aplica scripts adicionais anti-detecção ultra-avançados"""
        try:
            # Scripts para mascarar automação
            scripts = [
                # Remover propriedades de automação
                "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;",
                "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;",
                "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;",
                
                # Mascarar webdriver
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
                
                # Simular plugins
                "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});",
                
                # Simular linguagens
                "Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en-US', 'en']});",
                
                # Simular permissões
                "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});",
                
                # Simular mediaDevices
                "Object.defineProperty(navigator, 'mediaDevices', {get: () => ({getUserMedia: () => Promise.resolve()})});",
                
                # Simular connection
                "Object.defineProperty(navigator, 'connection', {get: () => ({effectiveType: '4g', rtt: 50, downlink: 10})});",
                
                # Simular hardware
                "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});",
                "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});",
                
                # Simular touch
                "Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});",
                
                # Simular vendor e platform
                "Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});",
                "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});",
                
                # Simular outras propriedades
                "Object.defineProperty(navigator, 'cookieEnabled', {get: () => true});",
                "Object.defineProperty(navigator, 'doNotTrack', {get: () => null});",
                "Object.defineProperty(navigator, 'onLine', {get: () => true});",
                
                # Simular geolocation
                "Object.defineProperty(navigator, 'geolocation', {get: () => ({getCurrentPosition: () => Promise.resolve()})});",
                
                # Simular serviceWorker
                "Object.defineProperty(navigator, 'serviceWorker', {get: () => ({register: () => Promise.resolve()})});",
                
                # Simular storage
                "Object.defineProperty(navigator, 'storage', {get: () => ({estimate: () => Promise.resolve({usage: 1000000, quota: 10000000})})});",
                
                # Simular credentials
                "Object.defineProperty(navigator, 'credentials', {get: () => ({get: () => Promise.resolve(), store: () => Promise.resolve()})});",
                
                # Simular APIs modernas
                "Object.defineProperty(navigator, 'usb', {get: () => ({getDevices: () => Promise.resolve([])})});",
                "Object.defineProperty(navigator, 'bluetooth', {get: () => ({requestDevice: () => Promise.resolve()})});",
                "Object.defineProperty(navigator, 'hid', {get: () => ({getDevices: () => Promise.resolve([])})});",
                "Object.defineProperty(navigator, 'serial', {get: () => ({getPorts: () => Promise.resolve([])})});",
                "Object.defineProperty(navigator, 'wakeLock', {get: () => ({request: () => Promise.resolve()})});",
                "Object.defineProperty(navigator, 'share', {get: () => ({share: () => Promise.resolve()})});",
                "Object.defineProperty(navigator, 'canShare', {get: () => true});",
                
                # Simular getUserMedia
                "Object.defineProperty(navigator, 'getUserMedia', {get: () => () => Promise.resolve()});",
                "Object.defineProperty(navigator, 'webkitGetUserMedia', {get: () => () => Promise.resolve()});",
                "Object.defineProperty(navigator, 'mozGetUserMedia', {get: () => () => Promise.resolve()});",
                "Object.defineProperty(navigator, 'msGetUserMedia', {get: () => () => Promise.resolve()});",
            ]
            
            for script in scripts:
                try:
                    self.driver.execute_script(script)
                except Exception as e:
                    logger.warning(f"Erro ao executar script anti-detecção: {e}")
            
            logger.info("✅ Scripts anti-detecção ultra-avançados aplicados com sucesso")
            
        except Exception as e:
            logger.warning(f"Erro ao aplicar scripts anti-detecção: {e}")

    def run_porto_seguro_automation(self):
        """Automação específica do Porto Seguro - APENAS LOGIN"""
        try:
            # 1. Acessa página de login
            porto_url = "https://corretor.portoseguro.com.br/portal/site/corretoronline/template.LOGIN/"
            logger.info("🌐 ABRINDO PORTO SEGURO CORRETOR ONLINE...")
            self.driver.get(porto_url)
            logger.info(f"✅ Página aberta: {porto_url}")
            
            # Delay humano para carregamento
            self.human_like_delay(8, 12)
            
            # Aplicar scripts anti-detecção ultra-avançados após carregamento
            UltraStealthTechniques.apply_ultra_stealth_scripts(self.driver)
            self.apply_anti_detection_scripts()
            
            # Simular comportamento humano ultra-realista
            UltraStealthTechniques.simulate_ultra_human_behavior(self.driver)
            self.simulate_human_behavior()
            
            # Tirar screenshot de debug
            if BEHAVIOR.get('take_screenshots', True):
                screenshot_path = self.take_screenshot()
                if screenshot_path:
                    logger.info(f"📸 Screenshot de debug salvo em: {screenshot_path}")
            
            # 2. Clicar no botão específico antes do login
            try:
                logger.info("🎯 CLICANDO NO BOTÃO ESPECÍFICO ANTES DO LOGIN...")
                button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[1]/div/div[2]/ul/li/button/div'))
                )
                self.human_like_click(button)
                logger.info("✅ Botão específico clicado antes do login!")
                self.human_like_delay(1.5, 3.0)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao clicar no botão pré-login: {e}")
            
            # 3. Processo de login
            logger.info("🔐 INICIANDO PROCESSO DE LOGIN...")
            
            # Preencher CPF
            logger.info("📝 Preenchendo CPF...")
            cpf_field = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="logonPrincipal"]'))
            )
            UltraStealthTechniques.ultra_human_click(self.driver, cpf_field)
            self.human_like_delay(0.5, 1.0)
            UltraStealthTechniques.ultra_human_typing(self.driver, cpf_field, '140.552.248-85')
            logger.info("✅ CPF preenchido: 140.552.248-85")
            self.human_like_delay(1.0, 2.0)
            
            # Preencher senha
            logger.info("🔒 Preenchendo senha...")
            password_field = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="liSenha"]/div/input'))
            )
            UltraStealthTechniques.ultra_human_click(self.driver, password_field)
            self.human_like_delay(0.5, 1.0)
            UltraStealthTechniques.ultra_human_typing(self.driver, password_field, 'Shaddai2025!')
            logger.info("✅ Senha preenchida")
            self.human_like_delay(1.0, 2.0)
            
            # Simular comportamento humano antes do login
            self.simulate_human_behavior()
            
            # Clicar no botão de login
            logger.info("🚀 Clicando no botão de login...")
            login_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="inputLogin"]'))
            )
            UltraStealthTechniques.ultra_human_click(self.driver, login_button)
            logger.info("✅ Botão de login clicado!")
            
            # Aguardar processamento do login
            logger.info("⏳ Aguardando processamento do login...")
            self.human_like_delay(8, 12)
            
            # Preencher código SUSEP
            logger.info("🔢 Preenchendo código SUSEP...")
            codigo1 = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="susepsAutocomplete"]'))
            )
            UltraStealthTechniques.ultra_human_click(self.driver, codigo1)
            self.human_like_delay(0.5, 1.0)
            UltraStealthTechniques.ultra_human_typing(self.driver, codigo1, 'BA6QXJ (P)')
            logger.info("✅ Código SUSEP preenchido: BA6QXJ (P)")
            self.human_like_delay(1.0, 2.0)
            
            # Clicar no botão avançar
            logger.info("➡️ Clicando no botão avançar...")
            enter = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="btnAvancarSusep"]'))
            )
            UltraStealthTechniques.ultra_human_click(self.driver, enter)
            logger.info("✅ Botão avançar clicado!")
            self.human_like_delay(8, 12)
            
            # 4. VERIFICAR SE O LOGIN FOI BEM-SUCEDIDO
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
                    
                    # Simular comportamento humano após login
                    self.simulate_human_behavior()
                    
                    # Aplicar scripts anti-detecção adicionais
                    self.apply_anti_detection_scripts()
                    
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
