import sys, os
import warnings
import argparse
import time
import datetime
import youtube_dl
from selenium import webdriver
from tinydb import TinyDB, Query

# TODO : remove this, fix warnings about PhantomJS being deprecated instead
warnings.filterwarnings("ignore")

# Download dir
downloaddir = os.path.dirname(sys.argv[0]) + "/download"

# Reopen stdout file descriptor with write mode
# and 1 as the buffer size to avoid buffering
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)

# Logger for youtube-dl
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

# Progress hook for youtube-dl
def my_hook(d):
	if d['status'] == 'finished':
		message = "%s/%s\t Converting \t[%s] %s" % (count,nbvid,video['id'],video['desc'])
		sys.stdout.write("\b" * (len(message)+16))
		sys.stdout.write(message)
		sys.stdout.flush()

# Youtube-dl options
ydl_opts = {
    'nocheckcertificate' : True,
	'nooverwrites' : True,
	'ignoreerrors' : True,
	'outtmpl' : downloaddir + '/%(title)s.%(ext)s',
	'restrictfilenames' : True,
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
        }],
	'logger': MyLogger(),
	'progress_hooks': [my_hook]
    }

# Arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("command", help="Command to execute", choices=["list","add","remove","update","queue","download","flush"])
parser.add_argument("-c", "--chan", help="Channel identifier (usable on 'add', 'remove' and 'update' commands)")
args = parser.parse_args()
if args.command not in ['list','update','queue','download','flush'] and not args.chan:
	parser.error("Channel value is mantatory with command '%s' (use -c or --chan)" % args.command)

# Database
dbFile = os.path.join(os.path.dirname(sys.argv[0]), "db.json")
db = TinyDB(dbFile)

# Parse channel content and update database
def updateChannel(channel):
	# Get chan info from the db
	chan = Query()
	chan = db.search((chan.type == 'channel') & (chan.id == channel))
	if chan:
		chan = chan[0]
		# Get page content
		driver.get('https://www.youtube.com/user/%s/videos' % channel)
		# Get videos links and titles
		links = driver.find_elements_by_xpath('//body//h3[contains(@class,"yt-lockup-title")]/a')
		newVideos = []
		mostRecent = None
		for link in links:
			vtitle = link.get_attribute("title")
			vhref = link.get_attribute("href")
			vhrefid = vhref.split('=')[1]
			# Keep the first video as the most recent one
			if not mostRecent:
				mostRecent=vhrefid
			# If we reached the last known video we exit the loop
			if vhrefid == chan['lastvid']:
				break
			else:
				newVideos.append([vhrefid,vtitle])
		# Proceed each new video
		if len(newVideos) > 0:
			print("[%s]\t%s new videos found :" % (channel,len(newVideos)))
			for video in newVideos:
				viddesc = (video[1].encode('ascii', 'ignore')).decode("utf-8")
				print("\t[%s]\t%s" % (video[0],viddesc))
				# Add the video to the download queue
				db.insert({'type': 'video', 'id': video[0], 'desc': viddesc, 'status': 'new'})
		else:
			print("[%s]\tNo new videos found" % channel)
		# Update the lastvid and scants in db
		chan = Query()
		db.update({'lastvid': mostRecent, 'scants': int(time.time())}, (chan.type == 'channel') & (chan.id == channel))
	else:
		print("Channel %s is not in the database, use -a or --add to add it" % channel)

# Output the channel list
if args.command == "list":
	chans = Query()
	for chan in db.search(chans.type == 'channel'):
		scandate = "never"
		if chan['scants']:
			scandate = chan['scants']
			scandate = int(time.time()) - int(scandate)
			if scandate < 60:
				scandate = "just now"
			elif scandate < 3600:
				scandate = "%sm ago" % int(scandate/60)
			elif scandate < 86400:
				scandate = "%sh ago" % int(scandate/3600)
			else:
				scandate = "%sd ago" % int(scandate/86400)
		chanid = chan['id'] + (" " * (16-len(chan['id'])))
		print("%s\t[%s]" % (chanid,scandate))

# Add a new channel to the list
elif args.command=="add":
	chan = Query()
	if db.search((chan.type == 'channel') & (chan.id == args.chan)):
		print("Channel %s is already in the catalog" % args.chan)
	else :
		db.insert({'type': 'channel', 'id': args.chan, 'lastvid': None, 'scants': None})
		print("Channel %s added to the catalog" % args.chan)

# Remove a channel from the list
elif args.command=="remove":
	chan = Query()
	res = db.remove((chan.type == 'channel') & (chan.id == args.chan))
	if res:
		print("Channel %s was removed from the catalog" % args.chan)
	else :
		print("Channel %s was not in the catalog" % args.chan)

# Update channels in db
elif args.command=="update":
	# Init driver
	# TODO : replace with another driver (PhantomJS deprecated)
	driver = webdriver.PhantomJS()
	if args.chan:
		# Update a specific channel
		updateChannel(args.chan)
	else:
		# Update all channels
		chans = Query()
		for chan in db.search(chans.type == 'channel'):
			updateChannel(chan['id'])
	driver.quit()

# Print the queue content
elif args.command=="queue":
	videos = Query()
	counterror = 0
	for video in db.search(videos.type == 'video'):
		print("(%s)\t[%s] %s" % (video['status'],video['id'],video['desc']))
		if video['status'] == 'error':
			counterror += 1
	print("\nTOTAL : %s videos in queue" % db.count(videos.type == 'video'))
	if counterror > 0:
		print("%s previously failed, use 'flush' to remove it from the queue" % counterror)

# Process the queue content
elif args.command=="download":
	videos = Query()
	nbvid = db.count(videos.type == 'video')
	count = 0
	counterror = 0
	starttime = int(time.time())
	for video in db.search(videos.type == 'video'):
		count += 1
		sys.stdout.write("%s/%s\t Downloading\t[%s] %s" % (count,nbvid,video['id'],video['desc']))
		sys.stdout.flush()
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			res = ydl.download(['https://www.youtube.com/watch?v=%s' % video['id']])
			if res==0:
				# Successfull
				message = "%s/%s\t Done        \t[%s] %s" % (count,nbvid,video['id'],video['desc'])
				vid = Query()
				db.remove((vid.type == 'video') & (vid.id == video['id']))
			else:
				# Error
				counterror += 1
				message = "%s/%s\t Error       \t[%s] %s" % (count,nbvid,video['id'],video['desc'])
				vid = Query()
				db.update({'status': 'error'},(vid.type == 'video') & (vid.id == video['id']))
		sys.stdout.write("\b" * (len(message)+16))
		sys.stdout.write(message + "\n")
		sys.stdout.flush()
	endtime = int(time.time())
	print("\n%s/%s videos were successfully processed in %s" % (nbvid-counterror,nbvid,str(datetime.timedelta(seconds=endtime-starttime))))
	if counterror > 0:
		print("%s errors encountered, these videos were not removed from the queue" % counterror)

# Remove the video in error status from the queue
elif args.command=="flush":
	videos = Query()
	removed = db.search((videos.type == 'video') & (videos.status == 'error'))
	if removed:
		db.remove((videos.type == 'video') & (videos.status == 'error'))
		for video in removed:
			print("Removed\t[%s] %s" % (video['id'],video['desc']))
		print("\n%s videos were removed" % len(removed))
	else:
		print("No video to remove")

else:
	print("Command %s unknown." % args.command)

db.close()