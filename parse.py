import csv
import json
from datetime import datetime
myDict = {}
myDict['Transactions'] = []
epoch = datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0
    
with open ('test_data/Citi.CSV', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    with open ('new_citi.csv', 'w') as new_file:
        csv_writer = csv.writer(new_file)
    
        for line in csv_reader:
            
            s = datetime.strptime(line['Date'], "%m/%d/%Y")
            milli = unix_time_millis(s)
            line['Date'] = milli
            print(line)
            myDict['Transactions'].append(line)
            #csv_writer.writerow(s)
    
with open('data.txt', 'w') as outfile:  
    json.dump(myDict, outfile)
    

