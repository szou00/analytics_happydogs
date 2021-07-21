import requests
import json
import datetime
import pandas as pd
import dateutil.parser as dp
import time
import sys

# Global variable to store a list of dictionaries where key=tag, value=number of convos
analytics = []


def jprint(obj):
    """Prints a formatted string of a JSON object. 

        Parameters:
            obj: A Javascript Object

        Returns:
            None
    """
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def convo_metrics(day,inboxID,inboxName):
    """Requests information from the Front API and appends that information to a list. 
        
        Parameters: 
            day: A Datetime object
            inboxID: A string containing the inbox ID
            inboxName: A string containing the name of the inbox 
        Returns:
            None
    """

    numOfConvos = {}
    startDay = day # keep track of start; reminder to lessen number of variables

    start = str(day.timestamp())
    delta = datetime.timedelta(days=1)
    day+= delta
    end = str(day.timestamp())

    url = "https://api2.frontapp.com/analytics?start="+ start +"&end=" + end + "&metrics[0]id=tags_table&metrics[0]metric_type=table&inbox_ids[0]=" + inboxID
 
    payload={}
    files={}
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsic2hhcmVkOioiXSwiaWF0IjoxNjI2NzExMDI2LCJpc3MiOiJmcm9udCIsInN1YiI6ImhhcHB5X2RvZ3NfbnljIiwianRpIjoiZTUxYWFkNGM5Y2E3ODlhMiJ9.xZAyAkDSlxcaKYj9rhozowo84zBMVH4q7X0lGNZttn0'
    }

    requests.request("GET", url, headers=headers, data=payload, files=files) # first request triggers the calculation on the back-end

    time.sleep(0.5) # giving the API enough time to finish the calculation 

    response = requests.request("GET", url, headers=headers, data=payload, files=files) # second request actually gets the calculation now!
    
    # jprint(response.json())
    metrics=response.json()["metrics"]
    tags=metrics[0]["rows"]
    # jprint(tags)

    for tag in tags:
        name = tag[0]["v"]
        current = tag[3]["v"]
        numOfConvos['Date'] = startDay
        numOfConvos['Inbox'] = inboxName
        numOfConvos['Tag'] = name
        numOfConvos['Num'] = current
        analytics.append(numOfConvos)
        numOfConvos = {}


def get_stats(start,end):
    """Uses previous helper functions to generate a CSV file containing monthly analytics of email tags on Front App. 
    
        Parameters: 
            None
        Returns:
            None
    """
    start = start - datetime.timedelta(days = start.weekday()) # get the monday of the week
    delta = datetime.timedelta(days=7)
    inboxes = {"inb_ejh1":"234","inb_fu2t":"403","inb_fu4d":"504","inb_fu8t":"208"}

    while start <= end:
        print("--------------") # testing purposes
        print(start)
        for inboxID,inboxName in inboxes.items():
            convo_metrics(start,inboxID,inboxName)
        start += delta
    
    df = pd.DataFrame(analytics)
    df.to_csv('analytics.csv', mode='w',index=False)


def main():
    start = dp.isoparse(sys.argv[1])
    end = dp.isoparse(sys.argv[2])

    get_stats(start,end)

if __name__ == "__main__":
    main()