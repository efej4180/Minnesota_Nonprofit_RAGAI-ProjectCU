import os
import requests # used to make HTTP requests to a specific url
from bs4 import BeautifulSoup # makes our requests cute and readable to us as humans
import json
import sys
import time
import csv
import pandas as pd
import traceback

"""
This script collects and enriches nonprofit organization data for use in training
a Retrieval-Augmented Generation (RAG) AI system for a nonprofit organization.

It performs the following main tasks:
1. Scrapes nonprofit organization data from ProPublica's Nonprofit Explorer API,
   filtered by NTEE category and state (Minnesota).
2. Supplements scraped data with additional information from:
   - Local CSV files containing manually curated details such as websites, activity
     areas, primary communities served, and contact numbers.
   - The Every.org API, adding tags, cause categories, and missing website URLs.
3. (Optional/Planned) Scrapes nonprofit websites to extract relevant text for training.

Key Functions:
- scrape_nonprofits():
    Iterates through multiple NTEE categories and pages from the ProPublica API,
    building a list of nonprofits in Minnesota.
- supplement_orgs_from_csv():
    Merges supplemental CSV data with the scraped dataset using EIN as the unique key.
- supplement_orgs_from_everyorg(csv_file):
    Calls the Every.org API to append tags, cause categories, and missing websites.
    Also ensures incremental progress saving in case of failure.
- scrape_website(csv_file):
    (Incomplete) Intended to request each nonprofit's website and extract relevant
    textual content for the dataset.

Outputs:
- Intermediate and final CSV files containing cleaned, supplemented, and enriched
  nonprofit datasets for AI model training.
"""

def scrape_nonprofits():

   page_number = 0
   done = False
   nonprofits = []
   progress = 0
   for ntee_id in range(1,11):
        while done is not True:
            # submitting a get request to whatever the frick
            initial_request = requests.get(f"https://projects.propublica.org/nonprofits/api/v2/search.json?state%5Bid%5D=MN&ntee%5Bid%5D={ntee_id}&page={page_number}")

            if initial_request.status_code != 200:
                print("Something wrong with the request bud, Error: " + str(initial_request.status_code))
                sys.exit()


                

            # our request is given to us in json, so lets use the jsons methods in requests! this basically makes our request a dictionary.
            initial_request_json = (initial_request.json())

            #if we're on the last page
            if (page_number == (initial_request_json["num_pages"] - 1)):
                done = True

            page_nonprofits = initial_request_json["organizations"]
            for nonprofit in page_nonprofits:
                nonprofits.append(nonprofit)
            
            
            page_number += 1
            print(page_number)
            

        done = False
        page_number = 0
        progress += 1
        print(progress)
   print(len(nonprofits))


   return nonprofits

    
    



    
def supplement_orgs_from_csv():
    nonprofits = pd.read_csv("nonprofit and supplemental.csv")
    supplements = pd.read_csv("supplemental.csv") 

    supplements = supplements.to_dict('index')
    nonprofits = nonprofits.to_dict('records')

    for supplement in supplements.values():
        supplement["EIN"] = str(supplement["EIN"])
        supplement["EIN"] = (supplement["EIN"]).replace("-", "")
        if supplement["EIN"].isdigit() is False:
            supplement["EIN"] = "0"
        supplement["EIN"] = int(supplement["EIN"])

    nonprofits_by_ein = {nonprofit["ein"]: nonprofit for nonprofit in nonprofits}

    for _, supplemental in supplements.items():
        ein = supplemental["EIN"]
        if supplemental["EIN"] in nonprofits_by_ein.keys():
            nonprofits_by_ein[ein]["Website"] = supplemental.get("Website", "N/A")
            nonprofits_by_ein[ein]["Activity Area"] = supplemental.get("Activity Area", "N/A")
            nonprofits_by_ein[ein]["Primary Community Served"] = supplemental.get("Primary Community Served", "N/A")
            nonprofits_by_ein[ein]["Phone"] = supplemental.get("Phone", "N/A")


    nonprofit_df = pd.DataFrame.from_dict(nonprofits_by_ein, orient= "index")
    nonprofit_df.to_csv("gotta backdoor.csv", index = False)



def supplement_orgs_from_everyorg(csv_file):
    nonprofits = pd.read_csv(csv_file)
    nonprofits = nonprofits.to_dict('records')

    try:
        for nonprofit in nonprofits:
            if nonprofit["Progress"] == "Supplemented from Every.org":
                continue
                         
            ein = nonprofit["ein"]
            everyorg_nonprofit = requests.get(f"https://partners.every.org/v0.2/nonprofit/{ein}?apiKey=pk_live_2f649154dba71ef883a0fcfb820126d6")
            everyorg_nonprofit = everyorg_nonprofit.json()
            nonprofit["Tags"] = ""

            for fields in everyorg_nonprofit.get("data",{}).get("nonprofitTags",[]):
                nonprofit["Tags"] += "Cause Category: " + fields.get("causeCategory") + ", " + "Tag Name: " +  (fields.get("tagName") + ", ")
                
                if nonprofit["Website"] is None or (str(nonprofit["Website"])).strip() == "":
                    nonprofit["Website"] = everyorg_nonprofit.get("data",{}).get("nonprofit",{}).get("websiteUrl")

            time.sleep(0.8)  # Sleep to avoid hitting rate limits
            nonprofit["Progress"] = "Supplemented from Every.org"

    except Exception as e:
       nonprofit_df = pd.DataFrame.from_records(nonprofits)
       nonprofit_df.to_csv("holy grail (incomplete) v2.csv", index = False)
       print(f"Script crashed: {e}")
       traceback.print_exc()

    nonprofit_df = pd.DataFrame.from_records(nonprofits)
    nonprofit_df.to_csv("holy grail.csv v2", index = False)

def scrape_website(csv_file):
    nonprofits = pd.read_csv(csv_file)
    nonprofits = nonprofits.to_dict('records')

    for nonprofit in nonprofits:
        if nonprofit["Website"] is not None or (str(nonprofit["Website"])).strip() != "":
            url = nonprofit["Website"]
            website_request = requests.get(url)
            status = website_request.status_code
            if status != 200:
                nonprofit["Website Results"] = "Not code 200"
                continue
            


            #trafilatura extraction goes here

            nonprofit["Website Results"] = extraction
            
            



supplement_orgs_from_everyorg("holy grail (incomplete).csv")



