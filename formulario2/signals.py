from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import Formulario2, AutomationLog
from .automation import run_automation_for_form
import threading
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Formulario2)
def trigger_automation_on_form_save(sender, instance, created, **kwargs):
    """
    Signal que dispara a automação Selenium quando um formulário é salvo
    """
    if created:  # Só executa para novos registros
        try:
            logger.info(f"🚀 Formulário salvo! Iniciando automação para: {instance.nomeCompleto}")
            
            # Criar log de automação no banco
            automation_log = AutomationLog.objects.create(
                formulario=instance,
                status='pending',
                automation_data={
                    'form_id': instance.id,
                    'form_name': instance.nomeCompleto,
                    'triggered_at': timezone.now().isoformat()
                }
            )
            
            # Preparar dados do formulário para JSON
            form_data = {
                'id': instance.id,
                'nomeCompleto': instance.nomeCompleto,
                'nomeSocial': instance.nomeSocial or '',
                'dataNascimento': instance.dataNascimento.strftime('%Y-%m-%d') if instance.dataNascimento else None,
                'genero': instance.genero,
                'estadoCivil': instance.estadoCivil,
                'rg': instance.rg,
                'cpf': instance.cpf,
                'orgaoEmissor': instance.orgaoEmissor,
                'dataEmissao': instance.dataEmissao.strftime('%Y-%m-%d') if instance.dataEmissao else None,
                'telefone': instance.telefone,
                'email': instance.email,
                'nomeMae': instance.nomeMae,
                'created_at': instance.pk,  # Usar o ID como timestamp de criação
            }
            
            # Executar automação em thread separada para não bloquear o salvamento
            def run_automation_async():
                try:
                    logger.info(f"🔄 Iniciando automação assíncrona para formulário ID: {instance.id}")
                    success = run_automation_for_form(form_data, automation_log)
                    
                    if success:
                        logger.info(f"✅ Automação concluída com sucesso para formulário ID: {instance.id}")
                    else:
                        logger.error(f"❌ Falha na automação para formulário ID: {instance.id}")
                        
                except Exception as e:
                    logger.error(f"💥 Erro na automação assíncrona: {e}")
                    # Atualizar log com erro
                    automation_log.status = 'failed'
                    automation_log.error_message = str(e)
                    automation_log.save()
            
            # Iniciar thread da automação
            automation_thread = threading.Thread(target=run_automation_async)
            automation_thread.daemon = True  # Thread será encerrada quando o programa principal terminar
            automation_thread.start()
            
            logger.info(f"📋 Automação iniciada em background para formulário ID: {instance.id}")
            
        except Exception as e:
            logger.error(f"💥 Erro ao disparar automação: {e}")

@receiver(post_save, sender=Formulario2)
def log_form_save(sender, instance, created, **kwargs):
    """
    Signal para logar o salvamento do formulário
    """
    if created:
        logger.info(f"📝 Novo formulário criado - ID: {instance.id}, Nome: {instance.nomeCompleto}")
    else:
        logger.info(f"📝 Formulário atualizado - ID: {instance.id}, Nome: {instance.nomeCompleto}") 