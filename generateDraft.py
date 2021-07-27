import requests
import json
import time
import datetime
import os.path


def jprint(obj):
    """Prints a formatted string of a JSON object. Used for easier viewing purposes.

        Parameters:
            obj: A Javascript Object

        Returns:
            None
    """
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def tag_events():
    """Retrieves emails that are inbound or commented on and tags them with 'AUTO-review-needed'

        Parameters:
            None

        Returns:
            None
    """
    lastJob = load().timestamp() # loads the last time the events were reviewed. only looks at events past that

    url = "https://api2.frontapp.com/events?q[types]=comment&q[types]=inbound&q[after]=" + str(lastJob)

    payload = {}
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    events = response.json()["_results"]
    # jprint(events)
    for event in events:
        email = event["conversation"]
        convoID = email["id"] 
        print(email["subject"])
        remove_tag(convoID,"tag_mmo1x") # if the email was marked as AUTO-reviewed, untag it
        add_tag(convoID,"tag_mmlvp") # now add AUTO-review-needed tag
        print("tagged " + convoID) 


def go_thru_convos():
    """Goes through all the conversations that have the tag 'AUTO-review-needed' and creates drafts as 
       necessary.  

        Parameters:
            None

        Returns:
            None
    """

    url = "https://api2.frontapp.com/conversations/search/tag:tag_mmlvp"

    payload = {}
    files = []
    
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'
    }

    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    emails = response.json()["_results"]

    for email in emails:  
        convoID = email["id"] 
        # jprint(convoID)
        for tag in email["tags"]:
            # CREATE DRAFT HERE
            if tag["name"] == "example-tag": # simple example of draft being created based on a tag
                create_draft(convoID)
        retrieve_comments(convoID) # placeholder
        remove_tag(convoID,"tag_mmlvp") # removes AUTO-review-needed tag
        add_tag(convoID,"tag_mmo1x") # adds AUTO-reviewed tag


def get_canned_response(templateID):
    """Get message template. Currently only gets a certain one. [NEEDS FIXING]

        Parameters:
            templateID: A string containing the ID of the response template

        Returns:
            cannedResponse.json(): A JSON object containing the details of the response template
    """
    url = "https://api2.frontapp.com/responses/" + templateID
    payload = {}
    files = []
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'
    }

    cannedResponse = requests.request("GET", url, headers=headers, data=payload, files=files)
    return cannedResponse.json()


def create_draft(convoID):
    """Drafts a reply accordingly using a canned response.    

        Parameters:
            convoID: A string containing the ID of the conversation to reply to

        Returns:
            None
    """
    cannedResponse = get_canned_response("rsp_3rd8l")

    url = "https://api2.frontapp.com/conversations/" + convoID + "/drafts"

    payload = { 'body': cannedResponse["body"],
                'subject': cannedResponse["subject"],
                'author_id': 'tea_188ud', # [needs to change later on]
                'channel_id': 'cha_14tfp'} # [also will need to be changed for team based settings]
    files = []
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'
    }

    requests.request("POST", url, headers=headers, json=payload, files=files)

# just to keep track for now - 
# tag for 'AUTO-review-needed' : tag_mmlvp
# tag for 'AUTO-reviewed' : tag_mmo1x
def add_tag(convoID,tagID):
    """Adds tags to conversation.   

        Parameters:
            convoID: A string containing the ID of the conversation to add tags to
            tagID: A string containing the ID of the tag to add 

        Returns:
            None
    """
    url = "https://api2.frontapp.com/conversations/" + convoID + "/tags"

    payload = json.dumps({ "tag_ids": [tagID]})
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU',
    'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)


def remove_tag(convoID,tagID):
    """Removes tags from a conversation.   

        Parameters:
            convoID: A string containing the ID of the conversation to remove tags from
            tagID: A string containing the ID of the tag to remove

        Returns:
            None
    """
    url = "https://api2.frontapp.com/conversations/" + convoID + "/tags"

    payload = json.dumps({ "tag_ids": [tagID]})
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU',
    'Content-Type': 'application/json'
    }

    requests.request("DELETE", url, headers=headers, data=payload)


def retrieve_comments(convoID):
    """Retreives comments from a given conversation. Useful for deciding what template to use. 

        Parameters:
            convoID: A string containing the ID of the conversation to retrieve comments from

        Returns:
            None
    """
    url = "https://api2.frontapp.com/conversations/" + convoID + "/comments"
    payload = {}
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    for comment in response.json()["_results"]:
        jprint(comment["body"])


def save():
    """Writes the current time to a file.
       
       Parameters:
            None

        Returns:
            None
    """
    f = open('lastjob','w')
    f.write(datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S"))
    f.close()


def load():
    """Retrieves the last time the program was ran from the file. This way, we won't have to look at
       events that were already looked at. 

       Parameters:
            None

        Returns:
            None
    """
    if (os.path.isfile('lastjob')): # if the file exists
        f = open('lastjob','r')
        lastJob = datetime.datetime.strptime(f.read(),"%Y-%m-%d %H:%M:%S")
        f.close()
        return lastJob
    save()
    return datetime.datetime.now() # if file doesn't exist (possible if it's the first run), return current time


def main():
    tag_events()
    save()
    time.sleep(5)
    go_thru_convos()


if __name__ == "__main__":
    main()
