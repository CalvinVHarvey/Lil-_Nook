import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
from datetime import datetime

#Collect UAF schedule
#Parse website for json text then convert json text to json class
#Gather team dates from the json file and load them into a list

schedule_html = requests.get("https://alaskananooks.com/sports/mens-ice-hockey/schedule") 
parser = BeautifulSoup(schedule_html.content, "html.parser")
schedule_parsed = parser.find('script', type="application/ld+json") 
schedule_text = schedule_parsed.get_text()
json_schedule = json.loads(schedule_text)
date_tuple = {}

num = 0
for i in json_schedule:  #Loading Dates
    tmp = json_schedule[num]['startDate'].split('T')[0].split('-')
    date_tuple[num] = (datetime(int(tmp[0]), int(tmp[1]), int(tmp[2])))
    num += 1

#Match schedule to NCAA Hockey game ID's 
#Go through dates then locate alaska fairbanks college then grab game id
#Load game id into datastructure



#Use game ID's to retrieve json files to interact with



