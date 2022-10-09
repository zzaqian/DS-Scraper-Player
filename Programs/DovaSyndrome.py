from DSscraping import * 
from VLCplayer import *
import time
import random
import sys



#data = downloadBGM(17368)
#data = [12345, "abc", ["tag1", "tag2"], 0]
#storeCSV(downloadBGM(17350))
#storeTags()
#print(getSearchPageUrl("downloads", "m01"))
#print(isDownloaded(17368))
#DovaSyndrome().parseSearchPage("https://dova-s.jp/_contents/settingSound/run.html?tags=m01", startPage=4, endPage=5)
'''
tags = ["平静"]
searchResults = DovaSyndrome().searchLocalbyTags(tags) 
for bgmNum in list(searchResults.keys()): 
    print(searchResults[bgmNum][0])
    #print(searchResults[bgmNum][1]) 
    '''
    
'''
searchResults = DovaSyndrome().searchLocalbyDownloads()
print(searchResults)
'''
'''
new = DovaSyndrome()
pageUrl = new.getSearchPageUrl("downloads", "可爱") 
new.parseSearchPage(pageUrl, startPage=1, endPage=5)
'''

# file:\\\C:\Users\31801\Web Scraping\scrapingEnv

'''
tags = ["平静"]
searchResults = DovaSyndrome().searchLocalbyTags(tags) 
playList = list()
for bgmNum in list(searchResults.keys()): 
    bgmName = searchResults[bgmNum][0]
    print("Playing " + bgmName) 
    playList.append(bgmName)

playbyList(playList, 1)
'''

def downloadMostDownloads(startPage=1, endPage=1): 
    new = DovaSyndrome()
    pageUrl = new.getSearchPageUrl("downloads") 
    new.parseSearchPage(pageUrl, startPage=startPage, endPage=endPage)


def downloadLatest(startPage=1, endPage=1):
    new = DovaSyndrome()
    pageUrl = new.getSearchPageUrl() 
    new.parseSearchPage(pageUrl, startPage, endPage)


def downloadbyTag(tag, sort="time", startPage=1, endPage=1): 
    new = DovaSyndrome()
    pageUrl = new.getSearchPageUrl(sort, tag) 
    new.parseSearchPage(pageUrl, startPage, endPage)


def downloadbyAuthor(author, sort="time", startPage=1, endPage=1): 
    new = DovaSyndrome()
    pageUrl = new.getAuthorBGMListUrl(author, sort) 
    new.parseSearchPage(pageUrl, startPage, endPage)


def getTags(tags, displayMethod=3): 
    new = DovaSyndrome()
    searchResults = new.searchLocalbyTags(tags) 

    for bgmNum in searchResults.keys(): 
        if displayMethod >= 0:
            if displayMethod > 0:

                bgmName = searchResults[bgmNum][0]

                if displayMethod > 1: 

                    if displayMethod > 2:

                        tagNameString = ""
                        tagIdList = searchResults[bgmNum][1].split(" ") 
                        for tagId in tagIdList: 
                            tagNameString = tagNameString + " " + new.tagDictReverse[tagId]

                        tagNameString = tagNameString.strip() 

                        print(bgmNum + " " + bgmName) 
                        print("--->Tags: " + tagNameString)

                    else: 
                        print(bgmNum + " " + bgmName)

                else: 
                    print(bgmName)
            else: 
                print(bgmNum) # method = 0


