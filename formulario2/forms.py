from django import forms
from .models import Formulario2

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