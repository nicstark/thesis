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
phone_path = "Google/Voice/Calls/"
calendar_path = "Google/Calendar/"
geo_path = "Google/Location History/Location History.json"
dayChoice = "2017-05-10"
fixDay = 0


def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

dayChoiceObject = datetime.strptime(dayChoice, "%Y-%m-%d")
dayChoiceMilli = unix_time_millis(dayChoiceObject)
filename = root_path + search_path

testDict = {}
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
                    testDict[title[1][1:]] = 1
                except:
                    print ("error: ", filename)
    myDict['Phone'].append(phone_object)
print(testDict)
            #if title[:16] == "Missed call from":
                #print(title)
            #
            # for elem in soup:
            #     phoneDict = {}
            #     elemText = elem
            #     print(elemText)
                # if "Searched" in elemText[:8]:
                #     try:
                #         searchDict['Terms'] = elem.a.get_text()
                #         searchDate = str(elem.a.next_sibling.next_sibling)
                #         #searchDate = searchDate[0:-]
                #         splitDate = [x.strip() for x in searchDate.split(',')]
                #         searchTime = [x.strip() for x in splitDate[2].split(' ')]
                #         searchHour = [x.strip() for x in searchTime[0].split(':')]
                #         if len(splitDate[0]) == 5:
                #             fixDay = splitDate[0][0:-1] + "0" + splitDate[0][-1:]
                #         else:
                #             fixDay = str(splitDate[0])
                #         if searchTime[1] == "PM" and int(searchHour[0]) < 12:
                #             searchHour[0] = str(int(searchHour[0]) + 12)
                #         elif searchTime[1] == "AM" and searchHour[0] == "12":
                #             searchHour[0] = "00"
                #         elif len(searchHour[0]) == 1:
                #                 searchHour[0] = "0" + searchHour[0]
                #         try:
                #             t = datetime.strptime(str(fixDay + " " + str(splitDate[1]) + " " + str(searchHour[0]) + " " + str(searchHour[1]) + " " + str(searchHour[2])), "%b %d %Y %H %M %S" )
                #             milli = unix_time_millis(t)
                #         except ValueError:
                #             print (elem)
                #             continue
                #         searchDict['Date'] = int(milli)
                #
                #         myDict['Search'].append(searchDict)
                #
                #
                #     except AttributeError:
                #         try:
                #             hotelFix = [x.strip() for x in str(elem).split('>')]
                #             searchDict['Terms'] = hotelFix[1][13:-4]
                #             searchDate = hotelFix[2][:-5]
                #             splitDate = [x.strip() for x in searchDate.split(',')]
                #             searchTime = [x.strip() for x in splitDate[2].split(' ')]
                #             searchHour = [x.strip() for x in searchTime[0].split(':')]
                #             if len(splitDate[0]) == 5:
                #                 fixDay = splitDate[0][0:-1] + "0" + splitDate[0][-1:]
                #             else:
                #                 fixDay = str(splitDate[0])
                #             if searchTime[1] == "PM" and int(searchHour[0]) < 12:
                #                 searchHour[0] = str(int(searchHour[0]) + 12)
                #             elif searchTime[1] == "AM" and searchHour[0] == "12":
                #                 searchHour[0] = "00"
                #             elif len(searchHour[0]) == 1:
                #                 searchHour[0] = "0" + searchHour[0]
                #             try:
                #                 t = datetime.strptime(str(fixDay + " " + str(splitDate[1]) + " " + str(searchHour[0]) + " " + str(searchHour[1]) + " " + str(searchHour[2])), "%b %d %Y %H %M %S" )
                #                 milli = unix_time_millis(t)
                #             except ValueError:
                #                 print (elem)
                #                 continue
                #             searchDict['Date'] = int(milli)
                #         finally:
                #             myDict['Search'].append(searchDict)
