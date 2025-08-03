# 🤖 Sistema de Automação Selenium

Este sistema implementa automação Selenium que é disparada automaticamente quando um formulário é salvo no Django.

## 🚀 Como Funciona

1. **Trigger Automático**: Quando um formulário é salvo, um signal do Django dispara automaticamente a automação
2. **Execução Assíncrona**: A automação roda em uma thread separada para não bloquear o salvamento
3. **Logs Completos**: Todos os passos são registrados no banco de dados e em arquivos JSON
4. **Screenshots**: Capturas de tela são tiradas automaticamente
5. **Configurável**: Comportamento totalmente personalizável via arquivo de configuração

## 📁 Estrutura dos Arquivos

```
formulario2/
├── automation.py          # Classe principal da automação
├── automation_config.py   # Configurações personalizáveis
├── signals.py            # Signals do Django para trigger automático
├── models.py             # Modelo AutomationLog
├── management/
│   └── commands/
│       └── test_automation.py  # Comando para testar manualmente
└── templates/
    └── formulario2/
        └── automation_logs.html  # Interface para visualizar logs
```

## ⚙️ Configuração

### Arquivo `automation_config.py`

Personalize o comportamento da automação editando este arquivo:

```python
# URLs do sistema
URLS = {
    'formulario_create': 'http://127.0.0.1:8000/formulario2/create/',
    'formulario_list': 'http://127.0.0.1:8000/formulario2/',
    'automation_logs': 'http://127.0.0.1:8000/formulario2/automation-logs/',
    'api_viewer': 'http://127.0.0.1:8000/formulario2/api-viewer/',
}

# Comportamentos da automação
BEHAVIOR = {
    'fill_form': True,        # Preencher formulário automaticamente
    'navigate_pages': True,   # Navegar pelas páginas do sistema
    'take_screenshots': True, # Tirar screenshots
    'submit_form': False,     # Não submeter formulário automaticamente
    'close_browser': True,    # Fechar navegador ao finalizar
}

# Configurações do Chrome
CHROME_OPTIONS = {
    'headless': False,        # True para executar sem interface
    'window_size': '1920,1080',
}
```

## 🧪 Testando a Automação

### 1. Teste Automático
A automação é executada automaticamente quando você salva um formulário.

### 2. Teste Manual
Use o comando de gerenciamento do Django:

```bash
# Teste básico com dados de teste
python manage.py test_automation

# Teste com dados de um formulário específico
python manage.py test_automation --form-id 1

# Teste em modo headless (sem interface gráfica)
python manage.py test_automation --headless

# Teste sem preencher formulário
python manage.py test_automation --no-fill

# Combinações
python manage.py test_automation --form-id 1 --headless
```

## 📊 Visualizando Logs

### Interface Web
Acesse: `http://127.0.0.1:8000/formulario2/automation-logs/`

### Admin Django
Acesse: `http://127.0.0.1:8000/admin/` e vá para "Logs de Automação"

### Arquivos JSON
Os logs são salvos em: `formulario/logs/automation_log_YYYYMMDD_HHMMSS.json`

### Screenshots
As capturas são salvas em: `formulario/screenshots/screenshot_YYYYMMDD_HHMMSS.png`

## 🔧 Personalizando a Automação

### 1. Modificar URLs
Edite o arquivo `automation_config.py`:

```python
URLS = {
    'formulario_create': 'http://127.0.0.1:8000/formulario2/create/',
    # Adicione suas próprias URLs aqui
    'minha_pagina': 'http://127.0.0.1:8000/minha-pagina/',
}
```

### 2. Adicionar Novos Passos
Edite o método `run_automation_steps()` em `automation.py`:

```python
def run_automation_steps(self):
    # Seus passos personalizados aqui
    self.driver.get(URLS['minha_pagina'])
    # Mais lógica...
```

### 3. Modificar Comportamento
Edite `BEHAVIOR` em `automation_config.py`:

```python
BEHAVIOR = {
    'fill_form': False,      # Desabilitar preenchimento
    'navigate_pages': True,  # Manter navegação
    'custom_step': True,     # Adicionar novo comportamento
}
```

## 🐛 Solução de Problemas

### Erro: "ChromeDriver not found"
```bash
pip install webdriver-manager
```

### Erro: "Connection refused"
Certifique-se de que o servidor Django está rodando:
```bash
python manage.py runserver
```

### Automação não executa
1. Verifique se os signals estão registrados em `apps.py`
2. Confirme que o app está em `INSTALLED_APPS`
3. Verifique os logs do Django

### Screenshots não são salvos
1. Verifique permissões da pasta `screenshots/`
2. Confirme que `BEHAVIOR['take_screenshots'] = True`

## 📈 Monitoramento

### Logs em Tempo Real
```bash
# Acompanhar logs do Django
python manage.py runserver --verbosity=2
```

### Status das Automações
- **Pending**: Aguardando execução
- **Running**: Em execução
- **Completed**: Concluída com sucesso
- **Failed**: Falhou

## 🔒 Segurança

- A automação roda em thread separada
- Não bloqueia o salvamento do formulário
- Logs são salvos localmente
- Screenshots não contêm dados sensíveis

## 🚀 Próximos Passos

1. **Integração com APIs**: Conectar com APIs externas
2. **Relatórios**: Gerar relatórios automáticos
3. **Notificações**: Enviar notificações por email/Slack
4. **Agendamento**: Executar automações em horários específicos
5. **Testes**: Adicionar testes automatizados para a automação

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `formulario/logs/`
2. Consulte a documentação do Selenium
3. Teste com o comando `test_automation`

---

**Desenvolvido com ❤️ usando Django + Selenium** 