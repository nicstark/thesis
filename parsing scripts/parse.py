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
from pprint import pprint
import pandas as pd
import numpy as np
import icalendar




myDict = {}
files = {}
ActivityFiles = []
myDict['Activity'] = []
myDict['Transactions'] = []
myDict['Screen'] = []
myDict['Search'] = []
myDict['Calendar'] = []
myDict['Location'] = []
myDict['Phone'] = []
myDict['SMS'] = []
myDict['Email'] = []
fakeDaysArray = []
fitFilesRef = []
wakeList = []
realSleepArray = []
sleep_object = {}
protoGeoArray = []
epoch = datetime.utcfromtimestamp(0)
root_path = "C:/Users/eufou/Desktop/NewData/"
citi_path = "Financial/Citi.CSV"
usaa_path = "Financial/USAA_download.csv"
fit_path = "Takeout/Fit/Daily Aggregations/"
rescue_path = "Screen Activity/rescuetime-activity-history.csv"
search_path = "Takeout/My Activity/Search/MyActivity.html"
phone_path = "Takeout/Voice/Calls/"
calendar_path = "Takeout/Calendar/"
geo_path = "Takeout/Location History/Location History.json"
mail_path = "Takeout/Mail/All mail Including Spam and Trash.mbox"
fixDay = 0
sleepStarted = 0
endSleep = 0
i = 0
filter = ['Spam', 'SMS', 'Chat']
plusminus = ['+', '-']
dateFormats = ["%Y-%m-%d %H:%M:%S", ]

def humanDate(unix):
    return datetime.utcfromtimestamp(unix/1000).strftime('%Y-%m-%d %H:%M:%S')

def humanTime(unix):
    return(((unix/1000)/60)/60)
def humanDays(unix):
    return((((unix/1000)/60)/60)/24)
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

def screenDateParse(entry):
    t = datetime.strptime(entry[0:19], "%Y-%m-%d %X")
    milli = unix_time_millis(t)
    return int(milli)

#PHONE_________________________
def phoneParse():
    for filename in os.listdir(root_path + phone_path):
        if filename.endswith(".html"):

            with open (root_path + phone_path + filename, 'r', encoding="utf8") as phone_file:
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
                        b = datetime.strptime("1970,1,1," + duration[1:-1], "%Y,%m,%d,%X")
                        milliBegin = unix_time_millis(b)
                        phone_object['Duration'] = int(milliBegin)

                    except:
                        print ("error: ", filename)
                elif title[:16] == "Missed call from":
                    phone_object['Type'] = "Missed"
                    title = title.split("from")
                    phone_object['Duration'] = 0;
                    try:
                        phone_object['Person'] = title[1][1:]
                    except:
                        print ("error: ", filename)

                elif title[:18] == "Received call from":
                    phone_object['Type'] = "Received"
                    title = title.split("from")
                    try:
                        phone_object['Person'] = title[1][1:]
                        duration = soup.find('abbr', 'duration').get_text()
                        b = datetime.strptime("1970,1,1," + duration[1:-1], "%Y,%m,%d,%X")
                        milliBegin = unix_time_millis(b)
                        phone_object['Duration'] = int(milliBegin)
                    except:
                        print ("error: ", filename)

                elif title[:14] == "Voicemail from":
                    phone_object['Type'] = "Voicemail"
                    title = title.split("from")
                    try:
                        phone_object['Person'] = title[1][1:]
                        duration = soup.find('abbr', 'duration').get_text()
                        b = datetime.strptime("1970,1,1," + duration[1:-1], "%Y,%m,%d,%X")
                        milliBegin = unix_time_millis(b)
                        phone_object['Duration'] = int(milliBegin)
                    except:
                        print ("error: ", filename)

                if soup.find('div', 'hChatLog hfeed'):
                    phone_object['Type'] = "SMS"
                    if title[:5] == 'Me to':
                        person = title[6:]
                    else:
                        person = title

                    messageCorpus = soup.find_all('div', 'message')


                    for item in messageCorpus:
                        message = {}
                        sender = item.find('a', 'tel')
                        if sender.find('span'):
                            sender = sender.find('span').get_text()
                        else:
                            sender = sender.find('abbr', "fn").get_text()
                        message['Person'] = person

                        if sender == "Me":
                            message['Incoming'] = True;

                        else:
                            message['Incoming'] = False;

                        text = item.find('q')
                        text = text.get_text()
                        message['Length'] = len(text)
                        time = item.find('abbr')
                        time = time.get('title')
                        c = datetime.strptime(time[:-10], "%Y-%m-%dT%X")
                        milliTime = unix_time_millis(c)
                        message['Date'] = int(milliTime)
                        myDict['SMS'].append(message)

                try:
                    if phone_object["Type"] != "SMS":
                        myDict['Phone'].append(phone_object)
                except:
                    continue


