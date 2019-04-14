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
mail_path = "Google/Mail/All mail Including Spam and Trash.mbox"
geo_path = "Google/Location History/Location History.json"
dayChoice = "2017-05-10"
fixDay = 0
#
# from_addr = email.utils.formataddr(('Author',
#                                     'author@example.com'))
# to_addr = email.utils.formataddr(('Recipient',
#                                   'recipient@example.com'))




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
        #print (msg.get_content_type())
        #print (payload[:200])

filter = ['Spam', 'SMS', 'Chat']
plusminus = ['+', '-']

def email_parse(email):
    email_object = {}
    email_object['Subject'] = email['subject']
    email_object['Sender'] = email['from']
    email_object['Recipient'] = email['to']
    email_object['Body'] = showPayload(email)
    try:
        try:
            parentSplit = email['date'].split('(')
            if any(gmt in parentSplit[0] for gmt in plusminus):
                try:
                    gmtSplit = parentSplit[0].split('+')
                    gmtSplit = gmtSplit[0].split('-')

                except:
                    gmtSplit = parentSplit[0].split('-')
                email_object['Date'] = parse(gmtSplit[0])
            else:
                email_object['Date'] = parse(parentSplit[0])
        except:
            if any(gmt in email['date'] for gmt in plusminus):
                try:
                    dateSplit = email['date'].split('+')
                except:
                    dateSplit = email['date'].split('-')
                email_object['Date'] = parse(dateSplit[0])
            else:
                email_object['Date'] = parse(email['date'])
    except:
        email_object['Date'] = parse(email['date'][:-5])
        pass
    try:
        t = datetime.strptime(str(email_object['Date']), "%Y-%m-%d %H:%M:%S")
        milli = unix_time_millis(t)
        email_object['Date'] = int(milli)
    except:
        email_object['Date'] = parse(email['date'][:-5])
        pass

    myDict['Email'].append(email_object)

mbox = mailbox.mbox(root_path + mail_path)
for email in mbox:
    if email['X-Gmail-Labels']:
        if  any(filters in email['X-Gmail-Labels'] for filters in filter):
            continue
        else:
            email_parse(email)
    else:
        email_parse(email)
