import requests
import json
from bs4 import BeautifulSoup

# use this to get json
# IMPORTANT NOTE: It's not possible to get a full list of an user's stories.
# You can only get THREE of them. 
# With metadataJSON['metadata']['data'][0]['stories']['total] you can get a number of the user's total stories count.
# User lists and conversations/comments are not aviable til yet.
def extractInformationFromWattpad(url):
    # wattpad.com/story/-URLs don't include the metadata.
    # Nobody knows why BUT we can still get the information by getting the json of
    # the first part.
    isstory = False
    if "wattpad.com/story/" in url:
        isstory = True
        originalurl = url
        firstparturl = extractFirstPartLink(url)
        url = firstparturl
    try:
        # user-agent header is important, otherwise wattpad will return a 403 Forbidden:
        mozillaheader = {
            "User-Agent": "Mozilla/5.0"
            }
        response = requests.get(url, headers=mozillaheader)
        if response.ok == False:
            print("Network response was not OK: " , response.status_code)
        pagesourcecode = response.text
        
        # searching the point 'window.prefetched' in source code, which contains the informations:
        start_index = pagesourcecode.find('window.prefetched')
        if start_index == -1:
            # couldn't find 'window.prefetched', so lets return none:
            return None
        
        # find the beginning of the JSON by searching for a {:
        open_brace_index = pagesourcecode.find('{', start_index)

        # find the end of the JSON by counting the number of { and }:
        open_braces_count = 1
        end_index = open_brace_index + 1

        while open_braces_count > 0:
            if pagesourcecode[end_index] == '{':
                open_braces_count += 1
            elif pagesourcecode[end_index] == '}':
                open_braces_count -= 1
            end_index += 1

        # extract the JSON:
        jsonCode = pagesourcecode[open_brace_index:end_index]

        try:
            # try to parse it:
            parsedData = json.loads(jsonCode)
            if "wattpad.com/user/" in url :
                metadataoriginalkey, worksoriginalkey, latestactivityoriginalkey = parsedData.keys()
                metadata = parsedData[metadataoriginalkey]
                works = parsedData[worksoriginalkey]
                latestactivity = parsedData[latestactivityoriginalkey]
                finaljson = {
                    "metadata": metadata,
                    "works": works,
                    "latestactivity": latestactivity
                }
            else:
                try:
                    metadataoriginalkey = list(parsedData.keys())[0]
                    metadata = parsedData[metadataoriginalkey]
                    finaljson = {
                        "metadata": metadata
                    }
                except Exception as error:
                    print("An Error occurred - maybe a broken link?\nYou can only get wattpad link to user profiles, stories or story-parts.\nPlease read the README.\nError: " , error)
            return finaljson
        except Exception as error:
            print("Error while parsing the JSON: ", error)
    except Exception as error:
        print("An Error occurred: ", error)


# Code to extract the link to the first part of a book of the wattpad.com/story/xyz URL:
def extractFirstPartLink(url):
    try:
        mozillaheader = {
            "User-Agent": "Mozilla/5.0"
            }
        response = requests.get(url, headers=mozillaheader)
        if response.ok == False:
            print("Network response was not OK: " , response.status_code)
        sourcecode = response.text

        soup = BeautifulSoup(sourcecode, "html.parser")

         # find "start reading" button in source code which contains the link:
        readBtnElement = soup.find("a", class_="read-btn")
        # check if found and return link:
        if readBtnElement:
            link = readBtnElement["href"]
            print(link)
            return "https://www.wattpad.com" + link
        else:
            print("error :(")
            return "error!"
    except Exception as error:
        print("paring error:", error)
        return "error!"