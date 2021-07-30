"""Retrieve Front Analytics

This script uses the Front API to create a CSV file with analytics about
emails.

This script requires that `requests`, `pandas`, and `dateutil` be 
installed within the Python environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * print_stats_to_CSV: prints analytics to CSV file
    * obtain_convo_metrics: retrieves all the analytics needed
    * print_JSON_object: print JSON object in a friendly format
    * main: the main function of the script, here it retrieves metrics, and then prints it to CSV file

Author: Sharon Zou
"""

import requests
import json
import datetime
import pandas as pd
from dateutil import parser as dateparser
import time
import sys
import socket

# Global variable to store the list of analytics to write into CSV file.
analytics = []
BEARER_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsic2hhcmVkOioiXSwiaWF0IjoxNjI2NzExMDI2LCJpc3MiOiJmcm9udCIsInN1YiI6ImhhcHB5X2RvZ3NfbnljIiwianRpIjoiZTUxYWFkNGM5Y2E3ODlhMiJ9.xZAyAkDSlxcaKYj9rhozowo84zBMVH4q7X0lGNZttn0"


def print_JSON_object(JSON_object):
    """Prints a formatted string of a JSON object. 

    This lets us view analytics from Front in a much 
    friendlier format. 

    Args:
        obj (JSON object): A JSON Object from an API request

    Returns:
        None
    """
    text = json.dumps(JSON_object, sort_keys=True, indent=4)
    print(text)


def obtain_tag_metrics(day, inbox_ID, inbox_name, interval):
    """Helper method. Requests information from the Front API and appends that information to a list. 
        
    Args: 
        day (Datetime obj): A Datetime object
        inbox_ID (str): Inbox ID
        inbox_name (str): Nme of the inbox 
        interval (str): Length of the interval to look at
    Returns:
        None
    """

    # Create start and end, two EPOCH time parameters, to pass into the API request
    start = str(day.timestamp())
    delta = datetime.timedelta(days=interval)
    end = str((day + delta).timestamp())

    # Make a request to the Front API
    # Requires us to make two API requests to the same endpoint:
    # The first request triggers the calculation on the back-end,
    # program will sleep for a short time to allow the calculation to finish,
    # and then the second request will retrieve the actual calculation
    url = (
        "https://api2.frontapp.com/analytics?start="
        + start
        + "&end="
        + end
        + "&metrics[0]id=tags_table&metrics[0]metric_type=table&inbox_ids[0]="
        + inbox_ID
    )
    payload = {}
    files = {}
    headers = {"Authorization": BEARER_TOKEN}
    requests.request("GET", url, headers=headers, data=payload, files=files)
    time.sleep(0.5)
    response = requests.request("GET", url, headers=headers, data=payload, files=files)

    # Grab information associated with each tag and append it to the list
    metrics = response.json()["metrics"]
    tags = metrics[0]["rows"]
    tagInfo = {}
    for tag in tags:
        name = tag[0]["v"]
        num_of_open_convos = tag[3]["v"]
        tagInfo["Date"] = day
        tagInfo["Inbox"] = inbox_name
        tagInfo["Tag"] = name
        tagInfo["Num"] = num_of_open_convos
        analytics.append(tagInfo)
        tagInfo = {}


def print_stats_to_CSV(start, end, interval):
    """Use analytics of email tags on Front App to generate a CSV file. 
    
    Args: 
        start (datetime obj): The beginning of the time period to get stats of 
        end (datetime obj): The end of the time period to get stats of
        interval (int): The interval to get stats of during that time period
                        Default is 7, which lets the program look at every Monday's statistics. 
    Returns:
        None
    """
    # Loop through dates. For each day, loop through inboxes and obtain tag
    # analytics by calling a helper function
    inboxes = {
        "inb_ejh1": "234",
        "inb_fu2t": "403",
        "inb_fu4d": "504",
        "inb_fu8t": "208",
    }
    delta = datetime.timedelta(days=interval)
    while start <= end:
        for inboxID, inboxName in inboxes.items():
            obtain_tag_metrics(start, inboxID, inboxName, interval)
        print("Success: " + str(start))
        start += delta

    # Write all the obtained analytics to a CSV file by using pandas
    dataframe = pd.DataFrame(analytics)
    dataframe.to_csv("analytics.csv", mode="w", index=False)


def main():
    try:
        # Turn date strings into Datetime Objects (increases functionality)
        start = dateparser.isoparse(sys.argv[1])
        end = dateparser.isoparse(sys.argv[2])

        if (start > end) or (start > datetime.datetime.now()):
            # If end dates are earlier than start dates, or the start date is in
            # the future, raise an error
            raise ValueError
        if len(sys.argv) == 4:
            # If a custom interval is inputted, use that to look at
            # and create analytics table
            interval = int(sys.argv[3])
            print_stats_to_CSV(start, end, interval)
        else:
            # If no custom interval is inputted, use a week as default interval.
            # We will look at every Monday's statistics specifically
            start = start - datetime.timedelta(days=start.weekday())
            print_stats_to_CSV(start, end, 7)
    except IndexError:
        # If program doesn't detect more than 2 command line arguments,
        # print out corresponding error message
        print("\nExpected 2 or more command line arguments")
        print(
            "Ex: 'python analytics.py 20210721 20210723', or"
            "'python analytics.py 20210721 20210723 1'\n"
        )
        exit(1)
    except ValueError:
        # If program detects dates in invalid formats, print out corresponding error message
        print("\nDates are invalid. Make sure: ")
        print("- they are in the format YYYYMMDD")
        print("- and start date is earlier than end date")
        print("- are in the present")
        exit(1)
    except socket.error:
        # If program loses connection and can't successfully call the Front API,
        # print out corresponding error message
        print("\nCan't connect to Front :(\n")
        exit(1)


if __name__ == "__main__":
    main()
