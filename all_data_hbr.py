import requests
import time
import random
from bs4 import BeautifulSoup
import json
from colorama import Fore, init
import logging
import dbs


db = dbs.DatabaseManager('./hbr.db')
start_time = time.time()
init(autoreset=True)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '_ym_uid=1712729898894970247; _ym_d=1712729898; hl=ru; fl=ru; habr_uuid=bmQ4b3VSa2FVaml6d0JPYWozbFh0bFNMWUkxV3Q4MVAvUUhGY1Z3SGZqdnF2RWpSd0dXUkdKMXRRMjQxYS85dA%3D%3D; split_version=triger; habr_web_home_feed=/articles/; _ga_VMM2ZGEV9D=GS1.1.1713448168.1.0.1713448168.0.0.0; _ga_EDKVH06JKZ=GS1.1.1713447548.1.1.1713448661.0.0.0; visited_articles=504952:689520:810041:691876:493580:759164:743628:714266:590067; _ga_7JGBT7D9D9=GS1.1.1714117408.1.0.1714117408.0.0.0; _ga=GA1.1.1373680956.1712729898; _ym_isad=2; _ga_S28W1WC23F=GS1.1.1714416398.21.1.1714416436.22.0.1975883177',
    'DNT': '1',
    'Host': 'habr.com',
    'If-None-Match': 'W/"46ba7-l7AVnmsjclj6XMX51Ouyb/FMqkY"',
    'Referer': 'https://www.yandex.ru/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '0',
    'sec-ch-ua-platform': "Linux"
}


def get_to_html():
    urls = [
        'https://habr.com/ru/search/?q=python&target_type=posts&order=relevance',
        'https://habr.com/ru/hubs/python/articles/']
    for url in urls:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        pagination = soup.find_all('a', class_='tm-pagination__page')
        print(pagination[-1].text)
        for i in range(1, int(pagination[-1].text) + 1):
            time.sleep(random.randrange(1, 3))
            if 'search' in url:
                print(f'[+] Page_search {i} complete!')
                response = requests.get(
                    url=f'https://habr.com/ru/search/page{i}/?q=python&target_type=posts&order=relevance',
                    headers=headers)
                with open(f'habr/habr_search_page{i}.html', 'w', encoding='utf-8') as file:
                    file.write(response.text)
            else:
                print(f'[+] Page_tags {i} complete!')
                response = requests.get(url=f'https://habr.com/ru/hubs/python/articles/page{i}', headers=headers)
                with open(f'habr/habr_tags_page{i}.html', 'w', encoding='utf-8') as file:
                    file.write(response.text)


def parsing_to_html():
    paths = ['habr/habr_search_page1.html', 'habr/habr_tags_page1.html']
    title_and_link_tags = {}
    title_and_link_search = {}
    for path in paths:
        with open(path, encoding='utf-8')as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        pagination = soup.find_all('a', class_='tm-pagination__page')
        for i in range(1, int(pagination[-1].text) + 1):
            if 'search' in path:
                print(f'[+] Page_search {i} complete!')
                with open(f'habr/habr_search_page{i}.html', encoding='utf-8')as file:
                    src = file.read()
                soup = BeautifulSoup(src, 'lxml')
                all_title = soup.find_all('a', class_='tm-title__link')
                for item in all_title:
                    item_text = item.text
                    link = 'https://habr.com' + item.get('href')
                    title_and_link_search[item_text] = link
            else:
                print(f'[+] Page_tags {i} complete!')
                with open(f'habr/habr_tags_page{i}.html')as file:
                    src = file.read()
                soup = BeautifulSoup(src, 'lxml')
                all_title = soup.find_all('a', class_='tm-title__link')
                for item in all_title:
                    item_text = item.text
                    link = 'https://habr.com' + item.get('href')
                    title_and_link_tags[item_text] = link

    title_and_link_search.update(title_and_link_tags)
    with open('habr/title_link.json', 'w') as file:
        json.dump(title_and_link_search, file, indent=4, ensure_ascii=False)


def parsing_news_to_db():
    with open('title_link.json') as file:
        src = json.load(file)
    num = len(src)
    print(f'[+] News {num} found!')
    get_to_continue = db.fetchall('SELECT title FROM news')
    get_to_continue = [x[0] for x in get_to_continue]
    for i, v in src.items():
        print(f'[+] News "{i}" append!')
        if i in get_to_continue:
            print('[+] News already in database: ' + Fore.YELLOW + f'{i}')
        else:
            try:
                time.sleep(random.randrange(1, 3))
                print('[-] News is not in database: ' + Fore.BLUE + f'{i}')
                response = requests.get(url=v, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'lxml')
                try:
                    title = soup.find('h1', class_='tm-title tm-title_h1').text
                    body = soup.find(
                        'div',
                        class_='article-formatted-body article-formatted-body article-formatted-body_version-2').text
                    date = soup.find('time')
                    date = date.get('datetime')
                except AttributeError:
                    title = soup.find('h1', class_='tm-title tm-title_h1').text
                    body = soup.find(
                        'div',
                        class_='article-formatted-body article-formatted-body article-formatted-body_version-1').text
                    date = soup.find('time')
                    date = date.get('datetime')
                db.query('INSERT INTO news (title, body, link, date) VALUES (?, ?, ?, ?)', (title, body, v, date))
                print(Fore.GREEN + f'[+] News "{i}" complete!')
                logging.info(f'[+] News "{i}" complete!')
            except Exception as ex:
                print(Fore.RED + f'[!] Error "{i}"')
                logging.info(f'[!] Error "{i}"')
                db.query('INSERT INTO news_err (title, link, exception) VALUES (?, ?, ?)', (i, v, str(ex)))


def main():
    try:
        format = ('%(asctime)s - [%(levelname)s] - %(message)s')
        db.create_tables()
        logging.basicConfig(level=logging.INFO, format=format, filename="lgs_hbr.txt")
        # get_to_html()
        # parsing_to_html()
        parsing_news_to_db()
    except Exception as e:
        logging.exception(e)
    finish_time = time.time() - start_time
    print(finish_time)
    logging.info('!!! [+++] Parsing complete !!!')


if __name__ == '__main__':
    main()
