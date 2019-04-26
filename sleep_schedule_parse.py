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



myDict = {}
files = {}
myDict['Transactions'] = []
TransactionFiles = [];
myDict['Activity'] = []
ActivityFiles = []
myDict['Screen Activity'] = []
myDict['Search'] = []
myDict['Calendar'] = []
myDict['Location'] = []
myDict['Phone'] = []
myDict['Email'] = []
fakeDaysArray = []
fitFilesRef = []
wakeList = []
realSleepArray = []
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

def email_parse(email):
    email_object = {}
    email_object['Subject'] = str(email['subject'])
    email_object['Sender'] = str(email['from'])
    email_object['Recipient'] = str(email['to'])
    email_object['Body'] = len(str(showPayload(email)))

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
print('made it up to here')
mbox = mailbox.mbox(root_path + mail_path)
print('mailbox loaded')
try:
    for email in mbox:
        print('working')
        if email['X-Gmail-Labels']:
            if  any(filters in email['X-Gmail-Labels'] for filters in filter):
                continue
            else:
                email_parse(email)
        else:
            email_parse(email)
except:
    print('error')

counter = 0
for filename in os.listdir(root_path + fit_path):
    if filename.endswith(".csv") and filename != "Daily Summaries.csv":
        filenameUnix = datetime.strptime(filename[:10], "%Y-%m-%d")
        milli = unix_time_millis(filenameUnix)
        fitFilesRef.append(milli)
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
                fit_object['Sleep Block'] = 'Real Entry'


                myDict['Activity'].append(fit_object)



print('number of fit files',len(fitFilesRef))
myDictSpan  = myDict['Activity'][-1]['Start Time'] - myDict['Activity'][0]['Start Time']
print('my dict activity length', len(myDict['Activity']))
print('my dict span quartered', myDictSpan/900000)


gapCount = 0
entryNum = 0

i=1
while i < len(fitFilesRef):
    fileGap = fitFilesRef[i] - fitFilesRef[i-1]
    if fileGap >  86400000:
        gapStart = fitFilesRef[i-1] + 86400000
        while gapStart < fitFilesRef[i]:
            myDict['Activity'].append({'Step Count' : 0, 'Sleep' : 0, 'Deep Sleep' : 0, 'Start Time' : int(gapStart), 'End Time' : int(gapStart + 900000), 'Sleep Block' : 'Fake Entry'})
            entryNum += 1
            gapStart+= 900000
        gapCount += humanDays(fileGap) -1
    i += 1

print('fake entries generated should be 25823', entryNum)
print('gap count', gapCount)

sortedActivity = sorted(myDict['Activity'], key=lambda k: k['Start Time'])
myDict['Activity'] = sortedActivity

print('my dict activity length after fakes', len(myDict['Activity']))

#here we catalogue real sleep
i = 0
sleepBreakTicker = 0
while i < len(myDict['Activity']) -1:
    #look for start of sleep block
    if myDict['Activity'][i]['Sleep'] > 0 and startSleep == 0 or myDict['Activity'][i]['Deep Sleep'] > 0 and startSleep == 0:
        startSleep = myDict['Activity'][i]['Start Time']
        myDict['Activity'][i]['Sleep Block'] = 'Real Start'
    elif myDict['Activity'][i]['Sleep'] == 0 and myDict['Activity'][i]['Deep Sleep'] == 0 and startSleep != 0:
        sleepBreakTicker += 1
        if myDict['Activity'][i]['Start Time'] - startSleep < 3600000*2:
             pass
        elif sleepBreakTicker == 10:
            myDict['Activity'][i-10]['Sleep Block'] = 'Real End'
            endSleep = myDict['Activity'][i-10]['Start Time']
            realSleepArray.append({'start': startSleep, 'end' : endSleep})
            startSleep = 0
            sleepBreak = 0
            sleepBreakTicker = 0
    i += 1



print('sleep array length ', len(realSleepArray))

print('sleep array span ', ((((realSleepArray[-1]['end'] - realSleepArray[0]['start'])/1000)/60)/60)/24)


