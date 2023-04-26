from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from datetime import datetime
import pandas as pd


def process_plan_to_db(table):
    """table - table name of connected database for saving data"""
    urls = [
        'https://www.investing.com/economic-calendar/interest-rate-decision-164',
        'https://www.investing.com/economic-calendar/interest-rate-decision-168',
        'https://www.investing.com/economic-calendar/consumer-inflation-expectation-920',
        'https://www.investing.com/economic-calendar/consumer-inflation-expectations-2024',
        'https://www.investing.com/economic-calendar/unemployment-rate-300',
        'https://www.investing.com/economic-calendar/unemployment-rate-299'
    ]

    new_id = 0

    chrome_options = Options()
    chrome_options.add_argument("start-maximized")

    for link in urls:
        driver = webdriver.Chrome(executable_path=".\chromedriver.exe", options=chrome_options)
        driver.implicitly_wait(10)

        driver.get(link)

        rows = driver.find_elements(By.XPATH, '//div[@class="historyTab"]//tr')[1:]
        info = driver.find_elements(By.XPATH, '//div[@id="overViewBox"]//span')

        for row in rows[::-1]:
            fs = row.find_elements(By.TAG_NAME, 'td')
            if fs[2].text.strip() == "":
                plan_news = {}
                dtime = fs[0].text.replace(',', '').split('(')[0].split(' ') + [fs[1].text.strip(), '-0400']
                dtime = datetime.strptime(' '.join(dtime), '%b %d %Y %H:%M %z').strftime('%Y-%m-%d %H:%M:%S%z')
                plan_news['dtime'] = pd.Timestamp(dtime)
                info[3].get_attribute('title')
                plan_news['country'] = info[3].find_element(By.TAG_NAME, 'i').get_attribute('title').strip()
                plan_news['currency'] = info[5].text.strip()
                plan_news['importance'] = '3'
                plan_news['event'] = driver.find_element(By.TAG_NAME, 'h1').text.strip()
                plan_news['actual'] = fs[2].text.strip()
                plan_news['forecast'] = fs[3].text.strip()
                plan_news['prev'] = fs[4].text.strip()
                plan_news['_id'] = f"{plan_news['currency']}_{new_id}"

                table.insert_one(plan_news)
                print(f"Insert news with id {plan_news['currency']}_{new_id}")
                new_id += 1
                break

        driver.close()
