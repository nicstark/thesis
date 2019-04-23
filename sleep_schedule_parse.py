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
import os.path


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
i = 0
filter = ['Spam', 'SMS', 'Chat']
plusminus = ['+', '-']
dateFormats = ["%Y-%m-%d %H:%M:%S", ]

def humanDate(unix):
    return datetime.utcfromtimestamp(unix/1000).strftime('%Y-%m-%d %H:%M:%S')

def humanTime(unix):
    return(((unix/1000)/60)/60)

def returnstart(sleepItem):
    return sleepItem['start']

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

def checkDupes(check,against,key):
    for x in against:
        if check == x[key]:
            return True




def check_availability(element, collection: iter):
    return element in collection

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
                fit_object['Sleep Block'] = 0


                myDict['Activity'].append(fit_object)

sortedActivity = sorted(myDict['Activity'], key=lambda k: k['Start Time'])
myDict['Activity'] = sortedActivity
entry = 0


while entry < len(myDict['Activity']) -1:
    #look for start of sleep block
    if myDict['Activity'][entry]['Sleep'] > 0 and startSleep == 0 or myDict['Activity'][entry]['Deep Sleep'] > 0 and startSleep == 0:
        startSleep = myDict['Activity'][entry]['Start Time']
        myDict['Activity'][entry]['Sleep Block'] = 1
    elif myDict['Activity'][entry]['Sleep'] == 0 and myDict['Activity'][entry]['Deep Sleep'] == 0 and startSleep != 0:
        if myDict['Activity'][entry]['Start Time'] - startSleep < 3600000*2:
             pass
        else:
            endSleep = myDict['Activity'][entry]['Start Time']
            sleep_array.append({'start': startSleep, 'end' : endSleep})
            startSleep = 0
    entry += 1


while i < len(sleep_array) -1:
    if sleep_array[i+1]['start'] - sleep_array[i]['end'] < 3600000 :
        sleep_array[i]['end'] = sleep_array[i+1]['end']
        del sleep_array[i+1]
    i +=1

i = 0
while i < len(sleep_array) -1:
    if sleep_array[i+1]['start'] - sleep_array[i]['end'] < 3600000 :
        sleep_array[i]['end'] = sleep_array[i+1]['end']
        del sleep_array[i+1]

    i +=1

for blocks in sleep_array:
    for x in myDict['Activity']:
        if blocks['start'] == x['Start Time']:
            x['Sleep Block'] = 1
        if blocks['end'] == x['End Time']:
            x['Sleep Block'] = 2


i = 0
new_days = []
#iterating over real sleep blocks
while i < len(sleep_array) -1:
    #check if there's more than 24 hours between sleep blocks
    if sleep_array[i+1]['start'] - sleep_array[i]['end'] > 93600000:
        emptyPeriod = humanTime(sleep_array[i+1]['start'] - sleep_array[i]['end'])
        emptyPeriodUnix = sleep_array[i+1]['start'] - sleep_array[i]['end']
        quarterHourDivision = emptyPeriodUnix/900000
        dayDivision = int(quarterHourDivision / 96)
        newDivision = 96*dayDivision*900000

        #if so create fake sleep blocks
        for d in range(1, int(dayDivision)+1):
            fakeStart = sleep_array[i]['end'] + (((86400000)*d) - 28800000)
            #print (fakeStart)
            fakeEnd = sleep_array[i]['end'] + (86400000)*d
            if checkDupes(fakeStart,sleep_array,'start') or checkDupes(fakeEnd,sleep_array,'start') or checkDupes(fakeStart,sleep_array,'end') or checkDupes(fakeEnd,sleep_array,'end'):
                pass
            else:
                new_days.append({'start' : fakeStart, 'end' : fakeEnd})
    i += 1



for blocks in new_days:
    for x in myDict['Activity']:
        if blocks['start'] == x['Start Time']:
            x['Sleep Block'] = 3
        if blocks['end'] == x['End Time']:
            x['Sleep Block'] = 4

j = 0
files =[]

lastValue = 0
while j < len(myDict['Activity']):
    if myDict['Activity'][j]['Sleep Block'] == 1 or myDict['Activity'][j]['Sleep Block'] == 3:
        name = str(myDict['Activity'][j]['Start Time'])

        value = myDict['Activity'][lastValue:j]
        files.append(value)
        lastValue = j

    j += 1



dir = ('C:/Users/eufou/Desktop/Parsed')
if not os.path.exists(dir):
    os.mkdir(dir)


print(files[0])
print(files[0][0])


for file in files:
    filename = str(file[0]['Start Time'])
    with open(os.path.join(dir, filename + '.csv'), mode='w') as csv_file:
        fieldnames = ['Step Count', 'Sleep', 'Deep Sleep', 'Start Time', 'End Time', 'Sleep Block']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator = '\n')

        writer.writeheader()
        for row in file:
            writer.writerow({'Step Count': row['Step Count'], 'Sleep' : row['Sleep'], 'Deep Sleep' : row['Deep Sleep'], 'Start Time': row['Start Time'], 'End Time' : row['End Time'], 'Sleep Block' : row['Sleep Block']})

for file in files:
    filename = str(file[0]['Start Time'])
    with open(os.path.join(dir, filename + '.txt'), mode='w') as outfile:
        json.dump(file, outfile, indent=4, sort_keys=True, default=str)
#     print(len(file))
# sleep_array.sort(key = returnstart)
#
# i = 0
# while i < len(sleep_array) -1:
#     if sleep_array[i+1]['start'] - sleep_array[i]['end'] > 86400000:
#         print(humanTime(sleep_array[i+1]['start'] - sleep_array[i]['end']))
#         print('over 1')
#     i += 1



#
#
# with open('sleep.csv', mode='w') as csv_file:
#     fieldnames = ['Step Count', 'Sleep', 'Deep Sleep', 'Start Time', 'Sleep Block']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames, lineterminator = '\n')
#
#     writer.writeheader()
#     for row in myDict['Activity']:
#         writer.writerow({'Step Count': row['Step Count'], 'Sleep' : row['Sleep'], 'Deep Sleep' : row['Deep Sleep'], 'Start Time': row['Start Time'], 'Sleep Block' : row['Sleep Block']})
