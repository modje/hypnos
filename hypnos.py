import sys, os
import warnings
import argparse
import time
from selenium import webdriver
from tinydb import TinyDB, Query
# TODO : remove this, fix warnings about PhantomJS being deprecated instead
warnings.filterwarnings("ignore")

# Arguments parser
parser = argparse.ArgumentParser()
parser.add_argument("command", help="Command to execute", choices=["list","add","remove","update"])
parser.add_argument("-c", "--chan", help="Channel identifier (has no effect on 'list' command)")
args = parser.parse_args()
if args.command not in ['list','update'] and not args.chan:
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
				print("\t[%s]\t%s" % (video[0],video[1]))
				# Add the video to the download queue
				db.insert({'type': 'video', 'id': video[0], 'desc': video[1]})
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
		print("%s\t[%s]" % (chan['id'],scandate))

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

else:
	print("Command %s unknown." % args.command)

db.close()