def listPlayer(bgmList, DS, playNum=0, isRandom=True, extraPauseTime=1, display=False):
    if isRandom: 
        random.shuffle(bgmList)

    if playNum > 0:
        bgmList = bgmList[:playNum] 

    if display: 
        print("List of all matches: ")
        for i in range(len(bgmList)): 
            if i < 10:
                index = "0" + str(i)
            else: 
                index = str(i)
            print(index + ") " + list(bgmList[i].values())[0][0])

        print("-----------------------------------------")

    #for i in range(len(bgmList)): 
    i = 0

    while i < len(bgmList) and i >= 0: # using a custom index allows going to previous bgm
        nextIndex = -1 # reinitialize the nextIndex 
        values = list(bgmList[i].values())[0]

        bgmName = values[0]
        if i+1 < len(bgmList):
            nextName = list(bgmList[i+1].values())[0][0]
        else: 
            nextName = "You have reached the end of the play list!"

        #tagNameList = list()
        tagNameString = ""
        tagIdList = values[1].split(" ") 
        for tagId in tagIdList: 
            tagNameString = tagNameString + " " + DS.tagDictReverse[tagId]
            #tagNameList.append(new.tagDictReverse[tagId])

        tagNameString = tagNameString.strip()

        playTime = values[2]

        if i < 10:
            index = "0" + str(i)
        else: 
            index = str(i)

        print("Current playing: " + index + ") " + bgmName) 
        print("--->Tags: " + tagNameString)
        print("--->Next to: " + nextName)
        nextIndex = VLCplayer.playbyList(bgmName, playTime, i) 
        print("-----------------------------------------")

        if nextIndex >= 0:
            i = nextIndex 
        else: 
            i += 1

        time.sleep(extraPauseTime) # pause for seconds between bgms 

    return None


def getTagsandPlay(tags, playNum=0, isRandom=True, extraPauseTime=1, display=False):
    #tags = ["温柔"]
    new = DovaSyndrome()
    searchResults = new.searchLocalbyTags(tags) 

    if len(searchResults) == 0:
        print("No matches.")

    bgmList = list() # list of dictionaries
    #bgmList = list(searchResults.keys())
    for key in searchResults.keys(): 
        bgmList.append({key: searchResults[key][:3]}) # the first three var in the value list: bgmNum, bgmName, playTime

    listPlayer(bgmList, new, playNum, isRandom, extraPauseTime, display)

    return None 


def getMostDownloadsandPlay(num=10, playNum=0, isRandom=False, extraPauseTime=1, display=True): 
    new = DovaSyndrome() 
    bgmList = new.searchLocalbyDownloads(num) 

    for item in bgmList: 
        key = list(item.keys())[0] 
        item[key] = item[key][:3]

    listPlayer(bgmList, new, playNum, isRandom, extraPauseTime, display) 

    return None


def getAuthorandPlay(author, playNum=0, isRandom=True, extraPauseTime=1, display=True):
    new = DovaSyndrome() 
    bgmList = new.searchLocalbyAuthor(author) 

    for item in bgmList: 
        key = list(item.keys())[0] 
        item[key] = item[key][:3]

    listPlayer(bgmList, new, playNum, isRandom, extraPauseTime, display) 

    return None


def playSingle(bgm, doLoop=False): # supports bgmNum, bgmName, and authors
    new = DovaSyndrome() 
    bgmDict = new.searchSingle(bgm) 

    if bgmDict != None: 
        key = list(bgmDict.keys())[0] 
    else: 
        print("No matches.")
        return None

    tagNameString = ""
    tagIdList = bgmDict[key][1].split(" ") 
    for tagId in tagIdList: 
        tagNameString = tagNameString + " " + new.tagDictReverse[tagId]
        #tagNameList.append(new.tagDictReverse[tagId])

        tagNameString = tagNameString.strip()


    print("Playing " + key + ": " + bgmDict[key][0] + " -by " + bgmDict[key][3]) 
    print("->Tags: " + tagNameString) 
    
    VLCplayer.playSingle(bgmDict[key][0], bgmDict[key][2]) # pass bgmName and playTime

    while doLoop:
        VLCplayer.playSingle(bgmDict[key][0], bgmDict[key][2])

    return None

    
def playAll(isRandom=True, extraPauseTime=1, display=False): 
    new = DovaSyndrome() 
    bgmList = new.searchAllSince() 

    listPlayer(bgmList, new, 0, isRandom, extraPauseTime, display)

    return None 


def playAllSince(start, isRandom=True, extraPauseTime=1, display=False): 
    new = DovaSyndrome() 
    bgmList = new.searchAllSince(start) 

    listPlayer(bgmList, new, 0, isRandom, extraPauseTime, display)

    return None 


