#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== INICIANDO TESTE DE AUTOMAÇÃO ===")

try:
    print("1. Importando bibliotecas...")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    print("✅ Bibliotecas importadas com sucesso!")
    
    print("2. Configurando Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    print("✅ Chrome configurado!")
    
    print("3. Baixando ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    print("✅ ChromeDriver baixado!")
    
    print("4. Iniciando navegador...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("✅ Navegador iniciado!")
    
    print("5. Navegando para o site...")
    driver.get("https://www.amil.com.br/empresa/#/login")
    print("✅ Site carregado!")
    
    print("6. Aguardando página carregar...")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("✅ Página carregada!")
    
    print("7. Procurando campo de login...")
    time.sleep(3)
    
    try:
        login_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]/div/div/section/section/form/div/div[1]/div/div/div/div/input')))
        print("✅ Campo de login encontrado!")
        
        print("8. Preenchendo login...")
        login_field.click()
        time.sleep(1)
        login_field.clear()
        login_field.send_keys("G2517723")
        print("✅ Login preenchido!")
        
        print("9. Procurando campo de senha...")
        senha_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]/div/div/section/section/form/div/div[2]/div[1]/div/div/div/div/input')))
        print("✅ Campo de senha encontrado!")
        
        print("10. Preenchendo senha...")
        senha_field.click()
        senha_field.send_keys('Netza240@@')
        print("✅ Senha preenchida!")
        
        print("11. Procurando botão entrar...")
        entrar_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login"]/div/div/section/section/form/div/div[3]/div[1]/div/div/button')))
        print("✅ Botão entrar encontrado!")
        
        print("12. Clicando no botão entrar...")
        entrar_button.click()
        print("✅ Login realizado!")
        
        print("13. Aguardando página carregar após login...")
        time.sleep(8)
        
        print("14. Procurando elemento do menu...")
        menu_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[2]/nav/div/ul/div[8]/div[1]')))
        print("✅ Elemento do menu encontrado!")
        
        print("15. Clicando no elemento do menu...")
        menu_element.click()
        print("✅ Elemento do menu clicado!")
        
        print("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        print("Navegador será mantido aberto. Pressione Ctrl+C para fechar.")
        
        # Manter aberto
        while True:
            time.sleep(5)
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print("Navegador será mantido aberto para inspeção.")
        while True:
            time.sleep(5)
            
except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")
    input("Pressione Enter para sair...") 