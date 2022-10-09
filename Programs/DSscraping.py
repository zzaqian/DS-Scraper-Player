import requests
from bs4 import BeautifulSoup 
from urllib.error import HTTPError
import csv
import re 
import time 
import random


class DovaSyndrome(): 
    def __init__(self): 
        self.downloadedSet = set()

        self.tagDict = dict() # key: Chinese; value: tagId

        with open("../bgmData/tags.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break
        
            #keys = ["tagId", "name", "English", "Chinese"]
            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader: 
                #print(row)
                self.tagDict[row["Chinese"]] = row["tagId"]
            f.close() 

        self.tagDictReverse = dict() # key tagId; value: Chinese
        for key in self.tagDict.keys(): 
            self.tagDictReverse[self.tagDict[key]] = key


    def downloadBGM(self, bgmNum):
        domain = "https://dova-s.jp/"

        playUrl = domain+"bgm/play"+str(bgmNum)+".html"

        session = requests.session()

        try:
            playPage = session.get(playUrl)
        except HTTPError:
            print("Player page not found.")
            return None

        pl = BeautifulSoup(playPage.text, "html.parser")


        playerBlock = pl.find("div", {"id": "playerBlock"})
        separator = "¶"
        playerBlockText = playerBlock.getText(separator)
        #print(playerBlockText)

        try:
            nameAuthor = playerBlock.find("h2", {"class": "textL"})
            writtenbyAuthor = nameAuthor.find("span", {"class": "textMS"}) 
            authorLink = writtenbyAuthor.find("a")["href"] 
            authorLink = domain+authorLink # turn relative link to absolute link

            writtenbyAuthor = writtenbyAuthor.text
            nameAuthor = nameAuthor.text 

            bgmName = nameAuthor.replace(writtenbyAuthor, "") 
            bgmName = bgmName.strip() 
            bgmName = self.replaceIllegalFilename(bgmName) 

            author = writtenbyAuthor.replace("written by", "") 
            author = author.strip() 
        except AttributeError:
            print("BGM's name or author or author link not found.")
            bgmName = None 
            author = None

        try:
            tagStr = ""
            tagLinkLength = 0
            tags = playerBlock.find("dl", {"class": "tags"}).find("dd").findAll("a") 
            for tag in tags: 
                if "href" in tag.attrs: 
                    if not tagLinkLength:
                        tagLinkLength = len(tag.attrs["href"])
                    tagId = tag.attrs["href"][tagLinkLength-3:]
                    tagStr = tagStr+tagId+" "

            tagStr = tagStr.strip()
        except AttributeError:
            print("tag or tag link not found.") 
            tagStr = ""

        try:
            playTime = ""
            playTimeIndex = playerBlockText.index("再生時間：")
            playTimeText = playerBlockText[playTimeIndex  + len("再生時間："): playTimeIndex + 20] 
            separatorIndex = playTimeText.index(separator)
            playTime = playTimeText[: separatorIndex]
            playTime = playTime.strip()
            #print(playTime)
        except AttributeError:
            print("Play time not found.") 
            playTime = ""

        try:
            isLoop = -1
            loopText = playerBlock.find("span", {"class": "icon"}).text
            # find("li", text="ループ：").
            if "disable" in loopText: 
                isLoop = 0 
            elif "able" in loopText: 
                isLoop = 1
        except AttributeError:
            print("Loop attribute not found.") 
            isLoop = -1

        try:
            downloadNum = 0
            downloadsNumIndex = playerBlockText.index("DL：")
            downloadsText = playerBlockText[downloadsNumIndex + len("DL："): downloadsNumIndex + 20]
            separatorIndex = downloadsText.index(separator) 
            downloadsText = downloadsText[: separatorIndex]
            downloadsText = downloadsText.strip()
            downloadNum = int(downloadsText)
            #print(downloadNum)
        except AttributeError:
            print("Download number not found.") 
            downloadNum = 0
        except ValueError: 
            print("Download number invalid.")
            downloadNum = 0

        try:
            releaseDate = ""
            releaseDateText = playerBlock.find("p", {"id": "releaseDate"}).text
            releaseDate = releaseDateText.replace("公開日：", "")
            releaseDate = releaseDate.strip()
            #print(releaseDate)
        except AttributeError:
            print("Release/publication date not found.") 
            releaseDate = "" 

        #print(bgmName)

        pl = pl.find("div", {"id": "toDownload"}) 

        paramsPl = dict()

        try:
            for hidden in pl.findAll("input", {"type": "hidden"}):
                if "name" in hidden.attrs:
                    if "[]" not in hidden.attrs["name"]:
                        paramsPl[hidden.attrs["name"]] = hidden.attrs["value"] 
                    else:
                        if hidden.attrs["name"] not in paramsPl:
                            paramsPl[hidden.attrs["name"]] = [hidden.attrs["value"]]
                        paramsPl[hidden.attrs["name"]].append(hidden.attrs["value"]) 
        except AttributeError:
            print("toDownload form or inputs (hidden) not found.") 
            return None


        downloadUrl = domain+"/bgm/download"+str(bgmNum)+".html"

        try: 
            downloadPage = session.post(downloadUrl, data=paramsPl) 
        except HTTPError: 
            print("Downloader page not found.") 
            return None


        dl = BeautifulSoup(downloadPage.text, "html.parser").find("div", {"id": "downloadArea"})

        paramsDl = dict()

        try: 
            for select in dl.findAll("select"): 
                option = select.find("option", {"selected": "selected"})
                if "name" in select.attrs and option: 
                    paramsDl[select.attrs["name"]] = option.attrs["value"]

            for hidden in dl.findAll("input", {"type": "hidden"}):
                if "name" in hidden.attrs:
                    paramsDl[hidden.attrs["name"]] = hidden.attrs["value"]
        except AttributeError: 
            print("downloadArea form or inputs (select or hidden) not found.") 
            return None


        fileUrl = domain+"/bgm/inc/file.html" 

        try: 
            filePage = session.post(fileUrl, data=paramsDl, headers={"referer": downloadUrl}) 
        except HTTPError: 
            print("File not found.") 
            return None
                         

        #print(filePage.status_code) 
        #print(filePage.headers)
        #print(filePage.text)
        #print(filePage.content)

        fileName = "../DSdownloads/"+bgmName+".mp3"
        with open(fileName, "wb") as f:
            f.write(filePage.content)
            f.close()

        #downloadTime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        t = time.localtime()
        downloadTime = time.strftime("%m/%d/%Y %H:%M:%S", t)
        #print(downloadTime)

        dataList = [bgmNum, bgmName, playUrl, author, authorLink, tagStr, playTime, isLoop, downloadNum, releaseDate, downloadTime] 
        return dataList


    def getDownloaded(self):
        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f:
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break
            #print(keys)
            #keys = ["bgmNum", "bgmName", "playUrl", "author", "authorLink", "tagStr", "playTime", "isLoop", "downloadNum", "releaseDate", "downloadTime"]
            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader: 
                self.downloadedSet.add(int(row["bgmNum"]))

            f.close()

        return None


    def getSearchPageUrl(self, sortMethod="time", tag=None):
        url = "https://dova-s.jp/_contents/settingSound/run.html" 

        if sortMethod == "time":
            url = url + "?sort=" + "1" 
        elif sortMethod == "downloads": 
            url = url + "?sort=" + "2" 
        else: 
            url = url + "?sort=" + "1" 

        if tag:
            if tag in self.tagDict.values():
                url = url + "&tags=" + tag 
            elif tag in self.tagDict.keys(): 
                url = url + "&tags=" + self.tagDict[tag] 
            else: 
                return None

        return url


    def getAuthorBGMListUrl(self, author, sortMethod="time"): 
        profileLink = None

        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f:
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                break
            #print(keys)
            #keys = ["bgmNum", "bgmName", "playUrl", "author", "authorLink", "tagStr", "playTime", "isLoop", "downloadNum", "releaseDate", "downloadTime"]
            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader: 
                if row["author"] == author: 
                    profileLink = row["authorLink"]
                    break

            f.close()

        profilePage = requests.get(profileLink) 
        bs = BeautifulSoup(profilePage.text, "html.parser") 

        bgmListUrl = "https://dova-s.jp/_contents" 
        bgmListUrl +=  bs.find("div", {"id": "toList"}).find("a").attrs["href"].replace("..", "") 

        if bgmListUrl == "https://dova-s.jp/_contents": 
            return None 
        else: 
            return bgmListUrl


    def parseSearchPage(self, url, startPage=1, endPage=1): 
        if startPage > endPage:
            print("Please enter valid page numbers.") 
            return None

        self.getDownloaded()
        
        session = requests.session() 

        searchPage = session.get(url) 
        bs = BeautifulSoup(searchPage.text, "html.parser") 

        if startPage == 1:
            pass
        elif startPage > 1:
            for i in range(startPage-1): 
                nextPageLink = self.gotoNextPage(bs, i+1)
                if not nextPageLink: 
                    print("Reached the end of the web pages.")
                    return None

                searchPage = session.get(nextPageLink) 
                bs = BeautifulSoup(searchPage.text, "html.parser") 
        else: 
            print("invalid starting page number.") 
            return None
        #print(bs.text)
    
        for i in range(endPage-startPage+1):
            if i > 0:
                nextPageLink = self.gotoNextPage(bs, startPage+i-1)  # current page is startPage + i - 1
                if not nextPageLink: 
                    print("Reached the end of the web pages.")
                    return None

                searchPage = session.get(nextPageLink) 
                bs = BeautifulSoup(searchPage.text, "html.parser") 

            print("--> Parsing page " + str(startPage+i) + ".")
            print("---------------------------------------------")

            previous = "" # to get rid of duplicate links 
            for item in bs.find("div", {"id": "itemList"}).findAll("a", {"href": re.compile("(/bgm/play[0-9]+\.html)$")}): 
                #print(item["href"])
                link = item["href"] 
                if link != previous: 
                    previous = link 
                    index1 = link.index("play") + len("play")
                    index2 = link.index(".html") 
                    bgmNum = int(link[index1: index2]) 
                
                    if bgmNum not in self.downloadedSet: 
                        print("Downloading bgm " + str(bgmNum) + ".")
                        dataList = self.downloadBGM(bgmNum)
                        self.storeCSV(dataList)
                        print("Bgm stored to: " + dataList[1] + ".mp3")
                        print("---------------------------------------------")
                        time.sleep(2) # control the parse speed

        print("All done!")
                    
        return None


    def gotoNextPage(self, bs, currentPageNum): 
        domain = "https://dova-s.jp"
        nextPageLink = ""

        print("Going to page " + str(currentPageNum+1) + ".")

        pages = bs.find("div", {"id": "pageNavigation"}).find("div", {"class": "pager"}).findAll("a")
        if len(pages) == 0:
            print("No previous page nor next page link found.") 
            return None

        for page in pages: 
            if "href" in page.attrs: 
                link = page.attrs["href"] 
                link = link.strip()
                index1 = link.index("page=") + len("page=") 
                pageNum = int(link[index1:]) 
                if pageNum == (currentPageNum)+1:  # make sure it links to the next page
                    nextPageLink = domain+link

        if len(nextPageLink) == 0:
            print("Reached the end of web pages.")
            return None

        return nextPageLink

    '''
    Main CSV File:
    # int bgmNum str bgmName; str playUrl; str author; str authorLink; str of ints concatenated with space (create dictionary) [tags]; str playTime; bool isLoop; int downloadNum; str releaseDate; str downloadTime;

    *After storing data in the main file, can read it and catalogue:
    Tag CSV Files:
    # int bgmNum str bgmName; int downloads
    '''

    def replaceIllegalFilename(self, bgmName): 
        illegalChars = ["<", ">", ":", "/", "\"", "|", "?", "*"]
        newName = bgmName
        for char in illegalChars: 
            while char in newName: 
                newName = newName.replace(char, "_") 

        return newName


    def storeCSV(self, dataList):
        with open("../bgmData/mainData.csv", "a", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="¶", lineterminator="\n")
            writer.writerow(dataList)
            f.close() 

        return None


    def storeTags(self):
        session = requests.session() 

        settingPage = session.get("https://dova-s.jp/_contents/settingSound/")
        setting = BeautifulSoup(settingPage.text, "html.parser")

        tags = setting.find("form", {"id": "setting"}).findAll("input", {"name": "tags[]"})

        with open("../bgmData/tags.csv", "a", encoding="utf-8") as f: 
            writer = csv.writer(f, delimiter="¶", lineterminator="\n")
            for tag in tags: 
                value = tag.attrs["value"] 
                name = tag.next_sibling.text 
                writer.writerow([value, name, "", ""]) 
                print(name)

            f.close() 

        return None
    

    def searchSingle(self, bgm): 
        singleDict = dict()
        authorDict = dict() # if bgm is author name
        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader: 
                if bgm == row["bgmNum"]: 
                    singleDict[bgm] = [row["bgmName"], row["tags"], row["playTime"], row["author"]] 
                    break 
                elif bgm == row["bgmName"]: 
                    singleDict[row["bgmNum"]] = [bgm, row["tags"], row["playTime"], row["author"]] 
                    break 
                elif bgm == row["author"]: 
                    authorDict[row["bgmNum"]] = [row["bgmName"], row["tags"], row["playTime"], bgm] 

            if len(authorDict) > 0: 
                randomIndex = random.randint(0, len(authorDict)-1) 
                randomKey = list(authorDict.keys())[randomIndex] 

                singleDict[randomKey] = [authorDict[randomKey][0], authorDict[randomKey][1], authorDict[randomKey][2], authorDict[randomKey][3]]

            f.close()

        if len(singleDict) == 0: 
            return None 
        else: 
            return singleDict

            
    def searchLocalbyTags(self, tags): # a list of tags is passed to this function
        resultDict = dict() 
        tagIdList = list()

        for tag in tags: 
            if tag in self.tagDict.values(): 
                tagIdList.append(tag) 
            elif tag in self.tagDict.keys(): 
                tagIdList.append(self.tagDict[tag]) 

        if len(tagIdList) == 0:
            print("Please enter valid tags.") 
            return resultDict

        #print(tagIdList)

        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader:
                isResult = True 
                for tagId in tagIdList: 
                    if tagId not in row["tags"]: 
                        isResult = False
                        break 

                if isResult: 
                    resultDict[row["bgmNum"]] = [row["bgmName"], row["tags"], row["playTime"]] 

            f.close()
        
        if len(resultDict.keys()) == 0:
            print("No matches.")

        return resultDict 


    def searchLocalbyDownloads(self, num=10): 
        downloadsList = list()
        for i in range(num+1):  # the last spot for sorting
            downloadsList.append(0)

        bgmNumList = list() 
        for i in range(num+1): 
            bgmNumList.append("") 

        bgmDict = dict() # initialize

        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader:
                downloadNum = int(row["downloadNum"]) 
                downloadsList[0] = downloadNum 
                bgmNumList[0] = row["bgmNum"]
                for i in range(num+1-1): 
                    if downloadsList[i] > downloadsList[i+1]: 
                        if i == 0: 
                            bgmDict[row["bgmNum"]] = [row["bgmName"], row["tags"], row["playTime"]]

                        temp1 = downloadsList[i] 
                        downloadsList[i] = downloadsList[i+1] 
                        downloadsList[i+1] = temp1 

                        temp2 = bgmNumList[i] 
                        bgmNumList[i] = bgmNumList[i+1] 
                        bgmNumList[i+1] = temp2 

            f.close()

        # map bgmNum to bgmName and reverse the order of the list and store
        finalList = list() 
        for i in range(num): 
            bgmNum = bgmNumList[-i-1]
            if bgmNum != "": 
                bgmName = bgmDict[bgmNum][0]
                tags = bgmDict[bgmNum][1]
                playTime = bgmDict[bgmNum][2]
                finalList.append({bgmNum: [bgmName, tags, playTime, downloadsList[-i-1]]}) # value has a third term downloadNum

        with open("../bgmData/mostDownloads.csv", "w", encoding="utf-8") as g:
            writer = csv.DictWriter(g, fieldnames=["bgmNum", "bgmName", "downloadNum"], delimiter="¶", lineterminator="\n") 
            writer.writeheader() 

            for item in finalList: 
                writer.writerow({"bgmNum": list(item.keys())[0], "bgmName": list(item.values())[0][0], "downloadNum": list(item.values())[0][3]})

            g.close()

        return finalList 

    def searchAllSince(self, start=2): 
        bgmList = list() # initialize

        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for lineCount, row in enumerate(reader):  # DictReader starts from line 2
                if lineCount+2 >= start: 
                    bgmList.append({row["bgmNum"] : [row["bgmName"], row["tags"], row["playTime"]]})

            f.close()

        return bgmList


    def searchFavorites(self): 
        bgmList = list() # initialize

        with open("../bgmData/favorites.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader: 
                bgmList.append({row["bgmNum"] : [row["bgmName"], row["tags"], row["playTime"]]})

            f.close()

        return bgmList


    def searchLatest(self, startLookingFrom=1): 
        bgmList = list() # initialize

        t = time.localtime()
        today = time.strftime("%m/%d/%Y", t) 

        with open(r"../bgmData/mainData.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for lineCount, row in enumerate(reader):  # DictReader starts from line 2
                if lineCount+2 >= startLookingFrom: 
                    downloadDate = row["downloadTime"][:len(today)] 
                    if downloadDate == today: 
                        bgmList.append({row["bgmNum"] : [row["bgmName"], row["tags"], row["playTime"]]})

            f.close()

        return bgmList


    def searchLocalbyAuthor(self, author):
        bgmList = list() # initialize

        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader:  # DictReader starts from line 2
                if row["author"] == author: 
                    bgmList.append({row["bgmNum"] : [row["bgmName"], row["tags"], row["playTime"]]})

            f.close()

        return bgmList


    def addtoFavorites(self, bgm):
        bgmDict = dict()
        keys = list()
        with open("../bgmData/mainData.csv", "r", encoding="utf-8") as f: 
            for line in f:
                line = line.replace("\ufeff", "")
                line = line.strip()
                keys = line.split("¶") 
                #print(keys)
                break

            reader = csv.DictReader(f, delimiter="¶", fieldnames=keys) 
            for row in reader: 
                if bgm == row["bgmNum"] or bgm == row["bgmName"]: 
                    bgmDict = row.copy()

            f.close() 


        with open("../bgmData/favorites.csv", "r+", encoding="utf-8") as g: 
            reader = csv.DictReader(g, fieldnames=keys, delimiter="¶")
            writer = csv.DictWriter(g, fieldnames=keys, delimiter="¶", lineterminator="\n")

            for row in reader: 
                if bgm == row["bgmNum"] or bgm == row["bgmName"]: # Avoid writing repeatedly
                    g.close()
                    return None
                
            writer.writerow(bgmDict)
            g.close() 


        return None