#SCREEN______________
def screenParse():
    # with open (root_path + rescue_path, 'r', encoding="utf8") as rescue_csv:
    #     rescue_reader = csv.DictReader(rescue_csv)
    #     rescue_reader.fieldnames = ['Date','Title', 'Details','Category','Type','Duration']
    #
    #     for line in rescue_reader:
    #         t = datetime.strptime(line['Date'][0:19], "%Y-%m-%d %X")
    #         milli = unix_time_millis(t)
    #         line['Date'] = int(milli)

    screen_df = pd.read_csv(root_path + rescue_path, header = None, names =['Date','Title', 'Details','Category','Type','Duration'] )
    screen_df['Date'] = screen_df['Date'].map(screenDateParse)

    aggregates = (screen_df.groupby(['Date']).agg(
    {
         'Duration':sum,    # Sum duration per group
    }))
    #aggregates.sort_values(by=['Date'])
    aggregates.columns=['Value']


    hour = 60*60*1000
    min = int(aggregates.index.min()/hour)
    max = int(aggregates.index.max()/hour)
    span = max - min

    def screenUnitConvert(x):
        return (x*hour) + aggregates.index.min() + hour
    #list(range(min,max,900000))
    df2 = pd.DataFrame({'Date':range(0,span), 'Value':0})
    df2['Date'] = df2['Date'].map(screenUnitConvert)
    df2.index = df2.Date

    df2.Value = aggregates.Value
    df2 =  df2.fillna(0)
    df2.sort_index(axis = 1);



    for index, row in df2.iterrows():
        myDict['Screen'].append({'Date': int(row['Date']), 'Value' : int(row['Value'])})
        # if (int(index) - int(row['Date']) != 0):
        #     print(int(row['Date']),int(row['Value']))

    # i=1
    # while i < len(myDict['Screen']):
    #     if myDict['Screen'][i]['Date'] - myDict['Screen'][i-1]['Date'] > hour:
    #         print("wtf")
    #     i+=1
#CALENDAR________________
def calParse():
    for filename in os.listdir(root_path + calendar_path):
        if filename.endswith(".ics"):
            with open (root_path + calendar_path + filename, 'r', encoding="utf8") as calendar_file:

                c = Calendar(calendar_file.read())

                for event in c.events:
                    try:
                        formatEvent = {}
                        formatEvent['Title'] = event.name
                        b = datetime.strptime(str(event.begin)[:-6], "%Y-%m-%dT%X")
                        milliBegin = unix_time_millis(b)
                        formatEvent['Begin'] = int(milliBegin)
                        e = datetime.strptime(str(event.end)[:-6], "%Y-%m-%dT%X")
                        milliEnd = unix_time_millis(e)
                        formatEvent['End'] = int(milliEnd)
                        myDict['Calendar'].append(formatEvent)

                    except:
                        continue





#EMAIL__________________________________________________
def emailParse():
    def email_parse(email):
        print('parsing')
        email_object = {}
        email_object['Subject'] = str(email['subject'])
        email_object['Sender'] = str(email['from'])
        email_object['Recipient'] = str(email['to'])
        email_object['Body'] = len(str(showPayload(email)))


        for x in range(13):
            index = x * -1
            try:
                emailDate = parse(email['date'][:index])
                t = datetime.strptime(str(emailDate), "%Y-%m-%d %H:%M:%S")
                milli = unix_time_millis(t)
                email_object['Date'] = int(milli)
                myDict['Email'].append(email_object)
                break
            except:
                continue




    for email in mailbox.mbox(root_path + mail_path):
        if email['X-Gmail-Labels']:
            if  any(filters in email['X-Gmail-Labels'] for filters in filter):
                print("filtered")
            else:
                email_parse(email)
        else:
            email_parse(email)



