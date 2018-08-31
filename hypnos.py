#import urllib.request
#import json
#from lxml import html
#from urllib.request import urlopen

from selenium import webdriver
#from selenium.webdriver.common.by import By

#from lxml.etree import tostring


driver = webdriver.PhantomJS()
driver.get('https://www.youtube.com/user/sprocker7/videos')
#p_element = driver.find_element_by_id(id_='video-title')
#print(p_element.text)
links = driver.find_elements_by_xpath('//body//a')
for link in links:
	print(link.text)

#doc = html.parse(urlopen('https://www.youtube.com/user/sprocker7/videos'))


#persons = []
#for person in driver.find_elements_by_class_name('person'):
#    title = person.find_element_by_xpath('.//div[@class="title"]/a').text
#    company = person.find_element_by_xpath('.//div[@class="company"]/a').text

#    persons.append({'title': title, 'company': company})


#print(tostring(doc))


#doc = html.parse('https://www.youtube.com/user/sprocker7/videos')
#doc = html.parse('http://modjecart.free.fr/index.php')

#res = doc.xpath("//a[@id='video-title']")
#print(res)


#author = 'sprocker7'

#foundAll = False
#ind = 1
#videos = []
#while not foundAll:

#with urllib.request.urlopen('http://gdata.youtube.com/feeds/api/videos?start-index={0}&max-results=50&alt=json&orderby=published&author={1}'.format(ind,author)) as url:
#    inp = url.read()
#    try:
#resp = json.load(inp)
#inp.close()
#        returnedVideos = resp['feed']['entry']
#        for video in returnedVideos:
#            videos.append( video ) 

        #ind += 50
        #print len(videos)
        #if ( len( returnedVideos ) < 50 ):
        #    foundAll = True
#    except:
        #catch the case where the number of videos in the channel is a multiple of 50
#        print "error"
#        foundAll = True

#for video in videos:
#    print video['title'] # video title
#    print video['link'][0]['href'] #url
