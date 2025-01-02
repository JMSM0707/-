import requests
import time
from bs4 import BeautifulSoup

API_KEY = 'YOUR_2CAPTCHA_API_KEY'  # Замените на ваш API-ключ от 2Captcha

# Функция для решения капчи
def solve_captcha(site_key, page_url):
    captcha_id = requests.post(
        f'https://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}'
    ).json()['request']

    # Ожидание решения капчи
    time.sleep(20)
    while True:
        response = requests.get(f'https://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}').json()
        if response['status'] == 1:
            return response['request']
        time.sleep(5)  # Ожидание перед следующим запросом

# Функция для загрузки аккаунтов и прокси
def load_accounts_and_proxies():
    with open('accs.txt', 'r') as acc_file:
        accounts = [line.strip() for line in acc_file if line.strip()]
    with open('proxys.txt', 'r') as prox_file:
        proxies = [line.strip() for line in prox_file if line.strip()]
    return accounts, proxies

# Основная функция
def main():
    accounts, proxies = load_accounts_and_proxies()

    for account, proxy in zip(accounts, proxies):
        username, password = account.split(':')
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }

        session = requests.Session()
        login_url = 'https://api.getgrass.io/login'  # URL логина

        # Получаем страницу для капчи
        response = session.get(login_url, proxies=proxy_dict)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Предполагаем, что site_key — это ключ капчи на странице
        site_key_div = soup.find('div', {'class': 'g-recaptcha'})
        
        if site_key_div:
            site_key = site_key_div['data-sitekey']

            # Решаем капчу
            captcha_response = solve_captcha(site_key, login_url)

            # Подготовка данных для входа
            login_data = {
                'username': username,
                'password': password,
                'g-recaptcha-response': captcha_response
            }

            # Логин на сайте
            login_response = session.post(login_url, data=login_data, proxies=proxy_dict)

            # Проверка успешного логина
            if login_response.ok:
                print(f'{username} успешно вошел')

                # Получаем np_token из cookie
                np_token = session.cookies.get('np_token')
                if np_token:
                    with open('tokens.txt', 'a') as token_file:
                        token_file.write(np_token + '\n')
                    print(f'Токен для {username}: {np_token} сохранен')
                else:
                    print(f'Не удалось получить токен для {username}')
            else:
                print(f'Ошибка входа для {username}: {login_response.text}')
        else:
            print(f'Капча не найдена для {username}')

if __name__ == "__main__":
    main()
