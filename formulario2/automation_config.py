# Configurações da Automação Selenium
# Personalize aqui os comportamentos da automação

# URLs do sistema
URLS = {
    'formulario_create': 'http://127.0.0.1:8000/formulario2/create/',
    'formulario_list': 'http://127.0.0.1:8000/formulario2/',
    'automation_logs': 'http://127.0.0.1:8000/formulario2/automation-logs/',
    'api_viewer': 'http://127.0.0.1:8000/formulario2/api-viewer/',
    'api_endpoint': 'http://127.0.0.1:8000/formulario2/api/',  # Endpoint da API
    'admin': 'http://127.0.0.1:8000/admin/',
    'porto_seguro_corretor': 'https://corretor.portoseguro.com.br/portal/site/corretoronline/template.LOGIN/',
    'administracao_de_apolices': 'https://corretor.portoseguro.com.br/corretoronline/iframe?javax.portlet.ctx_iframe=url=https://wwws.portoseguro.com.br/react-spa-saud-pbko-administracao-de-apolices/?source=col%23%23document=BA6QXJ%23%23smsession=KoeVr%2BJ6b95SayUEzv%2FQTCyBebyHV9wItjHn4qn%2B0pjAVw2UcfOwREHSolWIMFPkUuw9OL5PSuP0ERZvd2SsDghzES%2FMZFFtbtuMtW1Gm0%2BxVaDd1erYzJbNDWAN2RX5gb5K95EOP%2B1qcBAMHLc29TG19OLQmN1T%2FuGwx0Ll5CNJ4EdqBteMqDQI%2FrSFqYo173UFS0%2FrCgjRL2q%2BmhtzZWNz%2BASkMNJtHM%2F6sQ%2BAvLtae8bK14mNXKebGqrLKh5Xc29g0quWS3smVGn54OW76NByjYfjoXTUki5gqoDNR6CZhEGlGJSJ%2BTa5d2uYtcT1tkEuxKzOeENSmY6EAhij%2BeY6aXcc8JQN6jtFdIU853Gx9UQ1zoJSdsyFNnyzFBcyYMHINAV63tMC%2F4w%2BvtP2aAgJjkC3%2FGR9Wnf2qpuXKR29YscGbcGoCROB8kt4uuWGmIrVeQ7GccT%2B4of6qqwvtq7j46YAsjzseNyOOeJBtOytQ3VOsBcJIwMy0GsDNmnDc6hNtQHTXXSfKRJUomxStJ%2BEH6NOdZF%2FveYAw4yF74xjMK2NW5Q2iJkosb8d%2BKSTSHTWvDku%2Fu2t%2FoVy39sc8dtDIFXn8gLY0%2BU%2F%2F6VpMXswN6MZ7PRgpJ%2BxlsZ0%2FXIj6qWTis7n8ovAPbrUyupxCWLRgTWxvAqC1LjH0vh131nYtAxO%2BiGVxYjXZhw5Okxj%2FbdjAzGN76ekOIbGnCzRQi02XM1x9qEGaBMDq26awxFalq6gtbza1gwWMfAplB2C2YV9zIv2A8BKIVpdryPw34SoIKP8gn1TgF5Wh9mwdjn1JW5dGf2mHzCBjBUADoGv27ARwx6YlckKnXrEQJvKYbNiwSQO1go1z8DAfrAdDDF5cc8WWfsc8FESgPib%2Bn18SmE9Pi234l%2FegfHSd0XlDDhy8Ob33mpzDBGySRu17EIO3%2FCIT6ISUmFn735gY%2BgBPwFQX9uu7trPQJsyJttCXtcQNDQgRGSt0GMkSgYzZCXAntPz0ERiBVKOaUv8BX%2FieYHmsGgd5cViq4zZ3TISROipwn%2FbMem0QDR2HStWscdaBDHMbJvz9cpEvKXH%2FqHo%2FEHotBIKW1ILzz4TLbpJcxo6RAvmhoLE%2FH%2F8unZEIj1uWFAlwMu1t0eabrESmuzhpdAebz9EjwIRWn0dAj%2FpJgVOzqhp1%2BeH',
}

# Configurações do Chrome
CHROME_OPTIONS = {
    'headless': False,  # False para manter o navegador aberto
    'window_size': '1920,1080',
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'disable_gpu': True,
}

# Configurações de tempo (em segundos)
TIMING = {
    'page_load_wait': 3,
    'element_wait': 10,
    'form_fill_delay': 2,
    'navigation_delay': 2,
}

# Configurações de screenshots
SCREENSHOT = {
    'enabled': True,
    'directory': 'screenshots',
    'format': 'png',
}

# Configurações de logs
LOGGING = {
    'enabled': True,
    'directory': 'logs',
    'level': 'INFO',
}

# Comportamentos da automação
BEHAVIOR = {
    'fill_form': False,  # Não preencher o formulário automaticamente
    'navigate_pages': False,  # Não navegar pelas páginas do sistema
    'take_screenshots': True,  # Tirar screenshots
    'submit_form': False,  # Não submeter o formulário automaticamente
    'close_browser': False,  # Não fechar o navegador ao finalizar
    'fetch_last_api_object': True,  # Buscar último objeto da API
    'open_porto_seguro': True,  # Abrir Corretor Online da Porto Seguro
    'click_porto_button': True,  # Clicar no botão específico da Porto Seguro
    'do_login': True,  # Fazer login na Porto Seguro
}

# Dados de teste (usado se não houver dados do formulário)
TEST_DATA = {
    'nomeCompleto': 'João Silva Santos',
    'nomeSocial': 'João',
    'dataNascimento': '1990-03-15',
    'genero': 'M',
    'estadoCivil': 'S',
    'rg': '12.345.678-9',
    'cpf': '123.456.789-00',
    'orgaoEmissor': 'SSP',
    'dataEmissao': '2010-01-01',
    'telefone': '(11) 99999-9999',
    'email': 'joao@teste.com',
    'nomeMae': 'Maria Silva Santos',
} 