#ACTIVITY___________________________________________
def activityParse():
    counter = 0
    for filename in os.listdir(root_path + fit_path):
        if filename.endswith(".csv") and filename != "Daily Summaries.csv":
            filenameUnix = datetime.strptime(filename[:10], "%Y-%m-%d")
            milli = unix_time_millis(filenameUnix)
            if milli < 1484008200000:
                continue
            fitFilesRef.append(milli)
            with open (root_path + fit_path + filename, 'r', encoding="utf8") as fit_csv:
                fit_reader = csv.DictReader(fit_csv)
                for line in fit_reader:
                    fit_object = {}
                    try:
                        fit_object['StepCount'] = int(line['Step count'])
                    except:
                        fit_object['StepCount'] = 0;
                    try:
                        fit_object['Sleep'] = int(line['Sleep duration (ms)'])
                    except:
                        fit_object['Sleep'] = 0
                    try:
                        fit_object['DeepSleep'] = int(line['Deep sleeping duration (ms)'])
                    except:
                        fit_object['DeepSleep'] = 0

                    s = datetime.strptime(filename[:10] + " " + line['Start time'][0:8], "%Y-%m-%d %X")
                    milli = unix_time_millis(s)
                    fit_object['Start'] = int(milli)
                    e = datetime.strptime(filename[:10] + " " + line['End time'][0:8], "%Y-%m-%d %X")
                    milli = unix_time_millis(e)
                    fit_object['End'] = int(milli)
                    fit_object['SleepBlock'] = 'Real Entry'
                    if fit_object['End'] < fit_object['Start']:
                        fit_object['End'] = fit_object['Start'] + 900000

                    myDict['Activity'].append(fit_object)
    print(len(myDict['Activity']))
    print(myDict['Activity'][-1])



    # print('number of fit files',len(fitFilesRef))
    myDictSpan  = myDict['Activity'][-1]['Start'] - myDict['Activity'][0]['Start']
    # print('my dict activity length', len(myDict['Activity']))
    # print('my dict span quartered', myDictSpan/900000)
    #print("Data span", humanDays(myDictSpan))
    #should be ~ 652 days in total
    gapCount = 0
    entryNum = 0

    i=1
    while i < len(fitFilesRef):
        fileGap = fitFilesRef[i] - fitFilesRef[i-1]
        if fileGap >  86400000:
            gapStart = fitFilesRef[i-1] + 86400000
            while gapStart < fitFilesRef[i]:
                myDict['Activity'].append({'StepCount' : 0, 'Sleep' : 0, 'DeepSleep' : 0, 'Start' : int(gapStart), 'End' : int(gapStart + 900000), 'SleepBlock' : 'Fake Entry'})
                entryNum += 1
                gapStart+= 900000
            gapCount += humanDays(fileGap) -1
        i += 1

    #print('fake entries generated should be 25823', entryNum)
    # print('gap count', gapCount)

    sortedActivity = sorted(myDict['Activity'], key=lambda k: k['Start'])
    myDict['Activity'] = sortedActivity




    #here we catalogue real sleep
    i = 0
    sleepBreakTicker = 0
    sleepStarted = 0
    while i < len(myDict['Activity']) -1:
        #look for start of sleep block
        current = myDict['Activity'][i]
        if current['Sleep'] > 0 or current['DeepSleep'] > 0:
            if sleepStarted == 0:
                sleepStarted = current['Start']
                current['SleepBlock'] = 'Real Start'
            sleepBreakTicker = 0
        elif current['Sleep'] == 0 and current['DeepSleep'] == 0 and sleepStarted != 0:
            sleepBreakTicker += 1

            if sleepBreakTicker == 10:
                myDict['Activity'][i-10]['SleepBlock'] = 'Real End'
                endSleep = myDict['Activity'][i-10]['Start']
                realSleepArray.append({'start': sleepStarted, 'end' : endSleep})
                sleepStarted = 0
                sleepBreak = 0
                sleepBreakTicker = 0
        i += 1



    #print('sleep array length ', len(realSleepArray))

    #here we're removing likely false entries
    i=1
    while i < len(realSleepArray)-1:
        sleepTime = humanTime(realSleepArray[i]['end'] - realSleepArray[i]['start'])
        currentHumanStart = humanDate(realSleepArray[i]['start'])
        currentHumanEnd = humanDate(realSleepArray[i]['end'])
        distanceFromPrevious = humanTime(realSleepArray[i]['start'] - realSleepArray[i-1]['end'])
        distanceFromNext = humanTime(realSleepArray[i+1]['start'] - realSleepArray[i]['end'])
        previous = humanTime(realSleepArray[i-1]['end'] - realSleepArray[i-1]['start'])
        next = humanTime(realSleepArray[i+1]['end'] - realSleepArray[i+1]['start'])

        if distanceFromPrevious + sleepTime + previous < 10:
            realSleepArray[i-1]['end'] = realSleepArray[i]['end']
            del realSleepArray[i]

        if distanceFromNext + sleepTime + next < 10:
            realSleepArray[i+1]['start'] = realSleepArray[i]['start']
            del realSleepArray[i]

        i+=1

    i = 1
    numblockcounter = 0
    daysCounter = 0
    gapCounter = 0
    emptyperiodCounter = 0;
    while i < len(realSleepArray)-1:
        #check if there's more than 26 hours between sleep blocks
        numBlocks = 0
        if realSleepArray[i]['start'] - realSleepArray[i-1]['end'] > 900000*170:
            gapCounter+=1
            #get the amount of time between sleep blocks
            emptyPeriodUnix = realSleepArray[i]['start'] - realSleepArray[i-1]['end']
            emptyperiodCounter += emptyPeriodUnix
            emptyPeriod = humanTime(emptyPeriodUnix)

            #see how many 15 minute blocks fit into the period
            quarterHourDivision = emptyPeriodUnix/900000

            #find how many days fit into the period
            halfdaysInPeriod = int(emptyPeriodUnix / (86400000/2))
            numBlocks = int(halfdaysInPeriod)
            # daysCounter +=daysInPeriod
            # numblockcounter += numBlocks
            segmentLengthInBlocks = int((quarterHourDivision/numBlocks)*2)

            # print("empty period in hours", emptyPeriod)
            # print("number of quarter hour blocks in period", quarterHourDivision)
            # print("number of days in period", daysInPeriod)
            # print("numblocks ", numBlocks)
            # print("calculated segment", segmentLengthInBlocks)
            # print(" ")
            #if so create fake sleep blocks
        for d in range(1, int(numBlocks/2)+1):
            fakeEnd = realSleepArray[i-1]['end'] + (segmentLengthInBlocks*900000)*d
            fakeStart = fakeEnd - (900000*32)
            fakeDaysArray.append({'start' : int(fakeStart), 'end' : int(fakeEnd)})

        i += 1


    # i = 1
    # while i < len(realSleepArray)-1:
    #     #check if there's more than 26 hours between sleep blocks
    #     span = realSleepArray[i]['start'] - realSleepArray[i-1]['end']
    #     if span > 900000*88 and span < 900000*170:
    #         print(humanTime(span))
    #     i+=1
    # for blocks in fakeDaysArray:
    #     print(humanTime(blocks['end']-blocks['start']))
    # print('real sleep aray length', len(realSleepArray))
    # print("gap counter ", gapCounter)
    # print("numblocks counter ", numblockcounter)
    # print("days counter ", daysCounter)
    # print("Fake sleep Blocks", len(fakeDaysArray))
    # print("empty periods sum days", humanDays(emptyperiodCounter))

    count = 0
    for entry in myDict['Activity']:
        for fakeday in fakeDaysArray:
            if  abs(entry['Start'] == fakeday['start']):
                count += 1
                entry['SleepBlock'] = 'Fake Start'
            #else append
            if abs(fakeday['end'] == entry['End']):
                entry['SleepBlock'] = 'Fake End'




    j = 1
    lastValue = 1
    while j < len(myDict['Activity']):
        if myDict['Activity'][j]['SleepBlock'] == 'Real Start' or myDict['Activity'][j]['SleepBlock'] == 'Fake Start':
            value = myDict['Activity'][lastValue:j-1]
            if len(value) > 0:
                ActivityFiles.append(value)
            lastValue = j

        j += 1


    files['Activity'] = ActivityFiles






