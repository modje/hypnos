import sys, os
import argparse
from selenium import webdriver
from tinydb import TinyDB, Query

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

# Output the channel list
if args.command=="list":
	chans = Query()
	for chan in db.search(chans.type == 'channel'):
		scandate = "never"
		if chan['scants']:
			scandate = chan['scants']
			# TODO : get a pretty date string (like "4d ago")
		print("%s\t[%s]" % (chan['id'],scandate))

# Add a new channel to the list
elif args.command=="add":
	chan = Query()
	if db.search((chan.type == 'channel') & (chan.id == args.chan)):
		print("Channel %s is already in the catalog." % args.chan)
	else :
		db.insert({'type': 'channel', 'id': args.chan, 'lastvid': None, 'scants': None})
		print("Channel %s added to the catalog." % args.chan)

# Remove a channel from the list
elif args.command=="remove":
	chan = Query()
	res = db.remove((chan.type == 'channel') & (chan.id == args.chan))
	if res:
		print("Channel %s was removed from the catalog." % args.chan)
	else :
		print("Channel %s was not in the catalog." % args.chan)

# Update channels in db
#elif args.command=="update":


else:
	print("Command %s unknown." % args.command)

# Init driver
# TODO : replace with another driver (PhantomJS deprecated)
#driver = webdriver.PhantomJS()







# Parse channel content and update database
def refreshChannel(channel):
	# Get page content
	driver.get('https://www.youtube.com/user/%s/videos' % channel)
	# Get videos links and titles
	links = driver.find_elements_by_xpath('//body//h3[contains(@class,"yt-lockup-title")]/a')
	for link in links:
		vtitle = link.get_attribute("title")
		vhref = link.get_attribute("href")
		vhrefid = vhref.split('=')[1]
		print("[%s] Video found : %s" % (channel,vtitle))
		print("[%s] [%s] Video unknown" % (channel,vhrefid))





#refreshChannel('IndieCurrent')


db.close()