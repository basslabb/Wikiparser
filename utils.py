"""some utilities shared by several modules"""
import re

def clean_keyword_text(s):
	"""Takes a keyword string as input and returns a tuple consisting of the keyword(s) """
	return_s = re.sub(r'(\[|])',"",s)
	if "|" in return_s:
		return return_s.split("|")
	else:
		return return_s,None