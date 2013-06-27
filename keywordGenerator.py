#import event
import urllib2 as urllib
from xml.dom.minidom import parseString
import re
import logging
import utils

class KeyWordGenerator:
	def __init__(self):
		self.categories = []

	def main(self,rawTitle):
		logging.error(rawTitle)
		title = format_title(rawTitle)
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
					l = get_title(line)
					if l:
						self.main(format_title(l))
				#Is a correct article
				elif "Category" in line:
					#gets associated categories
					if get_categories(line):
						self.categories.append(get_categories(clean_text(line)))

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
def format_title(t):
	return t.replace(" ","_")

def get_title(s):
	try:
		keywords = re.search(r'\[\[([^]]*)\]\]',s).group()
		return keywords
	except:
		return None
def get_categories(s):
	#reString = re.findall(r'\[\[([^]]*)\]\]',s)[0]
	k1,k2 = "",""
	try:
		reString = re.search(r'\[\[([^]]*)\]\]',s).group()
		outString = reString.replace("Category:","")
		k1, k2 = utils.clean_keyword_text(outString)
	except:
		return None
	return k1

def clean_text(s):
	return_s = re.sub("[*]","",s)
	return return_s