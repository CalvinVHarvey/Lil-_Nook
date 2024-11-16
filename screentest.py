from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from ScoreGrabber import ScoreGrabber
from PIL import Image
import time
import datetime
import simpleaudio as sa

#@Purpose: Interfacing with the raspberry pi while integrating the ScoreGrabber Class
#Setting up the LED matrix to display count down to next game if there is no game going on
#Otherwise display live stats of current game and play sound when a team scores a point
#Play sound as well when the game starts and when the game ends different effects dependent on whether it was UAF that scored
#or the other team
#
#@Date: 11/10/2024
#@Author: Calvin Harvey
#@Note: If planning on replicating change file paths to absolute paths instead of relative paths
#


#Hardware Configuration for LED matrix
options1 = RGBMatrixOptions()
options1.rows = 32
options1.cols = 64
options1.hardware_mapping = 'adafruit-hat'
matrix = RGBMatrix(options = options1)

#Audio Setup
wescore = sa.WaveObject.from_wave_file("audio/wescore.wav")
theyscore = sa.WaveObject.from_wave_file("audio/theirscore.wav")
wewin = sa.WaveObject.from_wave_file("audio/wewin.wav")
welose = sa.WaveObject.from_wave_file("audio/welose.wav")
gamestart = sa.WaveObject.from_wave_file("audio/gamestart.wav")

#Screen Settings
font = graphics.Font()
font.LoadFont("fonts/verdana-7pt.bdf")
font2 = graphics.Font()
font2.LoadFont("fonts/verdana-6pt.bdf")
text_color = graphics.Color(0, 255, 255)
offscreen_canvas = matrix.CreateFrameCanvas()

#Configuration for UAF sports grabbing library
cur_game = -1
while cur_game == -1: 
    try:
        grabber = ScoreGrabber()
        cur_game = 0
    except:
        print("Connection Failed")
        time.sleep(5)

print("Game information obtained")

#Screen runtime variables
pos1 = 0
pos2 = 0
length1 = 0
length2 = 0
score1 = 0
score2 = 0
game_started = False
our_team = "Alas. Fairbanks"

#Running Screen
delay = 0.05 #Time in seconds
request_delay = 5 #Set time for every reqeust in seconds
cur_time_till_request = 5 #Time until next request for game info
while True:
    offscreen_canvas.Clear()
    if cur_time_till_request >= request_delay: #Check to see if there is a different game that was just pulled if so determine if the team won if last game was in session
        tmp_game = grabber.grab_most_recent_game()
        if cur_game != 0 and cur_game['id'] != tmp_game['id'] and cur_game["json"]["gameState"] == 'I':
            team1 = cur_game['json']['teams'][0]
            team2 = cur_game['json']['teams'][1]
            if team1['score'] > team2['score']:
                if team1['nameShort'] == our_team:
                    wewin.play()
                else:
                    welose.play()
            else:
                if team1['nameShort'] == our_team:
                    wewin.play()
                else:
                    welose.play()
        cur_game = tmp_game
        cur_time_till_request = 0
    cur_time_till_request += delay
    if cur_game != 0 and cur_game['json']['gameState'] == 'I': #If first statement true then there is a live game else it is waiting for next game
        pos1 -= 1
        pos2 -= 1
        if game_started == False: #If game just started play audio
            gamestart.play()
            game_started = True
        if pos1 + length1 < 0:
            pos1 = offscreen_canvas.width
        if pos2 + length2 < 0:
            pos2 = offscreen_canvas.width
        team1 = cur_game['json']['teams'][0]['nameShort'].upper()
        team2 = cur_game['json']['teams'][1]['nameShort'].upper()
        if score1 < cur_game['json']['teams'][0]['score']:
            if team1 == our_team.upper():
                wescore.play()
            else:
                theyscore.play()
        if score2 < cur_game['json']['teams'][1]['score']:
            if team2 == our_team.upper():
                wescore.play()
            else:
                theyscore.play()
        score1 = cur_game['json']['teams'][0]['score']
        score2 = cur_game['json']['teams'][1]['score']
        graphics.DrawText(offscreen_canvas, font2, 0, 6, text_color, cur_game['json']['currentPeriod'] + " PERIOD")
        length1 = graphics.DrawText(offscreen_canvas, font2, pos1, 12, graphics.Color(180,180,180), team1)
        graphics.DrawText(offscreen_canvas, font2, 3, 18, graphics.Color(255,255,0), str(score1))
        length2 = graphics.DrawText(offscreen_canvas, font2, pos2, 26, graphics.Color(180,180,180), team2)
        graphics.DrawText(offscreen_canvas, font2, 3, 32, graphics.Color(255,255,0), str(score2))
    elif cur_game != 0:  #Display count down to next game if there is currently not a game going on
        game_id = cur_game["id"]
        game_info = grabber.game_ids[game_id]["date"]
        diff = (game_info-datetime.datetime.now())
        pos1 -= 1
        if pos1 + length1 < 0:
            pos1 = offscreen_canvas.width
        length2 = graphics.DrawText(offscreen_canvas, font, offscreen_canvas.width/2 - length2/2, 8, graphics.Color(0,255,255), "Next Game")
        graphics.DrawText(offscreen_canvas, font, offscreen_canvas.width/2 - length1/2, offscreen_canvas.height/2, graphics.Color(255,255,0), "Days: " + str(diff.days))
        length1 = graphics.DrawText(offscreen_canvas, font, offscreen_canvas.width/2 - length1/2, offscreen_canvas.height/2 + 8, graphics.Color(0,255,255), str(diff.seconds//3600) + ":" + str(diff.seconds%3600//60) + ":" + str(diff.seconds%60))
    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas) #End if statement
    time.sleep(delay)
