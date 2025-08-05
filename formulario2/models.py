from django.db import models

class Formulario2(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Prefiro não informar'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Solteiro'),
        ('C', 'Casado'),
        ('D', 'Divorciado'),
        ('V', 'Viúvo'),
        ('U', 'União Estável'),
    ]
    
    nomeCompleto = models.CharField(max_length=100, verbose_name="Nome Completo")
    nomeSocial = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome Social")
    dataNascimento = models.DateField(verbose_name="Data de Nascimento")
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, verbose_name="Gênero")
    rg = models.CharField(max_length=20, verbose_name="RG")
    cpf = models.CharField(max_length=14, verbose_name="CPF")
    orgaoEmissor = models.CharField(max_length=10, verbose_name="Órgão Emissor")
    dataEmissao = models.DateField(verbose_name="Data de Emissão")
    estadoCivil = models.CharField(max_length=1, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado Civil")
    telefone = models.CharField(max_length=15, verbose_name="Telefone")
    email = models.EmailField(verbose_name="Email")
    nomeMae = models.CharField(max_length=100, verbose_name="Nome da Mãe")
    
    def __str__(self):
        return self.nomeCompleto
    
    class Meta:
        verbose_name = "Formulário Porto"
        verbose_name_plural = "Formulários Porto"

class FormularioAmil(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Solteiro'),
        ('C', 'Casado'),
        ('D', 'Divorciado'),
        ('V', 'Viúvo'),
        ('U', 'União Estável'),
    ]
    
    NACIONALIDADE_CHOICES = [
        ('B', 'Brasileiro'),
        ('E', 'Estrangeiro'),
    ]
    
    # Campos obrigatórios (marcados com * na imagem)
    nome = models.CharField(max_length=100, verbose_name="Nome*")
    cpf = models.CharField(max_length=14, verbose_name="CPF*")
    nome_cartao = models.CharField(max_length=100, verbose_name="Nome no cartão*")
    data_inclusao = models.DateField(verbose_name="Data de inclusão*")
    data_registro = models.DateField(verbose_name="Data de registro*")
    data_nascimento = models.DateField(verbose_name="Data de nascimento*")
    sexo = models.CharField(max_length=1, choices=GENERO_CHOICES, verbose_name="Sexo*")
    nome_mae = models.CharField(max_length=100, verbose_name="Nome da mãe*")
    estado_civil = models.CharField(max_length=1, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado civil*")
    plano = models.CharField(max_length=100, verbose_name="Plano*")
    
    # Campos opcionais
    nacionalidade = models.CharField(max_length=1, choices=NACIONALIDADE_CHOICES, default='B', blank=True, null=True, verbose_name="Nacionalidade")
    nome_pai = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome do pai")
    contrato_dental = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contrato Dental")
    plano_dental = models.CharField(max_length=100, blank=True, null=True, verbose_name="Plano Dental")
    
    # Campos de metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Formulário Amil"
        verbose_name_plural = "Formulários Amil"
        ordering = ['-created_at']

class AutomationLog(models.Model):
    """Modelo para armazenar logs de automação"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('running', 'Executando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]
    
    formulario = models.ForeignKey(Formulario2, on_delete=models.CASCADE, related_name='automation_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    log_file_path = models.CharField(max_length=500, blank=True, null=True)
    screenshot_path = models.CharField(max_length=500, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    automation_data = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Automação {self.id} - {self.formulario.nomeCompleto} ({self.status})"
    
    class Meta:
        verbose_name = "Log de Automação"
        verbose_name_plural = "Logs de Automação"
        ordering = ['-started_at']
    