#FINANCIAL____________________________________________
def financeParse():
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
            try:
                if abs(float(line['Debit'])) > 0:
                    line['Debit'] = "-" + line['Debit']
            except:
                continue
            if line['Credit']:
                line['Debit'] = 0
                line['Credit'] = line['Credit'].replace(",", "")
                line['Debit'] = line['Credit']

            line['Amount'] = line['Debit']
            del line['Credit']
            del line['Debit']
            myDict['Transactions'].append(line)

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

    filteredTransactions = []
    for transaction in myDict['Transactions']:
        if transaction['Date'] > myDict['Activity'][0]['Start'] and transaction['Date'] < myDict['Activity'][-1]['End']:
            filteredTransactions.append(transaction)
    myDict['Transactions'] = filteredTransactions


    myDict['Transactions'] = sorted(myDict['Transactions'], key=lambda k: k['Date'])

#SEARCH____________________________________________
def searchParse():
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
    print("len my dict search", len(myDict['Search']))

#GEOLOCATION_____________________________________
def geoParse():
    with open(root_path + geo_path, 'rb') as geo_csv:
        #geo_data = ijson.items(geo_path, 'locations')
        geo_data = json.load(geo_csv)
        for item in geo_data['locations']:
            geo_object = {}
            geo_object['Date'] = item['timestampMs']
            geo_object['Latitude'] = item['latitudeE7']/1e7
            geo_object['Longitude'] = item['longitudeE7']/1e7
            protoGeoArray.append(geo_object)
        i = 0
        while i < len(protoGeoArray)-1:
            myDict['Location'].append(protoGeoArray[i])
            i +=6

