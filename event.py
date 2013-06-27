import re
from datetime import datetime
from google.appengine.ext import db
#from django.utils import simplejson
import json
from datetime import datetime
import logging
import urllib
from xml.dom.minidom import parseString
import keywordGenerator as kwg
from google.appengine.api import memcache
import ast


def events_key(name = 'default'):
	return db.Key.from_path('events', name)

class Event(db.Model):
	text = db.TextProperty()
	date = db.DateTimeProperty()
	keywords = db.TextProperty()
	
	@classmethod
	def create(cls,date,event):
		cleanedText = cleanText(event)
		k = getKeyWords(event)
		d = generateDict(k)
		jsonString = json.dumps(d)
		return Event(text = cleanedText,
			date = date, 
			keywords = jsonString)

	@classmethod
	def by_id(cls, uid):
		return Event.get_by_id(uid, parent = events_key())

	@classmethod
	def as_Dict(cls,event):
		cleanedDictString = cleanText(event.keywords)
		#keywordDict = ast.literal_eval(cleanedDictString)
		keywordDict = ast.literal_eval(event.keywords)
		#logging.error(keywordDict)

		return {"date":event.date.strftime("%Y-%m-%d"),
		"event":cleanText(event.text),
		"keywords":cleanDict(keywordDict)}
	
	@classmethod
	def updateDict(cls,d):
		pass


##TODO Implement memcache. When everything works with the db
def getEvents(update=False):
	arts = memcache.get(key)
	events = "top"
	if events is None or update:
		logging.error("DB QUERY")
		events = db.GqlQuery("SELECT *"
							"FROM Event")
		events = list(events)
		memcache.set(key,events)
	return events
##TODO Implement memcache. When everything works with the db
def age_set(key,val):
	save_time = datetime.datetime.utcnow()
	memcache.set(key,(val,save_time))
##TODO Implement memcache. When everything works with the db
def age_get(key):
	r = memcache.get(key)
	if r:
		val,save_time = r
		age = (datetime.datetime.utcnow() - save_time).total_seconds()
	else:
		val,age = None,0


def cleanDict(d):
	out = {}
	for key,keywords in d.items():
		cleanList = []
		for keyword in keywords:
			logging.error(cleanText(keyword))
			cleanList.append(cleanText(keyword))
		d[key] = cleanList
	return d


def cleanText(s):
	
	"""takes event text as input, and returns a cleaned up version of the text, 
		without brackets and the correct format for the keyword"""
	#return_s = re.sub(r'(\[|])',"",s)
	r = re.findall(r"(\[\[([^]]*)\]\]|[\w']+)",s)
						 #r'\[\[([^]]*)\]\]'
	print r
	out_s = ""
	if r is not None and len(r) is not 0:
		for i in r:
			if re.search(r"\[\[([^]]*)\]\]",i[0]) is not None:
				#k1 is the article referenced, k2 is article text more suited for text
				k1,k2 = clean_keyword_text(i[0])
				if k2 is not None:
					out_s+=" " + k2
				else:
					out_s+=" " + k1
			else:
				out_s +=" " + i[0]
		out_s.strip()
		return out_s
	else:
		return ""


def clean_keyword_text(s):
	"""Takes a keyword string as input and returns a tuple consisting of the keyword(s) """
	return_s = re.sub(r'(\[|])',"",s)
	if "|" in return_s:
		return return_s.split("|")
	else:
		return return_s,None

# Retrieves wikipedia entities from the event text
def getKeyWords(s):
	keywords = re.findall(r'\[\[([^]]*)\]\]',s)
	return keywords

# Create the dictionary consisting of keywords (found in event text) 
# and the generated events
def generateDict(l):
	if len(l) is not 0:
		d = {}
		for i in l:
			keyWordGen = kwg.KeyWordGenerator()
			#categories = keyWordGen.categories
			keyWordGen.main(i)
			categories = getattr(keyWordGen,"categories")
			if len(categories) > 0:
				d[i] = categories
			else:
				d[i] = []
			
			#Seems to create huge dictionaries if you dont make sure these are deleted each run
			#I'm a talkin 1000+ type dictionaries, no bueno.
			del keyWordGen
			del categories
		return d