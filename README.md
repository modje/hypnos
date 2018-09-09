# hypnos
Youtube music download automation with youtube-dl

## Install pre-requisites
* PIP
  * curl "https://bootstrap.pypa.io/get-pip.py" -o get-pip.py
  * python get-pip.py
  * python -m pip install --upgrade pip setuptools wheel
* Selenium
  * python -m pip install selenium
* TinyDB
  * python -m pip install tinydb
* PhantomJS
  * http://phantomjs.org/download.html
  * Extract binary in folder contained in PATH
* Youtube-dl
  * python -m pip install youtube_dl
* FFMPEG
  * https://www.ffmpeg.org/download.html
  * Add the bin directory to the PATH

## Usage
hypnos.py [-h] [-c CHAN] {list,add,remove,update,queue}  

positional arguments:
* Command {list,add,remove,update,queue,download,flush} Command to execute
	* list : Output the channel list
	* add -c CHAN : Add the channel CHAN to the database
	* remove -c CHAN : Remove the channel CHAN from the database
	* update [-c CHAN] : Refresh video list for each channel since last update (or for one channel if specified with -c)
  * queue : Output the download queue
  * download : Processes the queue by downloading each element, converting it and deleting it from the queue
  * flush : Remove the videos in 'error' status from the queue

optional arguments:
* -h, --help            show this help message and exit
* -c CHAN, --chan CHAN  Channel identifier (usable on 'add', 'remove' and 'update' commands)
