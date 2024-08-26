from datetime import datetime

import loguru
import requests
from bs4 import BeautifulSoup
from sqlalchemy import text

from app.core.internal import extract_http_https_links
from app.core.snowflake_id import id_worker
from app.model.domain import Icgb
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
}

def update_usefulness(title, href, icgb_day, id, usefulness):
    now = int(datetime.now().timestamp())
    stmt = text(f"update icgb set title = '{title}', href = '{href}', icgb_day= '{icgb_day}', usefulness = {usefulness}, "
                f"update_time = {now} where id = {id}")
    return stmt

def batch_save_or_update(icgblist: list):
    values_list = []
    for icgb in icgblist:
        values_list.append(f"({icgb.id}, '{icgb.title}', '{icgb.href}', '{icgb.text}', '{icgb.url}', '{icgb.day}', "
                           f"'{icgb.icgb_day}', '{icgb.unique_title}', {icgb.create_time}, {icgb.update_time}, "
                           f"{icgb.deleted}, {icgb.usefulness}) ")
    sql = ",\n".join(values_list)
    return text(f"INSERT INTO icgb (id, title, href, text, url, day, icgb_day, unique_title, create_time, "
                f"update_time, deleted, usefulness) "
                f"VALUES {sql}"
                f"ON CONFLICT(unique_title, url) DO UPDATE SET "
                f"text = excluded.text, href = excluded.href, update_time = excluded.update_time")

def list_by_day(day: str, usefulness: int=1):
    if day:
        return text(f"select * from icgb where deleted = 0 and day = '{day}' ")
    else:
        return text(f"select * from icgb where deleted = 0 and usefulness = {usefulness} order by icgb_day desc limit 100")

def count_by_day(day: str):
    return text(f"select count(*) from icgb where deleted = 0 and day = '{day}' ")

def list_day():
    return text(f"select DISTINCT(day) from icgb order by id desc limit 3000 ")


def list_by_time(start: str, end: str):
    return text(f"select * from icgb where deleted = 0 and usefulness = 1 and icgb_day >= '{start}' and icgb_day <= '{end}' ")

def gen_icgb(index: int=1):
    timestamp = int(datetime.now().timestamp())
    url = (f"https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space?host_mid=57276677&page=1"
           f"&web_location=333.999&w_rid=39cdc015b4013257fcc8d5d27897b5c3&wts={timestamp}")
    response = requests.get(url, headers=headers)
    loguru.logger.info('{}', response.text)
    if response.status_code != 200 or response.json()['code'] != 0:
        raise IOError('client error')

    jump_url = response.json()['data']['items'][index]['jump_url'].replace("//", "https://")
    resp = requests.get(jump_url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    elements = soup.find_all(class_='publish-text')
    try:
        day = datetime.strptime(elements[0].get_text(), '%Y年%m月%d日 %H:%M').strftime('%Y-%m-%d')
    except:
        day = elements[0].get_text()
    icgblist = []
    for i, h1 in enumerate(soup.find_all('h1')):
        title = h1.get_text().strip().replace("\n", "").replace("\r", "")
        print(f"Section {i+1}: {title}")
        if title is None or title == '':
            continue

        next_h1 = h1.find_next('h1')
        content = []
        href = ''

        for sibling in h1.find_next_siblings():
            if sibling == next_h1:
                break
            text = sibling.get_text().strip()
            if text.startswith("群号"):
                continue
            if 'http' in text:
                href = extract_http_https_links(text)[0]
            content.append(text)
        now = datetime.now().timestamp()
        icgb = Icgb(title=title, href=href, text="".join(content), day=day, icgb_day=day, id=str(id_worker.next_id()),
                    create_time=now, update_time=now, url=jump_url, unique_title=title)
        icgblist.append(icgb)
    return icgblist, day