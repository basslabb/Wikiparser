#import event
import urllib2 as urllib
from xml.dom.minidom import parseString
import re
import logging

class KeyWordGenerator:
	def __init__(self):
		self.categories = []

	def main(self,rawTitle):
		logging.error(rawTitle)
		title = formatTitle(rawTitle)
		standardUrl = "http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&titles=%s&format=xml" % title
		req = urllib.urlopen(standardUrl)
		content = req.read()
		req.close()
		dom = parseString(content)
		if dom.getElementsByTagName("rev"):
			xmlString = dom.getElementsByTagName("rev")[0].firstChild.nodeValue
			lineList = xmlString.splitlines(True)
			for line in lineList:
				#Isn't a correct article, hits a redirect
				if "REDIRECT" in line:
					#logging.error("Hit Redirect: %s" % line.encode("latin-1","ignore"))
					l = getTitle(line)
					if l:
						self.main(formatTitle(l))
				#Is a correct article
				elif "Category" in line:
					#gets associated categories
					if getCategories(cleanText(line)):
						self.categories.append(getCategories(cleanText(line)))

					else:
						logging.error(line)
				else:
					"Nothing"
		else:
			return None

	def returnCategories(self):
		logging.error("Len: %s" % len(self.categories))
		return self.categories

#in order to input to the API
def formatTitle(t):
	return t.replace(" ","_")

def getTitle(s):
	try:
		keywords = re.search(r'\[\[([^]]*)\]\]',s).group()
		return keywords
	except:
		return None
def getCategories(s):
	#reString = re.findall(r'\[\[([^]]*)\]\]',s)[0]
	try:
		reString = re.search(r'\[\[([^]]*)\]\]',s).group()
		outString = reString.replace("Category:","")
	except:
		return None
	return outString

def cleanText(s):
	return_s = re.sub("[*]","",s)
	return return_s