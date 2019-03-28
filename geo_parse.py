import os
import csv
import json
import ijson
from datetime import datetime
import lxml
from bs4 import BeautifulSoup, SoupStrainer
from ics import Calendar, Event


myDict = {}
myDict['Transactions'] = []
myDict['Activity'] = []
myDict['Screen Activity'] = []
myDict['Search'] = []
myDict['Calendar'] = []
myDict['Location'] = []
epoch = datetime.utcfromtimestamp(0)
root_path = "C:/Users/eufou/Desktop/Data/"
citi_path = "Financial/Citi.CSV"
usaa_path = "Financial/USAA_download.csv"
fit_path = "Google/Fit/Daily Aggregations/"
rescue_path = "Screen Activity/rescuetime-activity-history.csv"
search_path = "Google/My Activity/Search/MyActivity.html"
voice_path = "Google/Voice/"
calendar_path = "Google/Calendar/"
geo_path = "Google/Location History/Location History.json"
dayChoice = "2017-05-10"
fixDay = 0

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

dayChoiceObject = datetime.strptime(dayChoice, "%Y-%m-%d")
dayChoiceMilli = unix_time_millis(dayChoiceObject)

with open(root_path + geo_path, 'rb') as geo_path:
    #location_data = ijson.items(geo_path, 'locations')
    geo_data = json.load(geo_path)
    # for entry in location_data:
    #     print(entry)

    print(json.dumps(geo_data, indent = 4, sort_keys=True))
