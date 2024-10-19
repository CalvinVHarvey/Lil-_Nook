import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from datetime import date

#@Class ScoreGrabber
#@Purpose: Grabs information on current UAF hockey game
#Library for Lil' Nook hardware integration  
#@Author: Calvin Harvey
#

class ScoreGrabber:
    
    #Constants
    LENGTH_OF_HOCKEY_GAME = 4
    TEAM_NAME = 'alas-fairbanks'
    
    #Sport settings the current sport determines which sport to pull statistics from the web from and sport map contains
    #useful information to the program to pull information such as what division UAF team is in and what the sport code is
    #To change the UAF sport the program pulls from change the SPORT variable to one of the keys in the sport map
    SPORT = 'mens-ice-hockey'
    SPORT_MAP = {
        "mens-ice-hockey": {"code":"MIH", "division":1},
        "mens-basketball": {"code":"MBB", "division":2},
        "womens-volleyball": {"code":"WVB", "division":2},
        "womens-basketball": {"code":"WBB", "division":2}
    }

    def __init__(self):
        self.json_schedule = {}
        self.hockey_dates = {}
        self.game_ids = {}

        self.grab_dates()
        self.grab_game_ids()
        
    #Collect UAF schedule
    #Parse website for json text then convert json text to json class
    #Gather team dates from the json file and load them into a list
    def grab_dates(self):
        schedule_html = requests.get("https://alaskananooks.com/sports/" + self.SPORT + "/schedule") 
        parser = BeautifulSoup(schedule_html.content, "html.parser")
        schedule_parsed = parser.find('script', type="application/ld+json") 
        schedule_text = schedule_parsed.get_text()
        self.json_schedule = json.loads(schedule_text)

        num = 0
        for i in self.json_schedule:  #Loading Dates
            dates = self.json_schedule[num]['startDate'].split('T')
            tmp = dates[0].split('-')
            tmp_time = dates[1].split(':')
            self.hockey_dates[num] = (datetime(int(tmp[0]), int(tmp[1]), int(tmp[2]), int(tmp_time[0]), int(tmp_time[1])))
            num += 1
            
    #Determing season year to make program more future orientated
    def determine_season(self, the_date = datetime.now()):
        today = the_date
        output_year = today.year
        if today.month < 4:
            return output_year-1
        elif today.month >= 9: 
            return output_year
        else:
            return output_year-1

    #Match schedule to NCAA Hockey game ID's 
    #Go through dates then locate alaska fairbanks college then grab game id
    #Load game id into datastructure
    def grab_game_ids(self):
        for i in self.hockey_dates:
            cur = self.hockey_dates[i]
            year = str(cur.year)
            month = str(cur.month)
            day = str(cur.day)
            if cur.day == 19 and cur.month == 12:
                print(cur)
            if cur.year <= date.today().year and date.today().month >= cur.month and date.today().day > cur.day:
                continue
            url = 'https://sdataprod.ncaa.com/?meta=GetContests_web&extensions={"persistedQuery":{"version":1,"sha256Hash":"f9d668706317cc187ecbe89591256e257b14af95432e36d4a68160dc78a7256c"}}&variables={"sportCode":"' + self.SPORT_MAP[self.SPORT]['code'] + '","division":' + str(self.SPORT_MAP[self.SPORT]['division']) + ',"seasonYear":2024,"contestDate":"' + month + '/'+day + '/' + year + '","week":null}'
            connection = requests.get(url)
            json_file = json.loads(connection.content)
            
            for elem in json_file['data']['contests']:
                cur_teams = elem['teams']
                if cur_teams[0]['seoname'] == self.TEAM_NAME:
                    self.game_ids[elem['contestId']] = {
                        "date": cur,
                        "ourScore": cur_teams[0]['score'],
                        "theirScore": cur_teams[1]['score']
                    }
                    break
                elif cur_teams[1]['seoname'] == self.TEAM_NAME:
                    self.game_ids[elem['contestId']] = {
                        "date": cur,
                        "ourScore": cur_teams[1]['score'],
                        "theirScore": cur_teams[0]['score']
                    }
                    break

    #Use game ID's to retrieve json files to interact with
    def grab_game_json(self, game_id):
        connection = requests.get('https://sdataprod.ncaa.com/?meta=GetGamecenterGameById_web&extensions={"persistedQuery":{"version":1,"sha256Hash":"c90d860c14087925c025a256d715edb1715183b438ec6ae6fee0ef8e5d1b7713"}}&variables={"id":"' + str(game_id) + '","week":null,"staticTestEnv":null}')
        return json.loads(connection.content)
    
    #Grab either live game and if no game is not live then grab the next most soon game
    def grab_most_recent_game(self):
        right_now = datetime.now()
        today = datetime.today()
        for i in self.game_ids:
            cur_date = self.game_ids[i]['date']
            game_json = self.grab_game_json(i)
            if cur_date == today and game_json['contests'][0]['gameState'] != 'F':
                return {"id":i, "json":game_json['data']['contests'][0]} # trimming down json noise
            elif cur_date > right_now:
                return {"id":i, "json": game_json['data']['contests'][0]}
        return 0
    