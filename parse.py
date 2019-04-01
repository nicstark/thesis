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
myDict['Phone'] = []
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

with open (root_path + citi_path, 'r', encoding="utf8") as citi_csv:
    citi_reader = csv.DictReader(citi_csv)

    for line in citi_reader:

        s = datetime.strptime(line['Date'], "%m/%d/%Y")
        milli = unix_time_millis(s)
        line['Date'] = int(milli)
        def delete_empty_value(line):
            for k, v in line.items():
                if not (v or k == 'Credit'):
                    del line[k]
                elif isinstance(v, dict):
                    delete_empty_value(v)
        #print(line)
        line['Debit'] = line['Debit'].replace(",", "")
        line['Debit'] = "-" + line['Debit']
        if line['Credit']:
            line['Debit'] = 0
            line['Credit'] = line['Credit'].replace(",", "")
            line['Debit'] = line['Credit']
        line['Amount'] = line['Debit']
        del line['Credit']
        del line['Debit']
        myDict['Transactions'].append(line)
        #csv_writer.writerow(s)

with open (root_path + usaa_path, 'r', encoding="utf8") as usaa_csv:
    usaa_reader = csv.DictReader(usaa_csv)
    usaa_reader.fieldnames = ['Status', 'Blank', 'Date', 'Blank2','Description', 'Category', 'Amount']
    for line in usaa_reader:
        t = datetime.strptime(line['Date'], "%m/%d/%Y")
        milli = unix_time_millis(t)
        line['Date'] = int(milli)
        del line['Blank']
        del line['Blank2']
        if "--" in line["Amount"][:2]:
            line['Amount'] = line['Amount'][2:]

        myDict['Transactions'].append(line)


myDict['Transactions'] = sorted(myDict['Transactions'], key=lambda k: k['Date'])
counter = 0
for filename in os.listdir(root_path + fit_path):
    if filename.endswith(".csv"):
        with open (root_path + fit_path + filename, 'r', encoding="utf8") as fit_csv:
            fit_reader = csv.DictReader(fit_csv)
            for line in fit_reader:
                fit_object = {}
                fit_object['Step Count'] = line['Step count']
                try:
                    fit_object['Sleep'] = int(line['Sleep duration (ms)'])
                except:
                    fit_object['Sleep'] = 0
                try:
                    fit_object['Deep Sleep'] = int(line['Deep sleeping duration (ms)'])
                except:
                    fit_object['Deep Sleep'] = 0
                try:
                    if len([x.strip() for x in filename.split('-')]) == 3:
                        new_date = dayChoice + " " + line['Start time'][0:8]
                        t = datetime.strptime(new_date, "%Y-%m-%d %X")
                        milli = unix_time_millis(t)
                        fit_object['Start Time'] = int(milli)
                        t = datetime.strptime(dayChoice + " " + line['End time'][0:8], "%Y-%m-%d %X")
                        milli = unix_time_millis(t)
                        fit_object['End Time'] = int(milli)
                    else:
                        continue
                except:
                    continue
                myDict['Activity'].append(fit_object)

with open (root_path + rescue_path, 'r', encoding="utf8") as rescue_csv:
    rescue_reader = csv.DictReader(rescue_csv)
    rescue_reader.fieldnames = ['Date','Title', 'Details','Category','Type','Duration']

    for line in rescue_reader:
        t = datetime.strptime(line['Date'][0:19], "%Y-%m-%d %X")
        milli = unix_time_millis(t)
        line['Date'] = int(milli)

        myDict['Screen Activity'].append(line)

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

for filename in os.listdir(root_path + calendar_path):
    if filename.endswith(".ics"):
        with open (root_path + calendar_path + filename, 'r', encoding="utf8") as calendar_file:
            c = Calendar(calendar_file.read())

            for event in c.events:
                formatEvent = {}
                formatEvent['Name'] = event.name
                b = datetime.strptime(str(event.begin)[:-6], "%Y-%m-%dT%X")
                milliBegin = unix_time_millis(b)
                formatEvent['Begin'] = int(milliBegin)
                e = datetime.strptime(str(event.end)[:-6], "%Y-%m-%dT%X")
                milliEnd = unix_time_millis(e)
                formatEvent['End'] = int(milliEnd)
                myDict['Calendar'].append(formatEvent)


with open(root_path + geo_path, 'rb') as geo_path:
    #geo_data = ijson.items(geo_path, 'locations')
    geo_data = json.load(geo_path)
    for item in geo_data['locations']:
        geo_object = {}
        geo_object['Date'] = item['timestampMs']
        geo_object['Latitude'] = item['latitudeE7']/1e7
        geo_object['Longtitude'] = item['longitudeE7']/1e7
        myDict['Location'].append(geo_object)

with open('data.txt', 'w') as outfile:
    json.dump(myDict, outfile)
