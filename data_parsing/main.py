from pymongo import MongoClient
from history_news_parser import choose_data, process_news_to_db
from planning_news_parser import process_plan_to_db
from datetime import datetime, timedelta


# Collect data for the last 6 months
date_from = (datetime.now() - timedelta(days=180)).strftime('%m/%d/%Y')
date_to = (datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')

host = 'localhost'
port = 27017
client = MongoClient(host, port)
db = client['data']

print(f'Parse news from {date_from} to {date_to}')

data_news = db['news']
html = choose_data(date_from=date_from, date_to=date_to)
process_news_to_db(html, data_news)

# Collect data for today
print('Parse news for today')

today_news = db['today']
html = choose_data(date_from=datetime.now().strftime('%m/%d/%Y'), 
                   date_to=datetime.now().strftime('%m/%d/%Y'))
process_news_to_db(html, today_news)

# Collect data about upcoming news
print('Parse data about upcoming news')

plan = db['planning']
process_plan_to_db(plan)
