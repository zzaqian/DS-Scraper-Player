import re 
import sys
from inputimeout import inputimeout, TimeoutOccurred
#import os
# importing vlc module
import vlc
  
# importing time module
import time
  
#os.add_dll_directory("C:\Program Files\VideoLAN\VLC")

class VLCplayer(): 
    def playSingle(bgmName, playTime): 
        # convert play time to secs 
        prime = "" 
        mins = ""
        secs = 0
        for char in playTime: 
            if char != ":": 
                prime += char 
            else: 
                mins = prime 
                prime = "" 

        if len(mins) != 0: 
            secs = 60 * int(mins) 

        secs += int(prime)
        barLen = 30

        # creating a vlc instance
        vlc_instance = vlc.Instance()
     
        # creating a media player
        player = vlc_instance.media_player_new()
     
        # creating a media
        media = vlc_instance.media_new("../DSdownloads/" + bgmName + ".mp3")
     
        # setting media to the player
        player.set_media(media)
     
        # play the video
        player.play()

        start = time.time() 
        pauseElapsed = 0
        displayPlayTime = True # initialize

        time.sleep(3) 

        while player.is_playing():
            try:
                command = inputimeout(prompt="", timeout=5)
            except TimeoutOccurred:
                command = 'timeout'
                if displayPlayTime: 
                    current = time.time() 
                    timeElapsed = min(round(current - pauseElapsed - start), secs) # cap the elapsed time
                    minElapsed = timeElapsed//60 
                    secElapsed = timeElapsed%60 

                    elapsedStr = ""
                    
                    elapsedStr += str(minElapsed) 
                    elapsedStr += ":"
                    if secElapsed < 10: 
                        elapsedStr += "0"

                    elapsedStr += str(secElapsed)

                    percentage = round(timeElapsed/secs*100) 
                    barNum = round(percentage/100*30) 

                    bar = "["
                    if barNum > 0: 
                        if barNum > 1:
                            for i in range(barNum-1):
                                bar += "*" 
                        bar += ">" 

                    for i in range(barLen - barNum): 
                        bar += "-" 

                    bar += "]  "
                    bar += elapsedStr + " / " + playTime 
                    print(bar)
                else: 
                    print(".")

            #command = input()  # input puts you on an infinite wait
            if command == "pause":
                player.set_pause(1) 
                pauseStart = time.time()
                print("paused")
                nextCommand = input()
                if nextCommand == "resume": 
                    pauseEnd = time.time()
                    pauseElapsed += pauseEnd - pauseStart
                    player.set_pause(0) 
                elif nextCommand == "quit": 
                    player.stop() 
                    sys.exit()
            elif command == "time": 
                displayPlayTime = not displayPlayTime 
            elif command == "quit": 
                player.stop() 
                sys.exit()

            time.sleep(1) 

        return None


    def playbyList(bgmName, playTime, currentIndex): 
        # convert play time to secs 
        prime = "" 
        mins = ""
        secs = 0
        for char in playTime: 
            if char != ":": 
                prime += char 
            else: 
                mins = prime 
                prime = "" 

        if len(mins) != 0: 
            secs = 60 * int(mins) 

        secs += int(prime)
        barLen = 30

        nextIndex = -1
        # creating a vlc instance
        vlc_instance = vlc.Instance()
     
        # creating a media player
        player = vlc_instance.media_player_new()
     
        # creating a media
        media = vlc_instance.media_new("../DSdownloads/" + bgmName + ".mp3")
     
        # setting media to the player
        player.set_media(media)
     
        # play the video
        player.play()

        start = time.time()
        pauseElapsed = 0
        displayPlayTime = True # initialize

        time.sleep(3)

        p = re.compile("goto [0-9]+")

        while player.is_playing():
            try:
                command = inputimeout(prompt="", timeout=5)
            except TimeoutOccurred:
                command = 'timeout'
                if displayPlayTime: 
                    current = time.time() 
                    timeElapsed = min(round(current - pauseElapsed - start), secs) # cap the elapsed time
                    minElapsed = timeElapsed//60 
                    secElapsed = timeElapsed%60 

                    elapsedStr = ""
                    
                    elapsedStr += str(minElapsed) 
                    elapsedStr += ":"
                    if secElapsed < 10: 
                        elapsedStr += "0"

                    elapsedStr += str(secElapsed)

                    percentage = round(timeElapsed/secs*100) 
                    barNum = round(percentage/100*30) 

                    bar = "["
                    if barNum > 0: 
                        if barNum > 1:
                            for i in range(barNum-1):
                                bar += "*" 
                        bar += ">" 

                    for i in range(barLen - barNum): 
                        bar += "-" 

                    bar += "]  "
                    bar += elapsedStr + " / " + playTime 
                    print(bar)
                else: 
                    print(".")

            #command = input()  # input puts you on an infinite wait
            if command == "pause":
                player.set_pause(1) 
                pauseStart = time.time()
                print("paused")
                nextCommand = input()
                if nextCommand == "resume": 
                    pauseEnd = time.time()
                    pauseElapsed += pauseEnd - pauseStart
                    player.set_pause(0)
                elif nextCommand == "quit": 
                    player.stop() 
                    sys.exit()
        
            elif command == "next": 
                player.stop()
                break 
            elif command == "previous": 
                nextIndex = currentIndex - 1 
                player.stop()
                break
            elif p.fullmatch(command): 
                command = command.replace("goto ", "") 
                command = command.strip() 
                nextIndex = int(command) 

                player.stop()
                break 
            elif command == "time": 
                displayPlayTime = not displayPlayTime 
            elif command == "quit": 
                player.stop() 
                sys.exit()

            time.sleep(1) 

        return nextIndex

'''
def playbyList(bgmList, playNum=0):
    if playNum == 0: # play all
        num = len(bgmList)
    else: 
        num = playNum

    # creating a media player object
    media_player = vlc.MediaListPlayer()
  
    # creating Instance class object
    player = vlc.Instance()
  
    # creating a new media list
    media_list = player.media_list_new()
  
    # creating a new media
    for bgmName, i in zip(bgmList, range(num)):
        media = player.media_new("scrapingEnv/DSdownloads/" + bgmName + ".mp3")
        print(media)
  
        # adding media to media list
        media_list.add_media(media)
  
    # setting media list to the media player
    media_player.set_media_list(media_list)
  
    # new media player instance
    new = player.media_player_new()
  
    # setting media player to it
    media_player.set_media_player(new)
  
    # start playing video
    media_player.play()
    #print("done")

    time.sleep(3)

    while media_player.is_playing():
        time.sleep(1)
        '''
