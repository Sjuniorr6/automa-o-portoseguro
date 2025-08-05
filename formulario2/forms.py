from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Formulario2, FormularioAmil

class LoginForm(AuthenticationForm):
    """
    Formulário de login personalizado
    """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Usuário',
                'required': 'required'
            }
        ),
        label='Usuário'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Senha',
                'required': 'required'
            }
        ),
        label='Senha'
    )

class Formulario2Form(forms.ModelForm):
    class Meta:
        model = Formulario2
        fields = '__all__'
        widgets = {
            'nomeCompleto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome completo'
            }),
            'nomeSocial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome social (opcional)'
            }),
            'dataNascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'genero': forms.Select(attrs={
                'class': 'form-control'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu RG'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'orgaoEmissor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: SSP, DETRAN'
            }),
            'dataEmissao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estadoCivil': forms.Select(attrs={
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
            'nomeMae': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome da sua mãe'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes de erro se houver
        for field_name, field in self.fields.items():
            if field_name in self.errors:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' error'

class FormularioAmilForm(forms.ModelForm):
    class Meta:
        model = FormularioAmil
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome completo'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '999.999.999-99'
            }),
            'nome_cartao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome como aparece no cartão'
            }),
            'data_inclusao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_registro': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'sexo': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'nacionalidade': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da mãe'
            }),
            'nome_pai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do pai (opcional)'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'form-control'
            }),
            'plano': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do plano'
            }),
            'contrato_dental': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do contrato dental (opcional)'
            }),
            'plano_dental': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do plano dental (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes de erro se houver
        for field_name, field in self.fields.items():
            if field_name in self.errors:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' error' 