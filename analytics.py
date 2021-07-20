import requests
import json
import datetime
import pandas as pd
import dateutil.parser as dp

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


# def get_epoch_values(day):
#     """Takes in a date and returns the epoch values of the beginning and end of the day. 

#         Parameters:
#             day: A datetime object
#         Returns:
#             values: A list of 2 epoch values
#     """
#     values = []

#     dayStart = day.timestamp()

#     dayEnd = day+=1

#     # finding epoch value of last day of the month 
#     next_month = thisDate.replace(day=28) + datetime.timedelta(days=4)
#     lastDay = next_month - datetime.timedelta(days=next_month.day) 
#     date_string = lastDay.isoformat()
#     dt = datetime.datetime.strptime(date_string, "%Y-%m-%d")
#     monthEnd = datetime.datetime.timestamp(dt)
#     values.append(monthEnd)

#     return values


def convo_metrics(day,inboxID,inboxName):
    """Takes in a datetime object uses it to request information from the Front API, and appends that
    information to a list. 
        
        Parameters: 
            day: A Datetime object
        Returns:
            None
    """

    numOfConvos = {}
    numOfConvos['date'] = day
    numOfConvos['inbox'] = inboxName

    start = str(day.timestamp())
    delta = datetime.timedelta(days=1)
    day += delta
    end = str(day.timestamp())

    url = "https://api2.frontapp.com/analytics?start="+ start +"&end=" + end + "&metrics[0]id=tags_table&metrics[0]metric_type=table&inbox_ids[0]=" + inboxID
 
    payload={}
    files={}
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsic2hhcmVkOioiXSwiaWF0IjoxNjI2NzExMDI2LCJpc3MiOiJmcm9udCIsInN1YiI6ImhhcHB5X2RvZ3NfbnljIiwianRpIjoiZTUxYWFkNGM5Y2E3ODlhMiJ9.xZAyAkDSlxcaKYj9rhozowo84zBMVH4q7X0lGNZttn0'
    }

    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    
    # jprint(response.json())
    metrics=response.json()["metrics"]
    tags=metrics[0]["rows"]
    # jprint(tags)

    for tag in tags:
        name = tag[0]["v"]
        current = tag[3]["v"]
        numOfConvos[name] = current
        # jprint(tag)
        # print("--------------")

    # print(numOfConvos)
    analytics.append(numOfConvos)

def get_stats(start,end):
    """Uses previous helper functions to generate a CSV file containing monthly analytics of email tags on Front App. 
    
        Parameters: 
            None
        Returns:
            None
    """
    delta = datetime.timedelta(days=1)
    inboxes = {"inb_ejh1":234,"inb_fu2t":403,"inb_fu4d":504,"inb_fu8t":208}
    
    # for inboxID,inboxName in inboxes.items():
    #     temp = start
    #     while temp <= end:
    #         convo_metrics(start,inboxID,inboxName)
    #         temp += delta
    #     df = pd.DataFrame(analytics)
    #     df.append(pd.Series(), ignore_index=True)
    #     df.to_csv('analytics.csv', mode='a',index=False)

    while start <= end:
        print("-----------")
        print(start)
        for inboxID,inboxName in inboxes.items():
            convo_metrics(start,inboxID,inboxName)
        start += delta
        analytics.append({})
    df = pd.DataFrame(analytics)
    print(df)
    df.to_csv('analytics.csv', mode='w',index=False)

    # for m in range(1,13):
    #     # Getting the data.
    #     day = [2020,m,1]
    #     dates = get_epoch_values(day)
    #     convo_metrics(day,dates)

    # pd.DataFrame(analytics).to_csv('analytics.csv', mode='a',index=False)
    # print("")

def main():
    print("Enter a start date in the format YYYY-MM-DD:")
    start = dp.isoparse(input())
    print("Enter an end date (inclusive) in the format YYYY-MM-DD:")
    end = dp.isoparse(input())

    get_stats(start,end)

if __name__ == "__main__":
    main()