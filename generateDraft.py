import requests
import json

def jprint(obj):
    """Prints a formatted string of a JSON object. 

        Parameters:
            obj: A Javascript Object

        Returns:
            None
    """
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def go_thru_convos():
    """Retrieves all the open conversations. Placeholder(?) until I figure out how to work Events.  

        Parameters:
            None

        Returns:
            None
    """
    url = "https://api2.frontapp.com/conversations/search/is:open"

    payload = {}
    files = []
    
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'
    }

    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    emails = response.json()["_results"]

    for email in emails:  
        convoID = email["id"] # retreiving the tag from the conversation object
        # jprint(convoID)
        for tag in email["tags"]:
            if tag["name"] == "example-tag":
                jprint(convoID)
                jprint(tag["name"])
                create_draft(convoID)
                remove_tag(convoID)
                retrieve_comments(convoID)


def get_canned_response(templateID):
    """Get message template. Currently only gets a certain one.   

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
    # jprint(cannedResponse)

    url = "https://api2.frontapp.com/conversations/" + convoID + "/drafts"

    payload = { 'body': cannedResponse["body"],
                'subject': cannedResponse["subject"],
                'author_id': 'tea_188ud',
                'channel_id': 'cha_14tfp'}
    files = []
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU'
    }

    requests.request("POST", url, headers=headers, json=payload, files=files)

    # jprint(response.json())        

def add_tag(convoID):
    """Adds tags to conversation.   

        Parameters:
            convoID: A string containing the ID of the conversation to add tags to

        Returns:
            None
    """
    url = "https://api2.frontapp.com/conversations/" + convoID + "/tags"

    payload = json.dumps({ "tag_ids": ["tag_mkipx","tag_mld1h"]})
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU',
    'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)

# only adds in two specific tags
def remove_tag(convoID):
    """Removes tags from a conversation.   

        Parameters:
            convoID: A string containing the ID of the conversation to remove tags from

        Returns:
            None
    """

    url = "https://api2.frontapp.com/conversations/" + convoID + "/tags"

    payload = json.dumps({ "tag_ids": ["tag_mkipx","tag_mld1h"]})
    headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsicHJpdmF0ZToqIl0sImlhdCI6MTYyNjk4MTM5NSwiaXNzIjoiZnJvbnQiLCJzdWIiOiJoYXBweV9kb2dzX255YyIsImp0aSI6IjBiNjJkNWMzYTRmMWExMzQifQ.IPviahR63lerU4f1zJmBZGkDTW1nA3GXy2zr_gGgVPU',
    'Content-Type': 'application/json'
    }

    requests.request("DELETE", url, headers=headers, data=payload)

def retrieve_comments(convoID):
    """Retreives comments from a given conversation.  

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



def main():
    go_thru_convos()

if __name__ == "__main__":
    main()
