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

class JSONProperty(db.TextProperty):
	def validate(self, value):
		return self._inflate(value)

	def get_value_for_datastore(self, model_instance):
		result = super(JsonProperty, self).get_value_for_datastore(model_instance)
		result = simplejson.dumps(result)
		return db.Text(result)
	
	def make_value_from_datastore(self, value):
		try:
			value = simplejson.loads(str(value))
		except:
			pass
		return super(JsonProperty, self).make_value_from_datastore(value)
def events_key(name = 'default'):
	return db.Key.from_path('events', name)

class Event(db.Model):
	text = db.TextProperty()
	date = db.DateTimeProperty()
	keywords = db.TextProperty()
	
	@classmethod
	def create(cls,date,event):
		cleanedText = cleanText(event)
		k = getKeyWords(cleanedText)
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
		cleanedDictString = cleanText2(event.keywords)
		#keywordDict = ast.literal_eval(cleanedDictString)
		keywordDict = ast.literal_eval(event.keywords)
		logging.error(keywordDict)
		return {"date":event.date.strftime("%Y-%m-%d"),
		"event":cleanText(event.text),
		"keywords":cleanDict(keywordDict)}
	
	@classmethod
	def updateDict(cls,d):
		pass

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

def age_set(key,val):
	save_time = datetime.datetime.utcnow()
	memcache.set(key,(val,save_time))

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
		logging.error(key)
		cleanList = []
		for keyword in keywords:
			logging.error(cleanText(keyword))
			cleanList.append(cleanText(keyword))
			#keyword = cleanText2(keyword)
			#logging.error(keyword)
		d[key] = cleanList
	return d

def cleanText(s):
	return_s = re.sub(r'(\[|])',"",s)
	return return_s

def cleanText2(s):
	#logging.error(s)
	return_s = re.sub("[[*]]","",s)
	return return_s
#Retrieves wikipedia entities from the event text
def getKeyWords(s):
	keywords = re.findall(r'\[\[([^]]*)\]\]',s)
	return keywords

	
def generateDict(l):
	if len(l) is not 0:
		d = {}
		for i in l:
			keyWordGen = kwg.KeyWordGenerator()
			#categories = keyWordGen.categories
			keyWordGen.main(i)
			categories = getattr(keyWordGen,"categories")
			#categories = kwg.KeyWordGenerator(i)
			if len(categories) > 0:
				d[i] = categories
			else:
				d[i] = []
			del keyWordGen
			del categories
		return d