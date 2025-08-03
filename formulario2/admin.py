from django.contrib import admin
from .models import Formulario2, AutomationLog

@admin.register(Formulario2)
class Formulario2Admin(admin.ModelAdmin):
    list_display = ('nomeCompleto', 'email', 'cpf', 'telefone', 'genero', 'estadoCivil')
    list_filter = ('genero', 'estadoCivil', 'dataNascimento')
    search_fields = ('nomeCompleto', 'email', 'cpf', 'rg')
    readonly_fields = ('id',)
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nomeCompleto', 'nomeSocial', 'dataNascimento', 'genero', 'estadoCivil', 'nomeMae')
        }),
        ('Documentos', {
            'fields': ('rg', 'cpf', 'orgaoEmissor', 'dataEmissao')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
    )

@admin.register(AutomationLog)
class AutomationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'formulario', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('formulario__nomeCompleto', 'formulario__email')
    readonly_fields = ('id', 'started_at', 'completed_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('formulario', 'status', 'started_at', 'completed_at')
        }),
        ('Arquivos', {
            'fields': ('log_file_path', 'screenshot_path'),
            'classes': ('collapse',)
        }),
        ('Dados da Automação', {
            'fields': ('automation_data', 'error_message'),
            'classes': ('collapse',)
        }),
    )