#EXPORT_________________________________________

dir = ('C:/Users/eufou/Desktop/NewParsed')
if not os.path.exists(dir):
    os.mkdir(dir)

for key in myDict:
    subdir = (dir +"/" + key)
    if not os.path.exists(subdir):
        os.mkdir(subdir)

def jsonOutput(subdir,filename,data):
    if data:
        with open(os.path.join(dir + subdir, filename + '.txt'), mode='w') as outfile:
            json.dump(data, outfile)
    else:
        pass


#EXPORT ACTIVITY____________________

def exporter():

    for file in files['Activity']:
        try:
            filename = str(file[0]['Start'])
            jsonOutput('/Activity', filename, file)
        except:
            print("_______________________________________",file)
            print(len(file[0]))
    #EXPORT TRANSACTIONS____________________
        transactionHolder = []
        for transaction in myDict['Transactions']:
            transactionDate = datetime.fromtimestamp(transaction['Date']/1000).strftime('%Y-%m-%d')
            if datetime.fromtimestamp(int(filename)/1000).strftime('%Y-%m-%d') == transactionDate:
                transactionHolder.append(transaction)
        transactionHolder = sorted(transactionHolder, reverse = True, key=lambda k: abs(float(k['Amount'])))

        jsonOutput('/Transactions', filename, transactionHolder)

    #EXPORT SEARCH______________________
        searchHolder = []

        for search in myDict['Search']:
            if search['Date'] > file[0]['Start'] and search['Date'] < file[-1]['End']:
                searchHolder.append(search)
        jsonOutput('/Search', filename, searchHolder)

    #EXPORT EMAIL_______________________
        emailHolder = []
        for email in myDict['Email']:
            try:
                if int(email['Date']) > int(file[0]['Start']) and int(email['Date']) < int(file[-1]['End']):
                    emailHolder.append(email)
            except Exception as e:
                print("Email ", e)
                continue
        jsonOutput('/Email', filename, emailHolder)

    #EXPORT GEOLOCATION___________________
        geoHolder = []
        for geo in myDict['Location']:
            try:
                if int(geo['Date']) > int(file[0]['Start']) and int(geo['Date']) < int(file[-1]['End']):
                    geoHolder.append(geo)
            except Exception as e:
                print("Location ", e)
                continue
        jsonOutput('/Location', filename, geoHolder)

    #EXPORT CALENDAR________________
        calHolder = []
        for event in myDict['Calendar']:
            try:
                if int(event['Begin']) > int(file[0]['Start']) and int(event['Begin']) < int(file[-1]['End']):
                    calHolder.append(event)
            except Exception as e:
                print("Calendar ", e)
                continue
        jsonOutput('/Calendar', filename, calHolder)

    #EXPORT SCREEN______________
        screenHolder = []
        for entry in myDict['Screen']:
            try:
                if int(entry['Date']) > int(file[0]['Start']) and int(entry['Date']) < int(file[-1]['End']):
                    screenHolder.append(entry)
            except Exception as e:
                print("Screen ", e)
                continue
        jsonOutput('/Screen', filename, screenHolder)

    #EXPORT PHONE__________
        phoneHolder = []
        for entry in myDict['Phone']:
            try:
                if int(entry['Date']) > int(file[0]['Start']) and int(entry['Date']) < int(file[-1]['End']):
                    phoneHolder.append(entry)
            except Exception as e:
                print("Phone ", e)
                continue
        jsonOutput('/Phone', filename, phoneHolder)

    #EXPORT SMS_________________
        smsHolder = []
        for entry in myDict['SMS']:
            try:
                if int(entry['Date']) > int(file[0]['Start']) and int(entry['Date']) < int(file[-1]['End']):
                    smsHolder.append(entry)
            except Exception as e:
                print("SMS", e)
                continue
        jsonOutput('/SMS', filename, smsHolder)


activityParse()
# emailParse()
# geoParse()
# searchParse()
financeParse()
# calParse()
# screenParse()
# phoneParse()
exporter()
