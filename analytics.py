import requests
import json
import datetime
import pandas as pd
import dateutil.parser as dateparser
import time
import sys

# Global variable to store a list of dictionaries where key=tag, value=number of convos
analytics = []
BEARER_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsic2hhcmVkOioiXSwiaWF0IjoxNjI2NzExMDI2LCJpc3MiOiJmcm9udCIsInN1YiI6ImhhcHB5X2RvZ3NfbnljIiwianRpIjoiZTUxYWFkNGM5Y2E3ODlhMiJ9.xZAyAkDSlxcaKYj9rhozowo84zBMVH4q7X0lGNZttn0"


def print_JSON_object(JSON_object):
    """Prints a formatted string of a JSON object. 

        Parameters:
            obj: A Javascript Object

        Returns:
            None
    """
    text = json.dumps(JSON_object, sort_keys=True, indent=4)
    print(text)


def obtain_convo_metrics(day, inboxID, inboxName, interval):
    """Requests information from the Front API and appends that information to a list. 
        
    Args: 
        day (Datetime obj): A Datetime object
        inboxID (str): Inbox ID
        inboxName (str): Nme of the inbox 
        interval (str): Length of the interval to look at
    Returns:
        None
    """

    convoInfo = {}
    startDay = day  # keep track of start

    start = str(day.timestamp())
    delta = datetime.timedelta(days=interval)
    day += delta
    end = str(day.timestamp())

    url = (
        "https://api2.frontapp.com/analytics?start="
        + start
        + "&end="
        + end
        + "&metrics[0]id=tags_table&metrics[0]metric_type=table&inbox_ids[0]="
        + inboxID
    )

    payload = {}
    files = {}
    headers = {"Authorization": BEARER_TOKEN}

    requests.request(
        "GET", url, headers=headers, data=payload, files=files
    )  # first request triggers the calculation on the back-end

    time.sleep(0.5)  # giving the API enough time to finish the calculation

    response = requests.request(
        "GET", url, headers=headers, data=payload, files=files
    )  # second request actually gets the calculation now!

    metrics = response.json()["metrics"]
    tags = metrics[0]["rows"]

    for tag in tags:
        name = tag[0]["v"]
        num_of_open_convos = tag[3]["v"]
        convoInfo["Date"] = startDay
        convoInfo["Inbox"] = inboxName
        convoInfo["Tag"] = name
        convoInfo["Num"] = num_of_open_convos
        analytics.append(convoInfo)
        convoInfo = {}


def get_stats(start, end, interval):
    """Use analytics of email tags on Front App to generaete a CSV file. 
    
    Args: 
        start (datetime obj): The beginning of the time period to get stats of 
        end (datetime obj): The end of the time period to get stats of
        interval (int): The interval to get stats of during that time period
                        Default is 7, which lets the program look at every Monday's statistics. 
    Returns:
        None
    """
    delta = datetime.timedelta(days=interval)
    inboxes = {
        "inb_ejh1": "234",
        "inb_fu2t": "403",
        "inb_fu4d": "504",
        "inb_fu8t": "208",
    }

    while start <= end:
        print(start)
        for inboxID, inboxName in inboxes.items():
            obtain_convo_metrics(start, inboxID, inboxName, interval)
        start += delta

    dataframe = pd.DataFrame(analytics)
    dataframe.to_csv("analytics.csv", mode="w", index=False)


def main():
    try:
        start = dateparser.isoparse(sys.argv[1])
        end = dateparser.isoparse(sys.argv[2])

        if (start > end) or (start > datetime.datetime.now()):
            raise ValueError
        if len(sys.argv) == 4:  # if a custom interval is time is inputted, use that
            interval = int(sys.argv[3])
            get_stats(start, end, interval)
        else:  # otherwise use a week as default, and look at every Monday's statistics specifically
            start = start - datetime.timedelta(days=start.weekday())
            get_stats(start, end, 7)
    except IndexError:
        print("\nExpected 2 or more command line arguments")
        print("Ex: 'python analytics.py 20210721 20210723'\n")
        exit(1)
    except ValueError:
        print(
            "\nDates are invalid: make sure they are in the format YYYYMMDD, are in the present,"
        )
        print("and start date is earlier than end date\n")
        exit(1)


if __name__ == "__main__":
    main()
