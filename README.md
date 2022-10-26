# DS-Scraper-Player
Scrapes the free BGM website [Dova-Syndrome](dova-s.jp) and automates the BGM downloading process. 
It also includes a mini player that plays donwloaded BGMs. 

## Dependencies: 
This repository is a virtual enviroment. Dependency modules should be installed when the virtual environment is activated (through Scripts/activate.bat). 
- requests
- Beautiful Soup
- urllib
- csv
- re
- time
- random
- sys
- inputimeout
- VLC: In order to use the VLC module in Python, the user must also install the VLC Player in computer.

## How to Use:
### start.bat
- Run `start.bat` to activate the virtual environment and call `Programs/DovaSyndrome.py`, which is the main program.
- If no errors occur, the command prompt will ask you to input an operation. Enter `guide` to view the list of possible operations.
- Here is the current list of possible operations, which are all function prototypes:
  - `downloadMostDownloads(startPage=1, endPage=1)`
  - `downloadLatest(startPage=1, endPage=1)`
  - `downloadbyTag(tag, sort="time", startPage=1, endPage=1)`
  - `downloadbyAuthor(author, sort="time", startPage=1, endPage=1)`
  - `getTags(tags, displayMethod=3)`
  - `getTagsandPlay(tags, playNum=0, isRandom=True, extraPauseTime=1, display=False)`
  - `getMostDownloadsandPlay(num=10, playNum=0, isRandom=False, extraPauseTime=1, display=True)`
  - `getAuthorandPlay(author, playNum=0, isRandom=True, extraPauseTime=1, display=True)`
  - `playSingle(bgm, doLoop=False)`
  - `playAll(isRandom=True, extraPauseTime=1, display=False)`
  - `playAllSince(start, isRandom=True, extraPauseTime=1, display=False)`
  - `playLatest(startLookingFrom=100, isRandom=False, extraPauseTime=1, display=True)`
  - `playFavorites(isRandom=True, extraPauseTime=1, display=True)`
  - `addtoFavorites(bgm)`

- Enter any of these function calls into the command prompt to execute. For example, if I type in `downloadLatest(1, 2)`, the program will go to [the home page](https://dova-s.jp/bgm/) and start downloading from the latest published BGM (first one on page 1) and stop after downloading all the BGMs on page 2. 
- To exit the program, simply close the command prompt window.

### Downloaded BGMs
- All BGMs donwloaded are stored in the `DSdownloads/` folder in .mp3 format.

### BGM Data and Tags
- In the `bgmData/`folder, there are 4 .csv files:
  - `mainData.csv`: Stores relevant data of every downloaded BGM.
  - `tags.csv`: Includes the look-up table of Dova-Syndrome's tags for BGMs. It not only contains every tag's ID and its original Japanese name but also contains its translation in English and Chinese. 
  - `mostDownloads.csv`: This file will be written every time `getMostDownloadsandPlay` is called. It stores the list of downloaded BGMs with top download numbers.
  - `favorites.csv`: This file will be appended every time `addtoFavorites` is called. It stores the user's favorites downloaded BGMs.
  
### Passing Tags into Functions
- The tag/tags arguments passed into the functions can be either a string of tag ID or its Chinese translation. Searching by Japanese or English is not supported because the author only needs to care about himself.

### VLC Player
- Every function with "play" in its name will play all specified downloaded BGM(s). It accesses the VLC Player installed in the computer with the VLC module. 
- There is a simple textual progress bar for the BGM playing, updating approximately every 5 seconds in the command prompt. While a BGM is playing, you can enter the following operations:
  - `pause`: Pauses the player.
  - `resume`: Resumes the player.
  - `quit`: Quits the player.
  - `next`: Switch to the next BGM on list.
  - `previous`: Switch to the previous BGM on list.
  - `goto [index]`: Go to the [index] BGM on list.
  - `time`: Toggle the progress bar display.


