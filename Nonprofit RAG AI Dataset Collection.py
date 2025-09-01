import os
import requests # used to make HTTP requests to a specific url
from bs4 import BeautifulSoup # makes our requests cute and readable to us as humans
import json
import sys
import time
import csv
import pandas as pd
import traceback
from urllib.parse import urljoin
from langchain_text_splitters import RecursiveCharacterTextSplitter


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
    nonprofit_df.to_csv("holy grail v2.csv", index = False)

def scrape_website_for_sub_pages(csv_file):
    nonprofits = pd.read_csv(csv_file)
    nonprofits = nonprofits.to_dict('records')
    try:
        
        for nonprofit in nonprofits:
            #if the nonprofit row has a website value | basically if we have the nonprofit's website.
            if pd.isna(nonprofit["Website"]) is False:
                
                #take the url
                url = nonprofit["Website"]
                try:
                    #attempt to make a request ot the website
                    website_request = requests.get(url)
                    status = website_request.status_code

                    #if it doesn't work we don't want to stop, just keep going and say the specific one failed.
                except requests.exceptions.RequestException as e:
                    # catch other request-related errors
                    print(f"Request failed for {url}: {e}")
                

                #take all of the website text
                website_html = website_request.text

                #use the html parser to find all of the links
                soup = BeautifulSoup(website_html, "html.parser")
                website_links = soup.find_all("a")
                link_list = []
                for link in website_links:

                    #ignore empty values
                    if link.get("href") is None:
                        continue


                    full_link = urljoin(url, link.get("href"))
                    

                    if full_link.startswith(url):
                        link_list.append(full_link)
                
                #use a set to remove all of the duplicates then make that set back into a list, containing all of the unique sub pages for the website.
                unique_links = list(set(link_list))
                nonprofit["Subpages"] = "\n".join(unique_links)
                nonprofit["Subpages Progress"] = "Progressed"

                
    except Exception as e:
        nonprofit_df = pd.DataFrame.from_records(nonprofits)
        nonprofit_df.to_csv("holy grail (incomplete) v3.csv", index = False)
        print(nonprofit)
        print(f"Script crashed: {e}")
        traceback.print_exc()

    nonprofit_df = pd.DataFrame.from_records(nonprofits)
    nonprofit_df.to_csv("holy grail v3.csv", index = False)
        


def chunk_subpages(csv_file):
    nonprofits = pd.read_csv(csv_file)
    nonprofits = nonprofits.to_dict('records')

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size  = 100,
        chunk_overlap = 50,
        length_function = len,
    )

    
    chunk_dataset = []

    try:
        
        for nonprofit in nonprofits:
            #if the nonprofit row has a website value | basically if we have the nonprofit's website.
            if pd.isna(nonprofit["Subpages"]) is False:

                urls = (nonprofit["Subpages"]).split("\n")
                suburl_index = 0
                for url in urls:
                    try:
                        #attempt to make a request ot the website
                        website_request = requests.get(url)
                        

                    #if it doesn't work we don't want to stop, just keep going and say the specific one failed.
                    except requests.exceptions.RequestException as e:
                        # catch other request-related errors
                        print(f"Request failed for {url}: {e}")
                        continue
                    soup = BeautifulSoup(website_request.text, "html.parser")

                    # Remove script and style tags
                    for script in soup(["script", "style"]):
                        script.extract()

                    # Get readable text
                    text = soup.get_text(separator="\n", strip=True)

                    chunks = text_splitter.create_documents([text])
                    chunk_index = 0
                    for chunk in chunks:
                        chunk_row = nonprofit.copy()
                        chunk_row["id"] = f"{nonprofit['ein']}_{suburl_index}_{chunk_index}"
                        chunk_row["chunk_index"] = chunk_index
                        chunk_row["chunk_text"] = chunk.page_content
                        chunk_row["source_url"] = url
                        chunk_dataset.append(chunk_row)
                        chunk_index += 1

                    suburl_index += 1
                #idk if this is right
                #chunks_by_id = {chunk_row["chunk_id"]: chunk_row for nonprofit in nonprofits}



    except Exception as e:
        nonprofit_df = pd.DataFrame.from_records(nonprofits)
        nonprofit_df.to_csv("holy grail (incomplete) v3.csv", index = False)
        print(nonprofit)
        print(f"Script crashed: {e}")
        traceback.print_exc()

    chunk_dataset = pd.DataFrame.from_records(chunk_dataset)
    chunk_dataset.to_csv("snipe of doom v1.csv", index = False)
                            
                        


    

nonprofits = pd.read_csv("holy grail.csv")
nonprofits = nonprofits.to_dict('records')

print(type(nonprofits))
print(nonprofits[0])



            
            

    
            

    

            
    
    
# scrape_website_for_sub_pages("holy grail.csv")





