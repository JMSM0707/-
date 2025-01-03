import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Настройка прокси
def get_proxies(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

# Получение аккаунтов
def get_accounts(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

# Функция для решения капчи с помощью 2captcha
def solve_captcha(api_key, site_key, url):
    response = requests.post('http://2captcha.com/in.php', {
        'key': api_key,
        'method': 'userrecaptcha',
        'googlekey': site_key,
        'pageurl': url
    })
    captcha_id = response.text.split('|')[1]
    time.sleep(20)  # Подождем решения капчи
    solution_response = requests.get(f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}')
    return solution_response.text.split('|')[1]

# Основная функция для входа
def login(account, proxy):
    login_info = account.split(':')
    username, password = login_info[0], login_info[1]

    options = Options()
    options.add_argument(f'--proxy-server={proxy}')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get("https://app.getgrass.io/dashboard")
        time.sleep(3)  # Дайте время загрузки страницы

        # Вводим логин и пароль
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
        
        time.sleep(5)  # Дайте время для возможного появления капчи

        # Проверяем наличие капчи
        if "captcha" in driver.page_source:
            site_key = "здесь_должен_быть_site_key_капчи"  # нужно указать правильный site_key
            web_url = driver.current_url
            captcha_solution = solve_captcha("ваш_api_key_2captcha", site_key, web_url)
            # Вставьте решение капчи в нужное поле
        
            # (Эти шаги могут меняться в зависимости от реализации сайта, возможно, вам нужно будет отредактировать их)

        time.sleep(5)  # Дайте время на загрузку после входа

        # Получаем токен
        token = driver.execute_script("return localStorage.getItem('np_token');")

        # Сохранить токен в файл
        with open('np_token.txt', 'a') as f:
            f.write(f'{username}: {token}\n')

    finally:
        driver.quit()

def main():
    accounts = get_accounts('accs/accounts.txt')
    proxies = get_proxies('proxys/proxies.txt')

    for account, proxy in zip(accounts, proxies):
        login(account, proxy)

if __name__ == "__main__":
    main()
