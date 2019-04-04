import os
import csv
import json
import ijson
from datetime import datetime
import lxml
from bs4 import BeautifulSoup, SoupStrainer
from ics import Calendar, Event
import mailbox
import email.utils

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
mail_path = "Google/Mail/All mail Including Spam and Trash.mbox"
geo_path = "Google/Location History/Location History.json"
dayChoice = "2017-05-10"
fixDay = 0

from_addr = email.utils.formataddr(('Author',
                                    'author@example.com'))
to_addr = email.utils.formataddr(('Recipient',
                                  'recipient@example.com'))




def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

dayChoiceObject = datetime.strptime(dayChoice, "%Y-%m-%d")
dayChoiceMilli = unix_time_millis(dayChoiceObject)

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
        #print (msg.get_content_type())
        #print (payload[:200])

filter = ['Spam', 'SMS', 'Chat']

def email_parse(email):
    email_object = {}
    email_object['Subject'] = email['subject']
    email_object['Sender'] = email['from']
    email_object['Recipient'] = email['to']
    email_object['Body'] = showPayload(email)
    dateString = str(email['date'])
    print(dateString)
    splitDate = dateString.split()
    if len(splitDate[0]) == 4:
        if len(splitDate[4]) < 8:
            splitTime = splitDate[4].split(':')
            t = datetime.strptime(splitDate[1] + "," + splitDate[2] + "," + splitDate[3] + "," + splitTime[0] + ':' + splitTime[1], "%d,%b,%Y,%H:%M")
        else:
            splitTime = splitDate[4].split(':')
            t = datetime.strptime(splitDate[1] + "," + splitDate[2] + "," + splitDate[3] + "," + splitTime[0] + ':' + splitTime[1] + ":" + splitTime[2], "%d,%b,%Y,%H:%M:%S")
    else:
        if len(splitDate[3]) < 8:
            splitTime = splitDate[3].split(':')
            t = datetime.strptime(splitDate[0] + "," + splitDate[1] + "," + splitDate[2] + "," + splitTime[0] + ':' + splitTime[1], "%d,%b,%Y,%H:%M")
        else:
            splitTime = splitDate[3].split(':')
            t = datetime.strptime(splitDate[0] + "," + splitDate[1] + "," + splitDate[2] + "," + splitTime[0] + ':' + splitTime[1] + ":" + splitTime[2], "%d,%b,%Y,%H:%M:%S")

    milli = unix_time_millis(t)
    email_object['Date'] = int(milli)

    myDict['Email'].append(email_object)

mbox = mailbox.mbox(root_path + mail_path)
for email in mbox:
    if email['X-Gmail-Labels']:
        if  any(filters in email['X-Gmail-Labels'] for filters in filter):
            print('filter working')
        else:
            email_parse(email)
    else:
        email_parse(email)



# print(len(myDict['Email']))
print(myDict['Email'][25])
print(myDict['Email'][23])
print(myDict['Email'][24])
