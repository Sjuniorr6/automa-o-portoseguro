from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fecha o navegador aberto pela automação'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔒 Fechando navegador...')
        )
        
        try:
            # Tentar importar e fechar o driver se existir
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Tentar encontrar e fechar o driver ativo
            try:
                # Listar todos os processos do Chrome
                import psutil
                
                chrome_processes = []
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'chrome' in proc.info['name'].lower():
                            chrome_processes.append(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if chrome_processes:
                    self.stdout.write(
                        self.style.WARNING(f'🔍 Encontrados {len(chrome_processes)} processos do Chrome')
                    )
                    
                    # Tentar fechar os processos
                    for pid in chrome_processes:
                        try:
                            proc = psutil.Process(pid)
                            proc.terminate()
                            self.stdout.write(
                                self.style.SUCCESS(f'✅ Processo {pid} terminado')
                            )
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    self.stdout.write(
                        self.style.SUCCESS('✅ Navegador fechado com sucesso!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Nenhum processo do Chrome encontrado')
                    )
                    
            except ImportError:
                self.stdout.write(
                    self.style.ERROR('❌ Biblioteca psutil não encontrada. Instale com: pip install psutil')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao fechar navegador: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🏁 Comando concluído!')
        ) 