#iterating over real sleep blocks
i = 1
while i < len(realSleepArray)-1:
    #check if there's more than 26 hours between sleep blocks
    if realSleepArray[i]['start'] - realSleepArray[i-1]['end'] > 93600000:
        #get the amount of time between sleep blocks
        emptyPeriodUnix = realSleepArray[i]['start'] - realSleepArray[i-1]['end']

        emptyPeriod = humanTime(emptyPeriodUnix)

        #see how many 15 minute blocks fit into the period
        quarterHourDivision = emptyPeriodUnix/900000
        #find how many days fit into the period

        daysInPeriod = int(emptyPeriodUnix / 86400000)

        segment = int(quarterHourDivision/(daysInPeriod*2))

        #if so create fake sleep blocks
        for d in range(1, daysInPeriod*2):
            fakeEnd = realSleepArray[i-1]['end'] + (segment*900000)*d
            fakeStart = fakeEnd - (900000*32)
            fakeDaysArray.append({'start' : int(fakeStart), 'end' : int(fakeEnd)})

    i += 1


#
# for day in fakeDaysArray:
#     print('--')
#     print(humanDate(day['start']))





count = 0
for entry in myDict['Activity']:
    for fakeday in fakeDaysArray:
        if fakeday['start'] == entry['Start Time']:
            count += 1
            entry['Sleep Block'] = 'Fake Start'
        #else append
        if fakeday['end'] == entry['End Time']:
            entry['Sleep Block'] = 'Fake End'


print('fake sleep blocks added, should be ~ 349',count)





j = 0
lastValue = 0
while j < len(myDict['Activity']):
    if myDict['Activity'][j]['Sleep Block'] == 'Real Start' or myDict['Activity'][j]['Sleep Block'] == 'Fake Start':
        name = str(myDict['Activity'][j]['Start Time'])
        value = myDict['Activity'][lastValue:j-1]
        ActivityFiles.append(value)
        lastValue = j

    j += 1


print('activity files length ',len(ActivityFiles))
files['Activity'] = ActivityFiles
print('activity file span ', humanDays(ActivityFiles[-1][0]['End Time'] - ActivityFiles[1][0]['Start Time']))

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
    if transaction['Date'] > myDict['Activity'][0]['Start Time'] and transaction['Date'] < myDict['Activity'][-1]['End Time']:
        filteredTransactions.append(transaction)
myDict['Transactions'] = filteredTransactions


myDict['Transactions'] = sorted(myDict['Transactions'], key=lambda k: k['Date'])


#SEARCH
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


for entry in myDict['Activity']:
    if entry['Sleep Block'] == 'Real End' or entry['Sleep Block'] == 'Fake End':
        #print(humanDate(entry['Start Time']))
        wakeList.append(entry)

dir = ('C:/Users/eufou/Desktop/Parsed')
if not os.path.exists(dir):
    os.mkdir(dir)

for key in myDict:
    subdir = ('C:/Users/eufou/Desktop/Parsed/' + key)
    if not os.path.exists(subdir):
        os.mkdir(subdir)

def jsonOutput(subdir,filename,data):
    with open(os.path.join(dir + subdir, filename + '.txt'), mode='w') as outfile:
        json.dump(data, outfile)




for file in files['Activity']:
    filename = str(file[0]['Start Time'])
    jsonOutput('/Activity', filename, file)

    transactionHolder = []
    for transaction in myDict['Transactions']:
        transactionDate = datetime.fromtimestamp(transaction['Date']/1000).strftime('%Y-%m-%d')
        if datetime.fromtimestamp(int(filename)/1000).strftime('%Y-%m-%d') == transactionDate:
            transactionHolder.append(transaction)
    try:
        transactionHolder = sorted(transactionHolder, reverse = True, key=lambda k: abs(float(k['Amount'])))
    except:
        print(transactionHolder)
        pass
    jsonOutput('/Transactions', filename, transactionHolder)

    searchHolder = []
    for search in myDict['Search']:
        if search['Date'] > file[0]['Start Time'] and search['Date'] < file[-1]['End Time']:
            searchHolder.append(search)
    jsonOutput('/Search', filename, searchHolder)
    emailHolder = []
    for email in myDict['Email']:
        if int(email['Date']) > int(file[0]['Start Time']) and int(email['Date']) < int(file[-1]['End Time']):
            emailHolder.append(email)
    jsonOutput('/Email', filename, emailHolder)










#
# for wake in wakeList:
#     print(datetime.fromtimestamp(wake['Start Time']/1000).strftime('%Y-%m-%d') )
#     filename = str(wake['Start Time'])
#     with open(os.path.join(dir + '/Transactions', filename + '.txt'), mode='w') as outfile:
#         json.dump(dayHolder, outfile)

print('wake list length ', len(wakeList))

print('wake list span ', wakeList[-1]['Start Time'] - wakeList[0]['Start Time'])

print('transactions length ', len(myDict['Transactions']))
