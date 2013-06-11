import re
from google.appengine.ext import db
import urllib
from xml.dom.minidom import parseString
import logging
import event
from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.ext import db

class WikiParse:
	eventList = []
	
	def __init__(self,startYear,endYear):
		self.eventList = []
		self.init(startYear,endYear)


	def init(self,startYear,endYear):
		if startYear < endYear:
			for year in range(startYear,endYear+1):
				self.wiki_parse(year)
		elif startYear == endYear:
			print "hey"
			self.wiki_parse(startYear)

		else:
			return "Incorrect Startyear and endyear"

	def wiki_parse(self,year):
		#startTime = datetime.now()
		ignoreWords = ["=== Date unknown ===","=== Date unknown ===", "== Births ==", "== Deaths =="]
		# create logger
		standardUrl = "http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&titles=%s&format=xml" % year
		# add a file handler	
		
		"""req = urllib.urlopen(standardUrl)
		content = req.read()
		req.close()"""
		urlFetch = urlfetch.fetch(standardUrl)
		dom = parseString(urlFetch.content)
		#year = 
		xmlString = dom.getElementsByTagName("rev")[0].firstChild.nodeValue


		#Event year, initializing as 0
		year = 0
				
		dateString =""
		month,date = "",""
		fullDate = None		
		errors = ""
		isLowerLevelEvent = False
		count = 0
		lineList = xmlString.splitlines(True)
		
		for line in lineList:
			
			i,j = "",""
			if "Year dab|" in line:
				year = getYear(''.join(line.split("|")))
			if any(igWord in line for igWord in ignoreWords):
				break

			if "**" in line and isLowerLevelEvent:
				j = line

			#Is a top level date event
			if "*" in line and "**" not in line:
				#j = line
				if u"ndash;" in line[:40]:
					
					i,j = line.split(u"ndash;",1)
					month,date = getDate(i)
					fullDate = createDateTimeObj(year,getMonth(month),date)

				elif hasCorrectDateFormat(line):
					isLowerLevelEvent = True
					month,date = getDate(line)
					fullDate = createDateTimeObj(year,getMonth(month),date)

			e = None
			#if (year and date and month and j) and (not date or month or j  == ""):
			if (fullDate and j) and (not j  == ""):

				e = event.Event.create(fullDate,j)
				e.put()
				logging.error(e.key().id())
			if e:
				self.eventList.append(e)
				logging.error(len(self.eventList))

_digits = re.compile('\d')
monthDict = {"January":1,"February":2,"March":3,
	"April":4,"May":5,"June":6,
	"July":7,"August":8,"September":9,
	"October":10,"November":11,"December":12}
def contains_digits(d):
    return bool(_digits.search(d))

#check to see if the date string consist of two elements
def hasCorrectDateFormat(s):
	logging.error("Date: %s" % s)
	return len(re.findall(r'\w+', s)) == 2

def createDateTimeObj(year,month,date):
	if year and month and date:
		return datetime(int(year),int(month),int(date))
	else:
		return None

def isMonth(d):
	pass

def getYear(s):
	year = None
	r = re.search("\d{4}",s)
	year = r.group()
	return int(year)

def getMonth(s):
	try:
		return monthDict[s]
	except:
		return None

#Cleans up the datestring and returns a tuple
def getDate(d):
	month,date = "",""
	if contains_digits(d):
		s = cleanText(d)
		if hasCorrectDateFormat(s):
			month,date = s.strip().split(" ")
		return month,date
	else:
		return None,None

def cleanText(s):
	return_s = re.sub(r'[^\w]', ' ', s)
	if return_s.find("amp"):
		return_s = return_s.replace("amp","")
		return return_s
