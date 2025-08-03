from django.core.management.base import BaseCommand
from formulario2.automation import run_automation_for_form
from formulario2.automation_config import TEST_DATA
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Testa a automação Selenium manualmente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--form-id',
            type=int,
            help='ID do formulário para usar na automação (opcional)',
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Executar em modo headless (sem interface gráfica)',
        )
        parser.add_argument(
            '--no-fill',
            action='store_true',
            help='Não preencher o formulário automaticamente',
        )
        parser.add_argument(
            '--close-browser',
            action='store_true',
            help='Fechar o navegador após a execução',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Iniciando teste da automação Selenium...')
        )
        
        # Preparar dados para a automação
        if options['form_id']:
            try:
                from formulario2.models import Formulario2
                formulario = Formulario2.objects.get(id=options['form_id'])
                
                form_data = {
                    'id': formulario.id,
                    'nomeCompleto': formulario.nomeCompleto,
                    'nomeSocial': formulario.nomeSocial or '',
                    'dataNascimento': formulario.dataNascimento.strftime('%Y-%m-%d') if formulario.dataNascimento else None,
                    'genero': formulario.genero,
                    'estadoCivil': formulario.estadoCivil,
                    'rg': formulario.rg,
                    'cpf': formulario.cpf,
                    'orgaoEmissor': formulario.orgaoEmissor,
                    'dataEmissao': formulario.dataEmissao.strftime('%Y-%m-%d') if formulario.dataEmissao else None,
                    'telefone': formulario.telefone,
                    'email': formulario.email,
                    'nomeMae': formulario.nomeMae,
                }
                
                self.stdout.write(
                    self.style.SUCCESS(f'📋 Usando dados do formulário ID: {formulario.id} - {formulario.nomeCompleto}')
                )
                
            except Formulario2.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Formulário com ID {options["form_id"]} não encontrado. Usando dados de teste.')
                )
                form_data = TEST_DATA
        else:
            form_data = TEST_DATA
            self.stdout.write(
                self.style.WARNING('⚠️ Usando dados de teste para a automação')
            )
        
        # Aplicar configurações personalizadas
        if options['headless']:
            from formulario2.automation_config import CHROME_OPTIONS
            CHROME_OPTIONS['headless'] = True
            self.stdout.write('🔧 Modo headless ativado')
        
        if options['no_fill']:
            from formulario2.automation_config import BEHAVIOR
            BEHAVIOR['fill_form'] = False
            self.stdout.write('🔧 Preenchimento automático desativado')
        
        # SEMPRE manter o navegador aberto, independente da opção
        from formulario2.automation_config import BEHAVIOR
        BEHAVIOR['close_browser'] = False
        self.stdout.write('🔧 Navegador SEMPRE será mantido aberto')
        
        if options['close_browser']:
            self.stdout.write('⚠️ Opção --close-browser ignorada - navegador permanecerá aberto')
        
        # Executar automação
        try:
            success = run_automation_for_form(form_data)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Automação executada com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Falha na execução da automação')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'💥 Erro durante a automação: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🏁 Teste da automação concluído!')
        )
        
        # MANTER O PROCESSO VIVO PARA PRESERVAR O NAVEGADOR
        self.stdout.write(
            self.style.WARNING('🔄 MANTENDO PROCESSO VIVO - Navegador permanecerá aberto!')
        )
        self.stdout.write(
            self.style.WARNING('💡 Para fechar o navegador, feche esta janela do terminal ou pressione Ctrl+C')
        )
        
        # Aguardar input do usuário para manter o processo vivo
        try:
            input("Pressione Enter para fechar o navegador ou deixe esta janela aberta...")
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('👋 Navegador será fechado...')
            ) 