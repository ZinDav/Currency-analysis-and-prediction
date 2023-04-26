from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time


def choose_data(date_from=(datetime.now() - timedelta(days=90)).strftime('%m/%d/%Y'), 
                date_to=(datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y'), 
                countries=[54, 34, 89, 71, 17, 51, 72, 22, 33, 10, 97, 96, 21, 26, 5]):
    """
    date_from - start date of the parsing,
    date_to - finish date of the parsing,,
    countries - list of codes of choosing countries
    """

    chrome_options = Options()
    chrome_options.add_argument("start-maximized")

    driver = webdriver.Chrome(executable_path=".\chromedriver.exe", options=chrome_options)
    driver.implicitly_wait(10)

    driver.get('https://investing.com/economic-calendar/')


    # Change choosen countries on checkbox
    driver.find_element(By.XPATH, "//a[@id='filterStateAnchor']").click()

    # Clear all countries
    driver.find_element(By.XPATH, "//div[@class='left float_lang_base_1']/a[contains(text(), 'Clear')]").click()

    # Choose need countries
    for c in countries:
        elem = driver.find_element(By.XPATH, f"//input[@id='country{c}']")

        actions = ActionChains(driver)
        actions.move_to_element(elem)
        actions.perform()
        elem.click()

    driver.find_element(By.XPATH, "//input[@id='timetimeOnly']").click()

    driver.find_element(By.XPATH, "//a[@id='ecSubmitButton']").click()

    driver.find_elements(By.XPATH, "//vdz-span")[-1].click()

    # Change time diapason
    elem = driver.find_element(By.XPATH, "//a[@id='datePickerToggleBtn']")

    actions = ActionChains(driver)
    actions.move_to_element(elem)
    actions.perform()

    time.sleep(2)
    elem.click()

    elem = driver.find_element(By.XPATH, "//input[@id='startDate']")
    elem.clear()
    elem.send_keys(date_from)

    elem = driver.find_element(By.XPATH, "//input[@id='endDate']")
    elem.clear()
    elem.send_keys(date_to)

    driver.find_element(By.XPATH, "//a[@id='applyBtn']").click()

    time.sleep(5)


    # Change timezone
    for tz in ("//div[@id='economicCurrentTime']", 
            '//li[contains(text(), "(GMT) Coordinated Universal Time")]'):
        elem = driver.find_element(By.XPATH, tz)

        actions = ActionChains(driver)
        actions.move_to_element(elem)
        actions.perform()
        elem.click()
    time.sleep(5)


    # Open all news from time diapason
    news = driver.find_elements(By.XPATH, '//table[@id="economicCalendarData"]/tbody/tr')
    id = news[-1].get_attribute('id')

    while True:
        actions = ActionChains(driver)
        actions.move_to_element(news[-1])
        actions.perform()
        time.sleep(5)

        news = driver.find_elements(By.XPATH, '//table[@id="economicCalendarData"]/tbody/tr')

        if id == news[-1].get_attribute('id'):
            break
        else:
            id = news[-1].get_attribute('id')
    
    # Return html with all news
    html = driver.page_source
    driver.close()
    return html


def process_news_to_db(html, table):
    """"
    html - str with html-page,
    table - table name of connected database for saving data
    """
    # Save html like dom-object in BeautifulSoup
    dom = BeautifulSoup(html, 'lxml')
    new_id = 0

    for row in dom.find('table', {"id":"economicCalendarData"}).find_all('tr')[2:]:
        new_news = {}
        if row.has_attr('id') and row.has_attr('data-event-datetime'):
            new_news['dtime'] = pd.Timestamp(row.get('data-event-datetime') + '+0000')
            fs = row.findChildren('td')
            new_news['country'] = fs[1].find('span').get('data-img_key')
            new_news['currency'] = fs[1].text.strip()
            new_news['importance'] = fs[2].get('data-img_key').replace('bull', '').strip()
            new_news['event'] = fs[3].text.strip()
            new_news['actual'] = fs[4].text.strip()
            new_news['forecast'] = fs[5].text.strip()
            new_news['prev'] = fs[6].text.strip()
            new_news['_id'] = f"{new_news['currency']}_{new_id}"

            table.insert_one(new_news)
            print(f"Insert news with id {new_news['currency']}_{new_id}")

            new_id += 1
        elif row.has_attr('id'):
            new_news['dtime'] = day
            fs = row.findChildren('td')
            new_news['country'] = fs[1].find('span').get('data-img_key')
            if new_news['country'] == 'United_States':
                new_news['currency'] = 'USD'
            else:
                new_news['currency'] = 'EUR'
            new_news['importance'] = fs[2].text.replace('bull', '').strip()
            new_news['event'] = fs[3].text.strip()
            new_news['actual'] = '-'
            new_news['forecast'] = '-'
            new_news['prev'] = '-'
            new_news['_id'] = f"{new_news['currency']}_{new_id}"

            table.insert_one(new_news)
            print(f"Insert news with id {new_news['currency']}_{new_id}")

            new_id += 1
        elif row.findChild('td').get('class') == ['theDay']:
            day = row.findChild('td').text.strip()
            print(f'Parsing data for {day}')
            day = datetime.strptime(day, '%A, %B %d, %Y').strftime('%Y-%m-%d %H:%M:%S')
            day = pd.Timestamp(day + '+0000')
        else:
            print('.....Something goes wrong.....')
