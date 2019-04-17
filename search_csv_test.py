import os
import csv
import json
import ijson
from datetime import *
import lxml
from bs4 import BeautifulSoup, SoupStrainer
from ics import Calendar, Event
import mailbox
import email.utils
from dateutil.parser import *

myDict = {}
myDict['Transactions'] = []
myDict['Activity'] = []
myDict['Screen Activity'] = []
myDict['Search'] = []
myDict['Calendar'] = []
myDict['Location'] = []
myDict['Phone'] = []
myDict['Email'] = []
epoch = datetime.utcfromtimestamp(0)
root_path = "C:/Users/eufou/Desktop/Data/"
citi_path = "Financial/Citi.CSV"
usaa_path = "Financial/USAA_download.csv"
fit_path = "Google/Fit/Daily Aggregations/"
rescue_path = "Screen Activity/rescuetime-activity-history.csv"
search_path = "Google/My Activity/Search/MyActivity.html"
phone_path = "Google/Voice/Calls/"
calendar_path = "Google/Calendar/"
geo_path = "Google/Location History/Location History.json"
mail_path = "Google/Mail/All mail Including Spam and Trash.mbox"
dayChoice = "2017-05-10"
fixDay = 0
filter = ['Spam', 'SMS', 'Chat']
plusminus = ['+', '-']
dateFormats = ["%Y-%m-%d %H:%M:%S", ]

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


filename = root_path + search_path
search_data = open(filename, 'r', encoding="utf8").read()
product = SoupStrainer('div','content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')
soup = BeautifulSoup(search_data,parse_only=product,features="lxml")
for elem in soup:
    searchDict = {}
    elemText = elem.get_text()
    if "Searched" in elemText[:8]:
        try:
            searchDict['Terms'] = elem.a.get_text()
            searchDate = str(elem.a.next_sibling.next_sibling)
            #searchDate = searchDate[0:-]
            splitDate = [x.strip() for x in searchDate.split(',')]
            searchTime = [x.strip() for x in splitDate[2].split(' ')]
            searchHour = [x.strip() for x in searchTime[0].split(':')]
            if len(splitDate[0]) == 5:
                fixDay = splitDate[0][0:-1] + "0" + splitDate[0][-1:]
            else:
                fixDay = str(splitDate[0])
            if searchTime[1] == "PM" and int(searchHour[0]) < 12:
                searchHour[0] = str(int(searchHour[0]) + 12)
            elif searchTime[1] == "AM" and searchHour[0] == "12":
                searchHour[0] = "00"
            elif len(searchHour[0]) == 1:
                    searchHour[0] = "0" + searchHour[0]
            try:
                t = datetime.strptime(str(fixDay + " " + str(splitDate[1]) + " " + str(searchHour[0]) + " " + str(searchHour[1]) + " " + str(searchHour[2])), "%b %d %Y %H %M %S" )
                milli = unix_time_millis(t)
            except ValueError:
                print (elem)
                continue
            searchDict['Date'] = int(milli)

            myDict['Search'].append(searchDict)


        except AttributeError:
            try:
                hotelFix = [x.strip() for x in str(elem).split('>')]
                searchDict['Terms'] = hotelFix[1][13:-4]
                searchDate = hotelFix[2][:-5]
                splitDate = [x.strip() for x in searchDate.split(',')]
                searchTime = [x.strip() for x in splitDate[2].split(' ')]
                searchHour = [x.strip() for x in searchTime[0].split(':')]
                if len(splitDate[0]) == 5:
                    fixDay = splitDate[0][0:-1] + "0" + splitDate[0][-1:]
                else:
                    fixDay = str(splitDate[0])
                if searchTime[1] == "PM" and int(searchHour[0]) < 12:
                    searchHour[0] = str(int(searchHour[0]) + 12)
                elif searchTime[1] == "AM" and searchHour[0] == "12":
                    searchHour[0] = "00"
                elif len(searchHour[0]) == 1:
                    searchHour[0] = "0" + searchHour[0]
                try:
                    t = datetime.strptime(str(fixDay + " " + str(splitDate[1]) + " " + str(searchHour[0]) + " " + str(searchHour[1]) + " " + str(searchHour[2])), "%b %d %Y %H %M %S" )
                    milli = unix_time_millis(t)
                except ValueError:
                    print (elem)
                    continue
                searchDict['Date'] = int(milli)
            finally:
                myDict['Search'].append(searchDict)


with open('search.csv', mode='w', encoding="utf-8") as csv_file:
    fieldnames = ['Date', 'Terms']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for item in myDict['Search']:
        writer.writerow({'Date': item['Date'], 'Terms': item['Terms']})
