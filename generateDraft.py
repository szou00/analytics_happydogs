"""Front Automatic Draft Generator

This script uses the Front API to review emails and draft replies with
response templates when necessary. 

This script requires that `requests` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * 
    * main - the main function of the script
"""

import requests
import json
import time
import datetime
import os.path

AUTO_REVIEWED = "tag_mmo1x"
AUTO_REVIEW_NEEDED = "tag_mmlvp"
BEARER_TOKEN = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'


def print_JSON_object(JSON_object):
    """Prints a reader-friendly, formatted string of a JSON object. 

    Args:
        obj (JSON object): A JSON Object from an API request

    Returns:
        None
    """
    formatted_string = json.dumps(JSON_object, sort_keys=True, indent=4)
    print(formatted_string)


def tag_new_events():
    """Tags emails that have new activity with 'AUTO-review-needed'

    Args:
        None

    Returns:
        None
    """
    time_of_last_run = load_last_run_time().timestamp() 
    url = "https://api2.frontapp.com/events?q[types]=comment&q[types]=inbound\
           &q[after]=" + str(time_of_last_run)
    payload = {}
    headers = {'Authorization': BEARER_TOKEN}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response)
    events = response.json()["_results"]
    for event in events:
        email = event["conversation"]
        convo_ID = email["id"] 
        remove_tag(convo_ID,AUTO_REVIEWED) # if the email was marked as AUTO-reviewed, untag it
        add_tag(convo_ID,AUTO_REVIEW_NEEDED) # now add AUTO-review-needed tag
        print("Flagged:" + email["subject"])
    save_current_run_time()


def review_tagged_conversations():
    """Review conversations with 'AUTO-review-needed' tag.

    If applicable, drafts will be created for conversations
    that need them. 

    Args:
        None

    Returns:
        None
    """
    url = "https://api2.frontapp.com/conversations/search/tag:" \
          + AUTO_REVIEW_NEEDED
    payload = {}
    files = []
    headers = {'Authorization': BEARER_TOKEN}
    response = requests.request("GET", url, headers=headers, 
                                data=payload, files=files)

    emails = response.json()["_results"]
    for email in emails:  
        convo_ID = email["id"]
        for tag in email["tags"]:
            # CREATE DRAFT HERE
            if tag["name"] == "example-tag": # simple example of draft being created based on a tag
                create_draft(convo_ID,"rsp_3rd8l")
        get_comments(convo_ID) # placeholder
        remove_tag(convo_ID,AUTO_REVIEW_NEEDED) # removes AUTO-review-needed tag
        add_tag(convo_ID,AUTO_REVIEWED) # adds AUTO-reviewed tag
        print("Reviewed:" + email["subject"])


def get_canned_response(template_ID):
    """Retrieves message template. 
    
    Helper function for create_draft(convo_ID,template_ID).

    Args:
        template_ID: A string containing the ID of the response template

    Returns:
        response_template.json(): A JSON object of the response template
    """
    url = "https://api2.frontapp.com/responses/" + template_ID
    payload = {}
    files = []
    headers = {'Authorization': BEARER_TOKEN}

    response_template = requests.request("GET", url, headers=headers, 
                                        data=payload, files=files)
    return response_template.json()


def create_draft(convo_ID, template_ID):
    """Drafts a reply accordingly using a response template.    

    Args:
        convo_ID: A string containing the ID of the conversation to reply to
        template_ID: A string containing the ID of response template

    Returns:
        None
    """
    response_template = get_canned_response(template_ID)
    url = "https://api2.frontapp.com/conversations/" + convo_ID + "/drafts"
    payload = { 
        'body': response_template["body"],
        'subject': response_template["subject"],
        'author_id': 'tea_188ud', # [needs to change later on]
        'channel_id': 'cha_14tfp' # [also will need to be changed for team based settings]
        } 
    files = []
    headers = {'Authorization': BEARER_TOKEN}
    requests.request("POST", url, headers=headers, json=payload, files=files)


def add_tag(convo_ID,tag_ID):
    """Add tag to a conversation.   

    Args:
        convo_ID: A string containing the ID of the conversation
        tag_ID: A string containing the ID of the tag to add 

    Returns:
        None
    """
    url = "https://api2.frontapp.com/conversations/" + convo_ID + "/tags"
    payload = json.dumps({ "tag_ids": [tag_ID]})
    headers = {'Authorization': BEARER_TOKEN,
               'Content-Type': 'application/json'
    }
    requests.request("POST", url, headers=headers, data=payload)


def remove_tag(convo_ID,tag_ID):
    """Removes tags from a conversation.   

    Args:
        convo_ID: A string containing the ID of the conversation 
        tag_ID: A string containing the ID of the tag to remove

    Returns:
        None
    """
    url = "https://api2.frontapp.com/conversations/" + convo_ID + "/tags"
    payload = json.dumps({ "tag_ids": [tag_ID]})
    headers = {'Authorization': BEARER_TOKEN,
               'Content-Type': 'application/json'
               }
    requests.request("DELETE", url, headers=headers, data=payload)


def get_comments(convo_ID):
    """Retreives comments from a given conversation. 
    
    This is a useful function to help decide which draft template to use. 

    Args:
        convoID: A string containing the ID of the conversation

    Returns:
        None
    """
    url = "https://api2.frontapp.com/conversations/" + convo_ID + "/comments"
    payload = {}
    headers = {'Authorization': BEARER_TOKEN}
    response = requests.request("GET", url, headers=headers, data=payload)
    for comment in response.json()["_results"]:
        print_JSON_object(comment["body"])


def save_current_run_time():
    """Writes the current time to a file.
       
    Args:
        None

    Returns:
        None
    """
    path = '/Users/szou/Downloads/bu/happydogs/analytics_happydogs/lastjob' # hard coding this due to CRON, but will remove later
    output_file = open(path,'w')
    current_time_string = datetime.datetime.strftime(datetime.datetime.now(),
                                                     "%Y-%m-%d %H:%M:%S")
    output_file.write(current_time_string)
    print(current_time_string)
    output_file.close()


def load_last_run_time():
    """Retrieves the last time the program was ran from the file. 
    
    This increases efficiency by bypassing events that were already looked at. 

    Args:
        None

    Returns:
        None
    """
    path = '/Users/szou/Downloads/bu/happydogs/analytics_happydogs/lastjob'
    if (os.path.isfile(path)): # if the file exists
        f = open(path,'r')
        lastJob = datetime.datetime.strptime(f.read(),"%Y-%m-%d %H:%M:%S")
        f.close()
        return lastJob
    save_current_run_time()
    return datetime.datetime.now() # if file doesn't exist (possible if it's the first run), return current time


def main():
    print("\n") # for easier CRON output viewing, separating each output
    tag_new_events()
    time.sleep(10)
    review_tagged_conversations()
    # create_draft("cnv_8rjow91", "rsp_3rd8l")

# to run the CRON JOB: */5 * * * * /Users/szou/Downloads/bu/happydogs/analytics_happydogs/env/bin/python 
# /Users/szou/Downloads/bu/happydogs/analytics_happydogs/generateDraft.py 
# >>/Users/szou/Downloads/bu/happydogs/analytics_happydogs/CRONoutput.log 2>&1

if __name__ == "__main__":
    main()
