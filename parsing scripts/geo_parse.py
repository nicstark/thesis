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
print("test")
with open(root_path + geo_path, 'rb') as geo_path:
    #geo_data = ijson.items(geo_path, 'locations')
    geo_data = json.load(geo_path)
    print(len(geo_data['locations']))
    for item in geo_data['locations']:
        geo_object = {}
        geo_object['Date'] = item['timestampMs']
        geo_object['Latitude'] = item['latitudeE7']/1e7
        geo_object['Longtitude'] = item['longitudeE7']/1e7
        myDict['Location'].append(geo_object)
    print(len(myDict['Location']))


    # for item in geo_data['locations']:
    #     try:
    #         print(geo_data['locations'][1]['velocity'])
    #     except KeyError:
    #         print ('nope')



    # for item in geo_data['locations']:

        # myDict['Location'].append(item)
        # if str(item['longitudeE7'])[0] == 0:
        #     print(str(item['longitudeE7']))
        # # print(len(item))
    # while fixDay < 10:
    #     print(myDict['Location'][fixDay])
    #     fixDay += 1;
    #print(myDict['Location'][0:10][0])
    #print(geo_data['locations'].keys())
    #print(geo_data[0].keys())
    # for item in geo_data:
    #     print(type(item))
    #     print(item)
    #     # for key in item.keys():
    #     #     print(key)
    #     i = 0
    #     i =+ 1
    #     print (i)
    #     #print(len(item))

    #print(json.dumps(geo_data, indent = 4, sort_keys=True))
