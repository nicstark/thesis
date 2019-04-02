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



mbox = mailbox.mbox(root_path + mail_path)
print(mbox[4])
for email in mbox:
    if 'Spam' in email['X-Gmail-Labels']:
        continue
        print('spam filtered')
    else:
        if email.is_multipart():
            content = ''.join(part.get_payload() for part in email.get_payload()[0])
        else:
            content = email.get_payload()
        email_object = {}
        email_object['Subject'] = email['subject']
        email_object['Sender'] = email['from']
        email_object['Recipient'] = email['to']
        email_object['Body'] = content
        email_object['Date'] = email['date']
        myDict['Email'].append(email_object)

# print(len(myDict['Email']))
print(myDict['Email'][25])
print(myDict['Email'][26])
print(myDict['Email'][27])
print(myDict['Email'][28])
print(myDict['Email'][29])
print(myDict['Email'][21])
print(myDict['Email'][22])
# print(myDict['Email'][23])
# print(myDict['Email'][24])
