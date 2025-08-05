from django.contrib import admin
from .models import Formulario2, FormularioAmil, AutomationLog

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

@admin.register(FormularioAmil)
class FormularioAmilAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'plano', 'sexo', 'estado_civil', 'created_at')
    list_filter = ('sexo', 'estado_civil', 'nacionalidade', 'created_at')
    search_fields = ('nome', 'cpf', 'nome_cartao', 'plano')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'nome_cartao', 'data_nascimento', 'sexo', 'nacionalidade')
        }),
        ('Datas', {
            'fields': ('data_inclusao', 'data_registro')
        }),
        ('Informações Familiares', {
            'fields': ('nome_mae', 'nome_pai', 'estado_civil')
        }),
        ('Informações do Plano', {
            'fields': ('plano', 'contrato_dental', 'plano_dental')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
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
