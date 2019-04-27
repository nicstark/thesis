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
myDict['SMS'] = []
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

def email_parse(email):
    email_object = {}
    email_object['Subject'] = str(email['subject'])
    email_object['Sender'] = str(email['from'])
    email_object['Recipient'] = str(email['to'])
    email_object['Body'] = str(showPayload(email))

    for x in range(12):
        index = x * -1
        try:
            email_object['Date'] = parse(email['date'][:index])
            t = datetime.strptime(str(email_object['Date']), "%Y-%m-%d %H:%M:%S")
            milli = unix_time_millis(t)
            email_object['Date'] = int(milli)
            break
        except:
            pass


    myDict['Email'].append(email_object)




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



for filename in os.listdir(root_path + phone_path):
    if filename.endswith(".html"):
        with open (root_path + phone_path + filename, 'r', encoding="utf8") as phone_file:
        # with open (root_path + phone_path + "Kyle Walsh - Placed - 2012-09-17T18_23_27Z.html", 'r', encoding="utf8") as phone_file:
            product = SoupStrainer('a','published')
            phone_object = {}
            soup = BeautifulSoup(phone_file,features="lxml")
            title = soup.find('title')
            title = title.get_text()
            date = soup.find('abbr')
            date = date.get('title')
            b = datetime.strptime(date[:-10], "%Y-%m-%dT%X")
            milliDate = unix_time_millis(b)
            phone_object['Date'] = int(milliDate)
            if title[:14] == "Placed call to":
                phone_object['Type'] = "Placed"
                title = title.split("to")
                try:
                    phone_object['Person'] = title[1][1:]
                    duration = soup.find('abbr', 'duration').get_text()
                    phone_object['Duration'] = duration[1:-1]

                except:
                    print ("error: ", filename)
            if title[:16] == "Missed call from":
                phone_object['Type'] = "Missed"
                title = title.split("from")
                try:
                    phone_object['Person'] = title[1][1:]
                except:
                    print ("error: ", filename)

            if title[:18] == "Received call from":
                phone_object['Type'] = "Received"
                title = title.split("from")
                try:
                    phone_object['Person'] = title[1][1:]
                    duration = soup.find('abbr', 'duration').get_text()
                    phone_object['Duration'] = duration[1:-1]
                except:
                    print ("error: ", filename)

            if title[:14] == "Voicemail from":
                phone_object['Type'] = "Voicemail"
                title = title.split("from")
                try:
                    phone_object['Person'] = title[1][1:]
                    duration = soup.find('abbr', 'duration').get_text()
                    phone_object['Duration'] = duration[1:-1]
                except:
                    print ("error: ", filename)

            if soup.find('div', 'hChatLog hfeed'):
                phone_object['Type'] = "SMS"
                # person = soup.find('head')
                # person = person.find('title')
                # person = person.get_text()
                # phone_object['Person'] = person
                # if person[:5] == 'Me to':
                #     phone_object['Person'] = person[6:]
                # phone_object['Messages'] = []
                messageCorpus = soup.find_all('div', 'message')
                for item in messageCorpus:
                    message = {}
                    sender = item.find('a', 'tel')
                    if sender.find('span'):
                        sender = sender.find('span').get_text()
                    else:
                        sender = sender.find('abbr').get_text()
                    message['Sender'] = sender
                    text = item.find('q')
                    text = text.get_text()
                    message['Text'] = text
                    time = soup.find('abbr')
                    time = time.get('title')
                    c = datetime.strptime(time[:-10], "%Y-%m-%dT%X")
                    milliTime = unix_time_millis(c)
                    message['Time'] = int(milliTime)
                    myDict['SMS'].append(message)
    if phone_object['Type'] == 'SMS':
        continue
    else:
        myDict['Phone'].append(phone_object)

mbox = mailbox.mbox(root_path + mail_path)
for email in mbox:
    if email['X-Gmail-Labels']:
        if  any(filters in email['X-Gmail-Labels'] for filters in filter):
            continue
        else:
            email_parse(email)
    else:
        email_parse(email)

with open('search', mode='w') as csv_file:
    fieldnames = ['Date', 'Terms']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for row in myDict['Search']:
        writer.writerow({'Date': row.Date, 'Terms': row.Terms})


# for keys in myDict:
#     with open(keys + '.txt', 'w') as outfile:
#         json.dump(myDict[keys], outfile, indent=4, sort_keys=True, default=str)
