import requests
import time
import random
from bs4 import BeautifulSoup
import json
from colorama import Fore, init
import logging
import dbs
from datetime import timedelta, date


db = dbs.DatabaseManager('./hbr.db')
start_time = time.time()
init(autoreset=True)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '_ym_uid=1712729898894970247; _ym_d=1712729898; hl=ru; fl=ru; habr_uuid=bmQ4b3VSa2FVaml6d0JPYWozbFh0bFNMWUkxV3Q4MVAvUUhGY1Z3SGZqdnF2RWpSd0dXUkdKMXRRMjQxYS85dA%3D%3D; split_version=triger; habr_web_home_feed=/articles/; _ga_VMM2ZGEV9D=GS1.1.1713448168.1.0.1713448168.0.0.0; _ga_EDKVH06JKZ=GS1.1.1713447548.1.1.1713448661.0.0.0; _ga_7JGBT7D9D9=GS1.1.1714117408.1.0.1714117408.0.0.0; _ga=GA1.1.1373680956.1712729898; _ym_isad=2; visited_articles=736526:498364:504952:689520:810041:691876:493580:759164:743628:714266; _ga_8F8M5R02JL=GS1.1.1714546564.4.1.1714546596.0.0.0; habr_web_hub_filter_python=/hubs/python/articles/; _ga_S28W1WC23F=GS1.1.1714546564.31.1.1714548450.55.0.175257248',
    'DNT': '1',
    'Host': 'habr.com',
    'If-None-Match': 'W/"57071-k4NzT/XQjOF+GaaprhlBM6F3mf8"',
    'Referer': 'https://yandex.ru/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '0',
    'sec-ch-ua-platform': "Linux",
}


def get_to_html():
    urls = [
        'https://habr.com/ru/search/?q=python&target_type=posts&order=date',
        'https://habr.com/ru/hubs/python/articles/']
    for url in urls:
        for i in range(1, 4):
            try:
                print(i)
                if 'search' in url:
                    print(f'[+] Page_search {i} complete!')
                    response = requests.get(
                        url=f'https://habr.com/ru/search/page{i}/?q=python&target_type=posts&order=date',
                        headers=headers,
                        timeout=10)
                    with open(f'habr/news/habr_search_page{i}.html', 'w', encoding='utf-8') as file:
                        file.write(response.text)
                else:
                    print(f'[+] Page_tags {i} complete!')
                    response = requests.get(
                        url=f'https://habr.com/ru/hubs/python/articles/page{i}',
                        headers=headers,
                        timeout=10)
                    with open(f'habr/news/habr_tags_page{i}.html', 'w', encoding='utf-8') as file:
                        file.write(response.text)
                time.sleep(random.randint(1, 3))
            except Exception as ex:
                exc = {'err': str(ex)}
                with open('habr/news/errors.json', 'a') as file:
                    json.dump(exc, file, indent=4, ensure_ascii=False)


def parsing_to_html():
    title_and_link_tags = {}
    title_and_link_search = {}
    for i in range(1, 4):
        yesterday = int((date.today() - timedelta(days=1)).strftime('%d'))
        with open(f'habr/news/habr_search_page{i}.html', encoding='utf-8')as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        all_title = soup.find_all('a', class_='tm-title__link')
        date_y = soup.find_all('time')
        for item, date_n in zip(all_title, date_y):
            date_n = int(date_n.get('datetime')[8: 10])
            if date_n == yesterday:
                item_text = item.text
                link = 'https://habr.com' + item.get('href')
                title_and_link_tags[item_text] = link
        print(f'[+] Page_search {i} complete!')
        with open(f'habr/news/habr_tags_page{i}.html', encoding='utf-8')as file:
            src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        all_title = soup.find_all('a', class_='tm-title__link')
        date_y = soup.find_all('time')
        for item, date_n in zip(all_title, date_y):
            date_n = int(date_n.get('datetime')[8: 10])
            if date_n == yesterday:
                item_text = item.text
                link = 'https://habr.com' + item.get('href')
                title_and_link_tags[item_text] = link
        print(f'[+] Page_tags {i} complete!')

    title_and_link_search.update(title_and_link_tags)
    print(title_and_link_search)
    with open('habr/news/title_link.json', 'w') as file:
        json.dump(title_and_link_search, file, indent=4, ensure_ascii=False)


def parsing_news_to_db():
    news_now = []
    with open('habr/news/title_link.json') as file:
        src = json.load(file)
    num = len(src)
    print(f'[+] News {num} found!')
    for i, v in src.items():
        print(f'[+] News "{i}" append!')
        try:
            time.sleep(random.randrange(1, 3))
            response = requests.get(url=v, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                title = soup.find('h1', class_='tm-title tm-title_h1').text
                body = soup.find(
                    'div',
                    class_='article-formatted-body article-formatted-body article-formatted-body_version-2').text
                date = soup.find('time').get('datetime')
            except AttributeError:
                title = soup.find('h1', class_='tm-title tm-title_h1').text
                body = soup.find(
                    'div',
                    class_='article-formatted-body article-formatted-body article-formatted-body_version-1').text
                date = soup.find('time').get('datetime')
            db.query('INSERT INTO news (title, body, link, date) VALUES (?, ?, ?, ?)', (title, body, v, date))
            print(Fore.GREEN + f'[+] News "{i}" complete!')
            news_now.append({'title': title, 'body': body})
            logging.info(f'[+] News "{i}" complete!')
        except Exception as ex:
            print(Fore.RED + f'[!] Error "{i}"')
            logging.info(f'[!] Error "{i}"')
            db.query('INSERT INTO news_err (title, link, exception) VALUES (?, ?, ?)', (i, v, str(ex)))
    with open('habr/news/news_now.json', 'w') as file:
        json.dump(news_now, file, indent=4, ensure_ascii=False)


def main():
    try:
        format = ('%(asctime)s - [%(levelname)s] - %(message)s')
        db.create_tables()
        logging.basicConfig(level=logging.INFO, format=format, filename="lgs_hbr.txt")
        # get_to_html()
        parsing_to_html()
        parsing_news_to_db()
    except Exception as e:
        logging.exception(e)
    finish_time = time.time() - start_time
    print(finish_time)
    print('!!! [+++] Parsing complete !!!')


if __name__ == '__main__':
    main()