def playLatest(startLookingFrom=100, isRandom=False, extraPauseTime=1, display=True):
    new = DovaSyndrome() 
    bgmList = new.searchLatest(startLookingFrom) 

    listPlayer(bgmList, new, 0, isRandom, extraPauseTime, display)

    return None 


def playFavorites(isRandom=True, extraPauseTime=1, display=True): 
    new = DovaSyndrome() 
    bgmList = new.searchFavorites() 

    listPlayer(bgmList, new, 0, isRandom, extraPauseTime, display)

    return None 


def addtoFavorites(bgm): 
    DovaSyndrome().addtoFavorites(bgm) 

    return None


#downloadbyTag("苦涩", "downloads", endPage=10)
#getTagsandPlay(["孤独"], extraPauseTime=1, display=True) 
#getMostDownloadsandPlay(20)
#getTags(["孤独"])
#DovaSyndrome().searchLocalbyDownloads() 
#downloadLatest(1, 2)
#downloadMostDownloads(1, 10) 
#playSingle("コールドフィッシュ")
#playAll()
#playLatest() 
#addtoFavorites("WILD BOYS")
#playFavorites()


'''
All prototypes:
downloadMostDownloads(startPage=1, endPage=1)
downloadLatest(startPage=1, endPage=1)
downloadbyTag(tag, sort="time", startPage=1, endPage=1)
downloadbyAuthor(author, sort="time", startPage=1, endPage=1)
getTags(tags, displayMethod=3)
getTagsandPlay(tags, playNum=0, isRandom=True, extraPauseTime=1, display=False)
getMostDownloadsandPlay(num=10, playNum=0, isRandom=False, extraPauseTime=1, display=True)
getAuthorandPlay(author, playNum=0, isRandom=True, extraPauseTime=1, display=True)
playSingle(bgm, doLoop=False)
playAll(isRandom=True, extraPauseTime=1, display=False)
playAllSince(start, isRandom=True, extraPauseTime=1, display=False)
playLatest(startLookingFrom=100, isRandom=False, extraPauseTime=1, display=True)
playFavorites(isRandom=True, extraPauseTime=1, display=True)
addtoFavorites(bgm)
'''

def guide():
            print("-------------------------------")
            print("All prototypes:")
            print("downloadMostDownloads(startPage=1, endPage=1)")
            print("downloadLatest(startPage=1, endPage=1)")
            print("downloadbyTag(tag, sort=\"time\", startPage=1, endPage=1)") 
            print("downloadbyAuthor(author, sort=\"time\", startPage=1, endPage=1)")
            print("getTags(tags, displayMethod=3)") 
            print("getTagsandPlay(tags, playNum=0, isRandom=True, extraPauseTime=1, display=False)") 
            print("getMostDownloadsandPlay(num=10, playNum=0, isRandom=False, extraPauseTime=1, display=True)")
            print("getAuthorandPlay(author, playNum=0, isRandom=True, extraPauseTime=1, display=True)")
            print("playSingle(bgm, doLoop=False)")
            print("playAll(isRandom=True, extraPauseTime=1, display=False)")
            print("playAllSince(start, isRandom=True, extraPauseTime=1, display=False)")
            print("playLatest(startLookingFrom=100, isRandom=False, extraPauseTime=1, display=True)")
            print("playFavorites(isRandom=True, extraPauseTime=1, display=True)")
            print("addtoFavorites(bgm)") 
            print("-------------------------------")


def main():
    #print(sys.path)

    functionSet = {"downloadMostDownloads", "downloadLatest", "downloadbyTag", "downloadbyAuthor", "getTags", "getTagsandPlay", 
                   "getMostDownloadsandPlay", "getAuthorandPlay", "playSingle", "playAll", "playAllSince", "playLatest", 
                   "playFavorites", "addtoFavorites"}

    while True:
        command = input("Please choose an operation.\nEnter guide to see all functions: ") 

        if command == "guide": 
            guide() 
        elif command == "exit": 
            print("To exit, just close the window.\n")

        if "(" in command: 
            pIndex = command.index("(") 
            fName = command[:pIndex] 

            if fName in functionSet:
                exec(command)


if __name__ == "__main__": 
    main()
