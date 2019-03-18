import csv
import json
from datetime import datetime


myDict = {}
myDict['Transactions'] = []
myDictDay = []
epoch = datetime.utcfromtimestamp(0)
dayChoice = "2017-05-10";

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0
    
dayChoiceObject = datetime.strptime(dayChoice, "%Y-%m-%d")
dayChoiceMilli = unix_time_millis(dayChoiceObject)

with open ('test_data/Citi.CSV', 'r') as citi_csv:
    citi_reader = csv.DictReader(citi_csv)
    
    # with open ('new_citi.csv', 'w') as new_file:
    #     csv_writer = csv.writer(new_file)
    
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
            
with open ('test_data/USAA_download.csv', 'r') as usaa_csv:
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

        #print(line)
        myDict['Transactions'].append(line)
        #csv_writer.writerow(s)
myDict['Transactions'] = sorted(myDict['Transactions'], key=lambda k: k['Date']) 

    
with open('data.txt', 'w') as outfile:  
    json.dump(myDict, outfile)

for transaction in myDict['Transactions']:
    if transaction['Date'] == dayChoiceMilli:
        myDictDay.append(transaction)
        print(transaction['Date'])
    
with open(dayChoice + '.txt', 'w') as outfile:  
    json.dump(myDictDay, outfile)
    


