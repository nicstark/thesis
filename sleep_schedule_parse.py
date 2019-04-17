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
sleep_array = []
sleep_object = {}
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
startSleep = 0
endSleep = 0
filter = ['Spam', 'SMS', 'Chat']
plusminus = ['+', '-']
dateFormats = ["%Y-%m-%d %H:%M:%S", ]


def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

def showPayload(msg):
    payload = msg.get_payload()

    if msg.is_multipart():
        div = ''
        message = []
        for subMsg in payload:
            #print (div)
            message.append(showPayload(subMsg))
            #div = '------------------------------'
        return message
    else:
        return payload[:200]


counter = 0
for filename in os.listdir(root_path + fit_path):
    if filename.endswith(".csv") and filename != "Daily Summaries.csv":
        with open (root_path + fit_path + filename, 'r', encoding="utf8") as fit_csv:
            fit_reader = csv.DictReader(fit_csv)
            for line in fit_reader:
                fit_object = {}
                try:
                    fit_object['Step Count'] = int(line['Step count'])
                except:
                    fit_object['Step Count'] = 0;
                try:
                    fit_object['Sleep'] = int(line['Sleep duration (ms)'])
                except:
                    fit_object['Sleep'] = 0
                try:
                    fit_object['Deep Sleep'] = int(line['Deep sleeping duration (ms)'])
                except:
                    fit_object['Deep Sleep'] = 0

                s = datetime.strptime(filename[:10] + " " + line['Start time'][0:8], "%Y-%m-%d %X")
                milli = unix_time_millis(s)
                fit_object['Start Time'] = int(milli)
                e = datetime.strptime(filename[:10] + " " + line['End time'][0:8], "%Y-%m-%d %X")
                milli = unix_time_millis(e)
                fit_object['End Time'] = int(milli)


                myDict['Activity'].append(fit_object)

sortedActivity = sorted(myDict['Activity'], key=lambda k: k['Start Time'])
myDict['Activity'] = sortedActivity

for entry in myDict['Activity']:
    #look for start of sleep block
    if entry['Sleep'] > 0 and startSleep == 0 or entry['Deep Sleep'] > 0 and startSleep == 0:
        startSleep = entry['Start Time']
        endCount = 0;
    elif entry['Sleep'] == 0 and entry['Deep Sleep'] == 0 and startSleep != 0:

        if endCount < 5:
            endCount +=1
        else:
            endSleep = entry['Start Time']
            sleep_object['start'] = startSleep
            sleep_object['end'] = endSleep
            duration = endSleep - startSleep
            endCount = 0
            #print (duration)
            sleep_array.append(sleep_object)

            # print(datetime.utcfromtimestamp(startSleep/1000).strftime('%Y-%m-%d %H:%M:%S'))
            # print(datetime.utcfromtimestamp(endSleep/1000).strftime('%Y-%m-%d %H:%M:%S'))
            # print (((duration/1000)/60)/60)
            startSleep = 0;

print(len(sleep_array))







#print(myDict['Activity'])

#
# with open('search', mode='w') as csv_file:
#     fieldnames = ['Date', 'Terms']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#
#     writer.writeheader()
#     for row in myDict['Search']:
#         writer.writerow({'Date': row.Date, 'Terms': row.Terms})
